#!/usr/bin/env python3
"""
Caixa de entrada do /avaliar-ideia via Telegram.

Lê o que o usuário mandou pro bot (texto, link, áudio, vídeo, foto, documento) pela
user API (Telethon), baixa a mídia, transcreve áudio/vídeo localmente (mlx-whisper),
gera contact sheet de vídeo, agrupa mensagens próximas numa ideia só e guarda tudo
numa fila local. O bot não precisa de backend: as mensagens ficam no histórico do chat.

Uso:
  python3.12 inbox_telegram.py            # puxa novidades e mostra a fila pendente
  python3.12 inbox_telegram.py list       # só mostra a fila pendente (JSON)
  python3.12 inbox_telegram.py done ID..  # marca ideias como avaliadas

Config: ~/.config/avaliar-ideia-inbox/config (chave=valor)
  TELEGRAM_API_ID, TELEGRAM_API_HASH   # my.telegram.org
  BOT_USERNAME                         # ex: meu_bot
  TELETHON_SESSION                     # caminho da sessão, sem .session
  INBOX_DIR                            # onde guardar mídia e fila
  GROUP_GAP_SECONDS                    # opcional, padrão 120
"""
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CONFIG_DIR = Path.home() / ".config/avaliar-ideia-inbox"
CONFIG_PATH = CONFIG_DIR / "config"
STATE_PATH = CONFIG_DIR / "state.json"
URL_RE = re.compile(r"https?://\S+")


def load_config():
    cfg = {}
    for line in CONFIG_PATH.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip()
    cfg["INBOX_DIR"] = Path(cfg.get("INBOX_DIR", CONFIG_DIR / "inbox")).expanduser()
    cfg["GROUP_GAP_SECONDS"] = int(cfg.get("GROUP_GAP_SECONDS", 120))
    return cfg


def load_json(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def transcribe(media_path):
    out = media_path.with_suffix(".transcript.txt")
    if out.exists():
        return out
    try:
        from mlx_whisper import transcribe as mlx_transcribe
        text = mlx_transcribe(
            str(media_path),
            path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
        ).get("text", "").strip()
    except Exception as e:  # sem fala, formato estranho, modelo ausente
        print(f"  ⚠ transcrição falhou em {media_path.name}: {type(e).__name__}: {e}")
        return None
    out.write_text(text or "(sem fala detectada)", encoding="utf-8")
    return out


def contact_sheet(video_path):
    out = video_path.with_suffix(".sheet.jpg")
    if out.exists():
        return out
    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video_path)],
        capture_output=True, text=True,
    ).stdout.strip()
    try:
        fps = 12 / max(float(dur), 1)
    except ValueError:
        return None
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video_path),
         "-vf", f"fps={fps},scale=360:-2,tile=4x3", "-frames:v", "1", str(out)],
        capture_output=True,
    )
    return out if out.exists() else None


def message_urls(msg):
    urls = set(URL_RE.findall(msg.message or ""))
    for ent, _txt in msg.get_entities_text() if msg.entities else []:
        url = getattr(ent, "url", None)
        if url:
            urls.add(url)
    wp = getattr(getattr(msg, "media", None), "webpage", None)
    if wp is not None and getattr(wp, "url", None):
        urls.add(wp.url)
    return sorted(u.rstrip(").,") for u in urls)


def process_message(client, msg, media_dir):
    entry = {
        "msg_id": msg.id,
        "date": msg.date.astimezone().isoformat(timespec="seconds"),
        "text": msg.message or "",
        "urls": message_urls(msg),
        "files": [],
    }
    if msg.fwd_from:
        entry["forwarded"] = True
    if msg.file and not getattr(msg.media, "webpage", None):
        media_dir.mkdir(parents=True, exist_ok=True)
        path = Path(client.download_media(msg, file=str(media_dir / f"{msg.id}_")))
        f = {"path": str(path), "mime": msg.file.mime_type or ""}
        is_av = bool(msg.voice or msg.audio or msg.video or msg.video_note or f["mime"].startswith(("audio/", "video/")))
        if is_av:
            t = transcribe(path)
            if t:
                f["transcript"] = str(t)
        if msg.video or msg.video_note or f["mime"].startswith("video/"):
            s = contact_sheet(path)
            if s:
                f["contact_sheet"] = str(s)
        entry["files"].append(f)
    return entry


def group_messages(entries, msgs, gap):
    """Mensagens em sequência curta (link + comentário, álbum) viram uma ideia só."""
    groups, last_ts, last_gid = [], None, None
    for e, m in zip(entries, msgs):
        ts = m.date.timestamp()
        same_album = m.grouped_id is not None and m.grouped_id == last_gid
        if groups and (same_album or (last_ts is not None and ts - last_ts <= gap)):
            groups[-1]["messages"].append(e)
        else:
            groups.append({"id": m.id, "status": "pendente", "messages": [e]})
        last_ts, last_gid = ts, m.grouped_id
    return groups


def fetch(cfg):
    from telethon.sync import TelegramClient

    state = load_json(STATE_PATH, {"last_message_id": 0})
    fila_path = cfg["INBOX_DIR"] / "fila.json"
    fila = load_json(fila_path, [])
    with TelegramClient(cfg["TELETHON_SESSION"], int(cfg["TELEGRAM_API_ID"]), cfg["TELEGRAM_API_HASH"]) as client:
        msgs = list(client.iter_messages(cfg["BOT_USERNAME"], min_id=state["last_message_id"], reverse=True))
        mine = [m for m in msgs if m.out and not (m.message or "").startswith("/")]
        print(f"{len(mine)} mensagem(ns) nova(s) no chat com @{cfg['BOT_USERNAME']}.")
        entries = []
        for i, m in enumerate(mine, 1):
            print(f"  [{i}/{len(mine)}] msg {m.id}")
            entries.append(process_message(client, m, cfg["INBOX_DIR"] / "media"))
    new_groups = group_messages(entries, mine, cfg["GROUP_GAP_SECONDS"])
    fila.extend(new_groups)
    save_json(fila_path, fila)
    if msgs:
        state["last_message_id"] = max(m.id for m in msgs)
        save_json(STATE_PATH, state)
    print(f"{len(new_groups)} ideia(s) nova(s) na fila.")
    return fila


def show_pending(fila):
    pend = [g for g in fila if g["status"] == "pendente"]
    print(f"\n=== FILA PENDENTE: {len(pend)} ideia(s) ===")
    print(json.dumps(pend, ensure_ascii=False, indent=2))


def main():
    cfg = load_config()
    fila_path = cfg["INBOX_DIR"] / "fila.json"
    args = sys.argv[1:]
    if args[:1] == ["done"]:
        ids = {int(x) for x in args[1:]}
        fila = load_json(fila_path, [])
        for g in fila:
            if g["id"] in ids:
                g["status"] = "avaliada"
                g["avaliada_em"] = datetime.now().isoformat(timespec="seconds")
        save_json(fila_path, fila)
        print(f"Marcadas como avaliadas: {sorted(ids)}")
    elif args[:1] == ["list"]:
        show_pending(load_json(fila_path, []))
    else:
        show_pending(fetch(cfg))


if __name__ == "__main__":
    main()
