#!/usr/bin/env python3
"""Aplica a moldura direto num arquivo de video, via filtro ffmpeg
(alphamerge + overlay). MUITO mais rapido que processar frame a frame em
PIL pra video longo (corpo inteiro de um episodio, 2-3min) -- nao gera
milhares de PNGs em disco, um unico pass de encode.

IMPORTANTE: fundo/mascara/papel sao inputs em loop infinito (-loop 1) --
sem -shortest no output, o encode NUNCA para sozinho nem quando o video
principal (input 0) acaba (bug real, 2026-09: rodou 47min pra uma fonte
de 60s antes de ser interrompido). -shortest resolve, ja aplicado abaixo.

Uso:
    python3 aplicar_video.py <video_entrada> <video_saida> \
        --config config.json [--ss INICIO] [--t DURACAO] [--fps 30]

Se --ss/--t nao forem passados, processa o video inteiro.
"""
import argparse
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
from moldura_core import load_config, export_ffmpeg_layers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video_in")
    ap.add_argument("video_out")
    ap.add_argument("--config", default=None)
    ap.add_argument("--background", default=None, help="Sobrescreve o fundo do config")
    ap.add_argument("--ss", type=float, default=None, help="Inicio do trecho (segundos)")
    ap.add_argument("--t", type=float, default=None, help="Duracao do trecho (segundos)")
    ap.add_argument("--fps", type=int, default=30)
    args = ap.parse_args()

    cfg = load_config(args.config)
    if args.background:
        cfg["background_image"] = args.background
    bg_path = cfg.get("background_image")
    if not bg_path:
        raise SystemExit("Falta o fundo: passe --background ou defina 'background_image' no config.")

    with tempfile.TemporaryDirectory() as tmp:
        video_mask_path, paper_layer_path = export_ffmpeg_layers(cfg, tmp)
        w, h = cfg["canvas_w"], cfg["canvas_h"]

        cmd = ["ffmpeg", "-y"]
        if args.ss is not None:
            cmd += ["-ss", str(args.ss)]
        cmd += ["-i", args.video_in]
        cmd += [
            "-loop", "1", "-framerate", str(args.fps), "-i", bg_path,
            "-loop", "1", "-framerate", str(args.fps), "-i", video_mask_path,
            "-loop", "1", "-framerate", str(args.fps), "-i", paper_layer_path,
            "-filter_complex",
            f"[0:v]scale={w}:{h},setsar=1,fps={args.fps}[vid];"
            "[2:v]format=gray[mask];"
            "[vid]format=rgba[vidrgba];"
            "[vidrgba][mask]alphamerge[vidmasked];"
            f"[1:v]scale={w}:{h},setsar=1,format=rgba[bg];"
            "[3:v]format=rgba[paper];"
            "[bg][paper]overlay=format=auto[step1];"
            "[step1][vidmasked]overlay=format=auto[final]",
            "-map", "[final]", "-map", "0:a",
            "-r", str(args.fps),
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "copy",
            "-shortest",
        ]
        if args.t is not None:
            cmd += ["-t", str(args.t)]
        cmd += [args.video_out]

        print("rodando:", " ".join(cmd))
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
