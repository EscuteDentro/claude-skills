"""Sobrepõe um PNG de overlay (gerado por `build_overlay.py`) num vídeo a partir de um
timestamp, opcionalmente mixando um SFX de entrada no mesmo instante.

Uso via CLI:
    python composite_overlay.py <video_in.mp4> <overlay.png> <video_out.mp4> \
        --x 354 --y 10 --tstart 140.4 [--sfx som.wav]

Uso via import:
    from composite_overlay import composite_overlay
    composite_overlay(src, overlay_png, x, y, tstart, outfile, sfx_path=None)
"""
import argparse
import subprocess
import sys


def composite_overlay(src: str, overlay_png: str, x: int, y: int, tstart: float, outfile: str,
                       sfx_path: str | None = None) -> None:
    """Overlay do elemento a partir de `tstart` (segundos, permanece até o fim do vídeo) +
    mixa `sfx_path` no mesmo instante, se informado. Sem `sfx_path`, só o overlay visual."""
    delay_ms = int(round(tstart * 1000))
    if sfx_path:
        filter_complex = (
            f"[0:v][1:v]overlay={x}:{y}:enable='gte(t,{tstart})'[v];"
            f"[2:a]adelay={delay_ms}|{delay_ms}[sfx];"
            f"[0:a][sfx]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]"
        )
        inputs = ["-i", src, "-i", overlay_png, "-i", sfx_path]
        maps = ["-map", "[v]", "-map", "[a]"]
    else:
        filter_complex = f"[0:v][1:v]overlay={x}:{y}:enable='gte(t,{tstart})'[v]"
        inputs = ["-i", src, "-i", overlay_png]
        maps = ["-map", "[v]", "-map", "0:a"]

    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filter_complex,
        *maps,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "24",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        outfile,
    ]
    print("RUN:", " ".join(f'"{c}"' if " " in c else c for c in cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:])
        sys.exit(1)
    print("OK ->", outfile)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video_in")
    ap.add_argument("overlay_png")
    ap.add_argument("video_out")
    ap.add_argument("--x", type=int, required=True)
    ap.add_argument("--y", type=int, required=True)
    ap.add_argument("--tstart", type=float, required=True)
    ap.add_argument("--sfx", default=None, help="Path de um SFX pra mixar no instante do overlay (opcional)")
    args = ap.parse_args()
    composite_overlay(args.video_in, args.overlay_png, args.x, args.y, args.tstart, args.video_out, sfx_path=args.sfx)


if __name__ == "__main__":
    main()
