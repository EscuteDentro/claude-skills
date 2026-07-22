#!/usr/bin/env python3
"""Composite the caption cards (from build_captions.py) onto a base video via
ffmpeg overlay, timed with enable='between(t,start,end)'. Positions (hook/body
vertical center) come from config_default.json (or an override), same as
build_captions.py, so the two stay in sync.

Usage:
    python composite_captions.py <cards_dir> <base_video> <out_video> [--config config.json]

<cards_dir> is the output directory build_captions.py wrote to (contains
cards.json and the card_*.png files).
"""
import argparse
import json
import subprocess
from pathlib import Path


def load_config(config_path: str | None) -> dict:
    default_path = Path(__file__).parent / "config_default.json"
    cfg = json.loads(default_path.read_text())
    if config_path:
        override = json.loads(Path(config_path).read_text())
        for k, v in override.items():
            if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                cfg[k].update(v)
            else:
                cfg[k] = v
    return cfg


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cards_dir")
    ap.add_argument("base_video")
    ap.add_argument("out_video")
    ap.add_argument("--config", default=None)
    args = ap.parse_args()

    cfg = load_config(args.config)
    cards_dir = Path(args.cards_dir)
    data = json.loads((cards_dir / "cards.json").read_text())
    cards = data["cards"]
    canvas_w = cfg["canvas_w"]

    inputs = ["-i", args.base_video]
    filter_parts = []
    prev_label = "0:v"
    for i, c in enumerate(cards, start=1):
        inputs += ["-i", str(cards_dir / c["file"])]
        cy = cfg["hook"]["center_y"] if c["style"] == "hook" else cfg["body"]["center_y"]
        x = (canvas_w - c["w"]) // 2
        y = cy - c["h"] // 2
        out_label = f"v{i}"
        filter_parts.append(
            f"[{prev_label}][{i}:v]overlay={x}:{y}:enable='between(t,{c['start']:.3f},{c['end']:.3f})'[{out_label}]"
        )
        prev_label = out_label

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", ";".join(filter_parts),
        "-map", f"[{prev_label}]", "-map", "0:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "copy",
        "-movflags", "+faststart",
        args.out_video,
    ]
    subprocess.run(cmd, check=True)
    print(f"composto -> {args.out_video}")


if __name__ == "__main__":
    main()
