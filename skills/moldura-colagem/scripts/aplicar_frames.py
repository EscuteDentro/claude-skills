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
    bg = Image.open(bg_path).convert("RGB").resize(canvas, Image.LANCZOS)

    video_mask, paper_mask = build_frame_layers(cfg)

    os.makedirs(args.out_dir, exist_ok=True)
    for i in range(args.n_frames):
        src = f"{args.raw_frames_dir}/f{i + args.start_index:04d}.{args.ext}"
        vid = Image.open(src).convert("RGB").resize(canvas, Image.LANCZOS)
        frame = apply_moldura(vid, bg, video_mask, paper_mask, cfg["paper_color"])
        frame.save(f"{args.out_dir}/f{i:04d}.png")

    print(f"moldura aplicada em {args.n_frames} frames -> {args.out_dir}")


if __name__ == "__main__":
    main()
