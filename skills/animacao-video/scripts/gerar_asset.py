#!/usr/bin/env python3
"""
Gera 1 imagem via fal.ai (nano-banana), texto->imagem ou edicao com fotos de referencia.

Sem referencia (--ref) = texto->imagem, endpoint fal-ai/nano-banana.
Com 1+ --ref           = edicao/estilizacao com referencia, endpoint fal-ai/nano-banana/edit.

Requer FAL_KEY no ambiente ou num .env no diretorio atual (linha `FAL_KEY=...`).

Uso:
  # asset generico (fundo, prop, objeto) a partir so de descricao
  python3 gerar_asset.py --prompt "descricao completa em ingles" --out fundo.png

  # personagem a partir de fotos de referencia (mantem semelhanca/pose/roupa)
  python3 gerar_asset.py --prompt "descricao completa em ingles" --out personagem.png \
      --ref foto1.jpg --ref foto2.jpg --ref foto3.jpg

  # 9:16 (vertical, Reels/Shorts) e o default; mude se precisar
  python3 gerar_asset.py --prompt "..." --out saida.png --aspect-ratio 1:1
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

SYNC_TXT2IMG = "https://fal.run/fal-ai/nano-banana"
SYNC_EDIT = "https://fal.run/fal-ai/nano-banana/edit"


def load_env(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, _, v = s.partition("=")
        k, v = k.strip(), v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        if k and k not in os.environ:
            os.environ[k] = v


def to_data_uri(path_str: str) -> str:
    p = Path(path_str)
    if not p.exists():
        sys.exit(f"ERRO: referencia nao encontrada: {path_str}")
    mime = mimetypes.guess_type(str(p))[0] or "image/png"
    data = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def save_result_image(result: dict, out_path: Path) -> bool:
    imgs = result.get("images") or []
    if not imgs:
        return False
    url = imgs[0]["url"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if url.startswith("data:"):
        _, _, b64 = url.partition(",")
        out_path.write_bytes(base64.b64decode(b64))
    else:
        with urllib.request.urlopen(url, timeout=60) as r:
            out_path.write_bytes(r.read())
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt", required=True, help="Prompt completo em ingles")
    ap.add_argument("--out", required=True, help="Caminho do PNG de saida")
    ap.add_argument("--ref", action="append", default=[], help="Foto de referencia (repetir a flag para varias, ate 14)")
    ap.add_argument("--aspect-ratio", default="9:16")
    args = ap.parse_args()

    load_env(Path.cwd() / ".env")
    fal_key = os.environ.get("FAL_KEY", "").strip()
    if not fal_key:
        sys.exit("ERRO: FAL_KEY nao configurada (variavel de ambiente ou .env no diretorio atual)")

    edit_mode = bool(args.ref)
    url = SYNC_EDIT if edit_mode else SYNC_TXT2IMG

    payload = {
        "prompt": args.prompt,
        "num_images": 1,
        "aspect_ratio": args.aspect_ratio,
        "output_format": "png",
    }
    if edit_mode:
        payload["image_urls"] = [to_data_uri(r) for r in args.ref]

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Authorization": f"Key {fal_key}", "Content-Type": "application/json"},
        method="POST",
    )

    print(f"Chamando {'nano-banana/edit' if edit_mode else 'nano-banana'} (chamada unica, sem retry)...")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            result = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"ERRO HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:500]}")

    out_path = Path(args.out)
    if not save_result_image(result, out_path):
        sys.exit(f"ERRO: sem imagem na resposta: {json.dumps(result)[:500]}")
    print(f"Salvo: {out_path}")


if __name__ == "__main__":
    main()
