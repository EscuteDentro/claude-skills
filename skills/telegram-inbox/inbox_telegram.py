#!/usr/bin/env python3
"""
Caixa de entrada pelo Telegram: infraestrutura comum a qualquer skill que recebe
conteúdo do celular por um bot (avaliar ideias, criar notas, ...).

Lê o que o usuário mandou pro bot (texto, link, áudio, vídeo, foto, documento) pela
user API (Telethon), baixa a mídia, transcreve áudio/vídeo localmente (mlx-whisper),
gera contact sheet de vídeo, agrupa mensagens que formam um item só e guarda tudo numa
fila local. O bot não precisa de backend: as mensagens ficam no histórico do chat.

Uso:
  python3 inbox_telegram.py --bot NOME             # puxa novidades e mostra a fila pendente
  python3 inbox_telegram.py --bot NOME list        # só mostra a fila pendente (JSON)
  python3 inbox_telegram.py --bot NOME done ID ..  # marca itens como feitos
  --config DIR no lugar de --bot NOME              # pasta de config em outro lugar

Agrupamento (um item = uma unidade de trabalho):
  - resposta (reply) a uma mensagem entra no item dela, mesmo dias depois
  - álbum (várias fotos de uma vez) é um item
  - fora isso, cada mensagem é um item (comentário vai na mesma mensagem ou em resposta)

Config: ~/.config/telegram-inbox/NOME/config (chave=valor)
  TELEGRAM_API_ID, TELEGRAM_API_HASH   # my.telegram.org
  BOT_USERNAME                         # ex: meu_bot
  TELETHON_SESSION                     # caminho da sessão, sem .session
  INBOX_DIR                            # onde guardar mídia e fila
  WAIT_LOCKS                           # opcional: lockfiles (com PID) de outros programas
                                       # que usam a mesma sessão, separados por vírgula
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

URL_RE = re.compile(r"https?://\S+")
LOCK_TIMEOUT = 600


def parse_args(argv):
    args, config_dir = [], None
    it = iter(argv)
    for a in it:
        if a == "--bot":
            config_dir = Path.home() / ".config/telegram-inbox" / next(it)
        elif a == "--config":
            config_dir = Path(next(it)).expanduser()
        else:
            args.append(a)
    if config_dir is None:
        sys.exit("Informe --bot NOME ou --config DIR.")
    return config_dir, args


def load_config(config_dir):
    cfg = {}
    for line in (config_dir / "config").read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip()
    cfg["INBOX_DIR"] = Path(cfg.get("INBOX_DIR", config_dir / "inbox")).expanduser()
    cfg["WAIT_LOCKS"] = [Path(p).expanduser() for p in cfg.get("WAIT_LOCKS", "").split(",") if p.strip()]
    return cfg


def load_json(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


# ── Lock da sessão Telethon (vários bots e programas usam a mesma) ──────────────

def pid_alive(lock):
    try:
        os.kill(int(lock.read_text().strip()), 0)
        return True
    except (FileNotFoundError, ProcessLookupError, PermissionError, ValueError):
        return False


def acquire_session_lock(cfg):
    own = Path(cfg["TELETHON_SESSION"] + ".inbox.lock")
    deadline = time.time() + LOCK_TIMEOUT
    while True:
        busy = [l for l in [own, *cfg["WAIT_LOCKS"]] if l.exists() and pid_alive(l)]
        if not busy:
            break
        if time.time() > deadline:
            sys.exit(f"Sessão do Telegram ocupada há {LOCK_TIMEOUT}s por: {', '.join(map(str, busy))}")
        print(f"Aguardando sessão do Telegram liberar ({busy[0].name})...")
        time.sleep(5)
    own.write_text(str(os.getpid()))
    return own


# ── Mídia ───────────────────────────────────────────────────────────────────────

def transcription_alerts(text, duration):
    """Sinais de transcrição incompleta: fala lenta demais pro tamanho do áudio, ou loop no fim."""
    alerts = []
    words = text.split()
    if duration and duration > 20 and len(words) / duration * 60 < 25:
        alerts.append(f"poucas palavras pro áudio ({len(words)} em {duration:.0f}s): pode faltar trecho")
    tail = [w.strip(".,!?…").lower() for w in words[-12:]]
    if len(tail) >= 8 and len(set(tail[-8:])) <= 2:
        alerts.append("fim repetitivo (loop do Whisper): pode ter perdido o final")
    return alerts


def transcribe(media_path):
    """Transcreve com mlx-whisper. condition_on_previous_text=False evita o loop de repetição
    que o Whisper cria em áudio longo ou com pausas (e que esconde o final da fala)."""
    out = media_path.with_suffix(".transcript.txt")
    if out.exists():
        return out, []
    try:
        from mlx_whisper import transcribe as mlx_transcribe
        result = mlx_transcribe(
            str(media_path),
            path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
            condition_on_previous_text=False,
        )
    except Exception as e:  # sem fala, formato estranho, modelo ausente
        print(f"  ⚠ transcrição falhou em {media_path.name}: {type(e).__name__}: {e}")
        return None, [f"transcrição falhou: {type(e).__name__}"]
    text = result.get("text", "").strip()
    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(media_path)],
        capture_output=True, text=True,
    ).stdout.strip()
    alerts = transcription_alerts(text, float(dur)) if dur else []
    for al in alerts:
        print(f"  ⚠ {media_path.name}: {al}")
    out.write_text(text or "(sem fala detectada)", encoding="utf-8")
    return out, alerts


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
    if msg.reply_to_msg_id:
        entry["reply_to"] = msg.reply_to_msg_id
    if msg.fwd_from:
        entry["forwarded"] = True
    if msg.file and not getattr(msg.media, "webpage", None):
        media_dir.mkdir(parents=True, exist_ok=True)
        path = Path(client.download_media(msg, file=str(media_dir / f"{msg.id}_")))
        f = {"path": str(path), "mime": msg.file.mime_type or ""}
        is_av = bool(msg.voice or msg.audio or msg.video or msg.video_note or f["mime"].startswith(("audio/", "video/")))
        if is_av:
            t, alerts = transcribe(path)
            if t:
                f["transcript"] = str(t)
            if alerts:
                f["alertas"] = alerts
        if msg.video or msg.video_note or f["mime"].startswith("video/"):
            s = contact_sheet(path)
            if s:
                f["contact_sheet"] = str(s)
        entry["files"].append(f)
    return entry


# ── Fila ────────────────────────────────────────────────────────────────────────

def add_to_fila(fila, entries, msgs):
    owner = {e["msg_id"]: g for g in fila for e in g["messages"]}
    last, last_gid = None, None
    new = 0
    for e, m in zip(entries, msgs):
        target = owner.get(m.reply_to_msg_id) if m.reply_to_msg_id else None
        if target is None and last is not None and m.grouped_id is not None and m.grouped_id == last_gid:
            target = last
        if target is None:
            target = {"id": m.id, "status": "pendente", "messages": []}
            fila.append(target)
            new += 1
        elif target["status"] != "pendente":
            target["status"] = "pendente"  # resposta nova reabre item já feito
            target["reaberto"] = True
        target["messages"].append(e)
        owner[m.id] = target
        last, last_gid = target, m.grouped_id
    return new


def fetch(cfg, state_path, fila_path):
    from telethon.sync import TelegramClient

    lock = acquire_session_lock(cfg)
    try:
        state = load_json(state_path, {"last_message_id": 0})
        fila = load_json(fila_path, [])
        with TelegramClient(cfg["TELETHON_SESSION"], int(cfg["TELEGRAM_API_ID"]), cfg["TELEGRAM_API_HASH"]) as client:
            msgs = list(client.iter_messages(cfg["BOT_USERNAME"], min_id=state["last_message_id"], reverse=True))
            mine = [m for m in msgs if m.out and not (m.message or "").startswith("/")]
            print(f"{len(mine)} mensagem(ns) nova(s) no chat com @{cfg['BOT_USERNAME']}.")
            entries = []
            for i, m in enumerate(mine, 1):
                print(f"  [{i}/{len(mine)}] msg {m.id}")
                entries.append(process_message(client, m, cfg["INBOX_DIR"] / "media"))
    finally:
        lock.unlink(missing_ok=True)
    new = add_to_fila(fila, entries, mine)
    save_json(fila_path, fila)
    if msgs:
        state["last_message_id"] = max(m.id for m in msgs)
        save_json(state_path, state)
    print(f"{new} item(ns) novo(s) na fila.")
    return fila


def show_pending(fila):
    pend = [g for g in fila if g["status"] == "pendente"]
    print(f"\n=== FILA PENDENTE: {len(pend)} item(ns) ===")
    print(json.dumps(pend, ensure_ascii=False, indent=2))


def main():
    config_dir, args = parse_args(sys.argv[1:])
    cfg = load_config(config_dir)
    state_path = config_dir / "state.json"
    fila_path = cfg["INBOX_DIR"] / "fila.json"
    if args[:1] == ["done"]:
        ids = {int(x) for x in args[1:]}
        fila = load_json(fila_path, [])
        for g in fila:
            if g["id"] in ids:
                g["status"] = "feito"
                g["feito_em"] = datetime.now().isoformat(timespec="seconds")
        save_json(fila_path, fila)
        print(f"Marcados como feitos: {sorted(ids)}")
    elif args[:1] == ["list"]:
        show_pending(load_json(fila_path, []))
    else:
        show_pending(fetch(cfg, state_path, fila_path))


if __name__ == "__main__":
    main()
