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


def _has_audio_stream(path: str) -> bool:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=index", "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    return bool(out.stdout.strip())


def _video_duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    )
    return float(out.stdout.strip())


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

    # video_zoom/video_pan_x (opcionais, default 1.0/0.0 = comportamento antigo
    # inalterado): pedido real (2026-09-10) de recentralizar a pessoa dentro do
    # retangulo do video sem editar a fonte. zoom>1 escala o video ALEM do
    # minimo que cobre o canvas, sobrando espaco horizontal pra escolher QUAL
    # fatia manter; pan_x em [-1,1] escolhe onde dentro desse espaco (-1 =
    # mantem só a fatia mais à ESQUERDA da fonte, cortando o lado direito;
    # +1 = mantem só a mais à DIREITA, cortando o esquerdo; 0 = centralizado,
    # igual antes). Aplicado só no [0:v] principal, nunca no fundo.
    zoom = cfg.get("video_zoom", 1.0)
    pan_x = cfg.get("video_pan_x", 0.0)

    with tempfile.TemporaryDirectory() as tmp:
        video_mask_path, paper_layer_path = export_ffmpeg_layers(cfg, tmp)
        w, h = cfg["canvas_w"], cfg["canvas_h"]
        zw, zh = round(w * zoom), round(h * zoom)
        slack = zw - w
        crop_x = f"{round(slack / 2 * (1 + pan_x))}"

        cmd = ["ffmpeg", "-y"]
        if args.ss is not None:
            cmd += ["-ss", str(args.ss)]
        cmd += ["-i", args.video_in]
        cmd += [
            "-loop", "1", "-framerate", str(args.fps), "-i", bg_path,
            "-loop", "1", "-framerate", str(args.fps), "-i", video_mask_path,
            "-loop", "1", "-framerate", str(args.fps), "-i", paper_layer_path,
            "-filter_complex",
            f"[0:v]scale={zw}:{zh}:force_original_aspect_ratio=increase,crop={w}:{h}:{crop_x}:(ih-{h})/2,setsar=1,fps={args.fps}[vid];"
            "[2:v]format=gray[mask];"
            "[vid]format=rgba[vidrgba];"
            "[vidrgba][mask]alphamerge[vidmasked];"
            f"[1:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,format=rgba[bg];"
            "[3:v]format=rgba[paper];"
            "[bg][paper]overlay=format=auto[step1];"
            "[step1][vidmasked]overlay=format=auto[final]",
            "-map", "[final]",
        ]
        # Bug real corrigido 2026-09-13: `-map 0:a` incondicional quebrava
        # ("Stream map '' matches no streams") toda vez que o vídeo de entrada
        # não tinha trilha de áudio (b-roll silencioso, moldura vazia sem som).
        has_audio = _has_audio_stream(args.video_in)
        if has_audio:
            cmd += ["-map", "0:a", "-c:a", "copy"]
        cmd += [
            "-r", str(args.fps),
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-shortest",
        ]
        effective_t = args.t
        if effective_t is None and not has_audio:
            # 2º bug real, achado testando o fix acima: `-shortest` só tinha
            # efeito antes porque `0:a` (fonte finita) sempre estava mapeado
            # junto com [final] (que sai de 2 loops infinitos de fundo/papel
            # — sem áudio, [final] nunca chega a um EOF natural sozinho).
            # Sem essa trilha, `-shortest` não tinha mais nada finito pra
            # comparar e o encode nunca parava sozinho (mesma classe do bug
            # de 47min já documentado no topo do arquivo, reproduzido de
            # verdade aqui: travou rodando até ser morto manualmente).
            # Fix: sem áudio, sempre fixar -t explícito pela duração real da
            # fonte de vídeo (contando o --ss, se houver).
            source_duration = _video_duration(args.video_in)
            effective_t = max(0.0, source_duration - (args.ss or 0.0))
        if effective_t is not None:
            cmd += ["-t", str(effective_t)]
        cmd += [args.video_out]

        print("rodando:", " ".join(cmd))
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
