#!/usr/bin/env python3
"""Aplica a moldura num lote de frames PNG/JPG numerados (f0000.ext, f0001.ext...).
Modo rapido: a mascara e calculada 1 vez so e reaproveitada em todos os frames.
Use pra clipes curtos (ate ~15-20s) onde ja existem os frames extraidos
individualmente (ex: composicoes que ja passaram por outro processamento
frame a frame, como um sticker colado em cima). Pra video longo continuo,
use aplicar_video.py (ffmpeg puro, muito mais rapido e sem gerar milhares
de PNGs em disco).

Uso:
    python3 aplicar_frames.py <raw_frames_dir> <out_dir> <n_frames> \
        --config config.json [--start-index N] [--ext jpg]
"""
import argparse
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from moldura_core import load_config, build_frame_layers, apply_moldura


def cover_resize(im: Image.Image, canvas: tuple[int, int]) -> Image.Image:
    """Redimensiona preservando proporção (cover, nunca stretch) - crop central
    do excesso. Sem isso, `.resize(canvas)` direto ESTICA a imagem sempre que a
    proporção de origem não bate com a do canvas (bug real, 2026-09-03: passou
    despercebido porque os 2 primeiros fundos usados coincidiam com 9:16)."""
    cw, ch = canvas
    iw, ih = im.size
    src_ratio, dst_ratio = iw / ih, cw / ch
    if src_ratio > dst_ratio:
        new_w = int(ih * dst_ratio)
        x0 = (iw - new_w) // 2
        im = im.crop((x0, 0, x0 + new_w, ih))
    else:
        new_h = int(iw / dst_ratio)
        y0 = (ih - new_h) // 2
        im = im.crop((0, y0, iw, y0 + new_h))
    return im.resize(canvas, Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw_frames_dir")
    ap.add_argument("out_dir")
    ap.add_argument("n_frames", type=int)
    ap.add_argument("--config", default=None, help="JSON de config (ver config_default.json)")
    ap.add_argument("--background", default=None, help="Sobrescreve o fundo do config")
    ap.add_argument("--start-index", type=int, default=0)
    ap.add_argument("--ext", default="jpg", help="Extensao dos frames de entrada (padrao jpg)")
    args = ap.parse_args()

    cfg = load_config(args.config)
    canvas = (cfg["canvas_w"], cfg["canvas_h"])

    bg_path = args.background or cfg.get("background_image")
    if not bg_path:
        raise SystemExit("Falta o fundo: passe --background ou defina 'background_image' no config.")
    bg = cover_resize(Image.open(bg_path).convert("RGB"), canvas)

    video_mask, paper_mask = build_frame_layers(cfg)

    os.makedirs(args.out_dir, exist_ok=True)
    for i in range(args.n_frames):
        src = f"{args.raw_frames_dir}/f{i + args.start_index:04d}.{args.ext}"
        vid = cover_resize(Image.open(src).convert("RGB"), canvas)
        frame = apply_moldura(vid, bg, video_mask, paper_mask, cfg["paper_color"])
        frame.save(f"{args.out_dir}/f{i:04d}.png")

    print(f"moldura aplicada em {args.n_frames} frames -> {args.out_dir}")


if __name__ == "__main__":
    main()
