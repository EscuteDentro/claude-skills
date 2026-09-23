#!/usr/bin/env python3
"""Composite the caption cards (from build_captions.py) onto a base video via
ffmpeg overlay, timed with enable='between(t,start,end)'. Vertical position
comes from config_default.json (or an override), same as build_captions.py,
so the two stay in sync. Each layer (hook/body) picks one anchor:
  - "center": placed around a fixed y (`center_y`) regardless of card height.
  - "bottom": placed `bottom_margin` px above the canvas bottom edge - this
    keeps the true visual margin constant across cards of different heights
    (1 vs 2 lines, long vs short text), which a fixed center_y cannot do.

Usage:
    python composite_captions.py <cards_dir> <base_video> <out_video> [--config config.json]

<cards_dir> is the output directory build_captions.py wrote to (contains
cards.json and the card_*.png files).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image


def probe_resolution(video_path: str) -> tuple[int, int]:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", video_path],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    w, h = out.split(",")
    return int(w), int(h)


def check_canvas_matches_video(cfg: dict, video_path: str) -> None:
    """This script overlays PNGs at raw pixel coordinates computed from
    cfg["canvas_w"/"canvas_h"] - it has zero awareness of the base video's
    REAL resolution. If cards.json (from build_captions.py) was generated
    against a config already correctly scaled to this video, cfg["canvas_w"]
    here will match; if it doesn't, the overlay lands at the wrong scale AND
    position, silently (bug found in production 2026-09-09, see
    build_captions.py's scale_config_to_video for the full incident). Hard
    warning here, not silent - by this point build_captions.py already baked
    the (possibly wrong) canvas into every card's rendered PNG, so this script
    can't fix it, only flag it before burning ffmpeg time."""
    video_w, video_h = probe_resolution(video_path)
    if (video_w, video_h) != (cfg["canvas_w"], cfg["canvas_h"]):
        print(
            f"  AVISO: vídeo é {video_w}x{video_h}, --config passado aqui é "
            f"{cfg['canvas_w']}x{cfg['canvas_h']} - se cards.json foi gerado com um config "
            f"DIFERENTE (já escalado), isso é esperado e inofensivo; se for o MESMO config "
            f"usado nos dois passos, os cards vão sair no tamanho/posição errados."
        )


def validate_cards(cards: list[dict], cards_dir: Path) -> None:
    """Each card's overlay position is computed from its stored w/h, so a
    PNG that doesn't match its recorded dimensions renders at the wrong
    position - or, if the file itself holds the wrong content (e.g. a stale
    file left over from hand-editing cards.json after the original
    build_captions.py run), silently shows the wrong text in the right spot.
    Catch both by failing before any ffmpeg time is spent, not after."""
    errors = []
    for i, c in enumerate(cards):
        path = cards_dir / c["file"]
        if not path.exists():
            errors.append(f"  card {i} ({c['text']!r}): arquivo não existe: {c['file']}")
            continue
        with Image.open(path) as im:
            real_size = im.size
        expected = (c["w"], c["h"])
        if real_size != expected:
            errors.append(
                f"  card {i} ({c['text']!r}): {c['file']} tem {real_size}px, "
                f"cards.json espera {expected}px - regenere o card com render_card()"
            )
    if errors:
        sys.exit(
            "cards.json desalinhado com os PNGs em disco (comum após editar cards.json ou "
            "trocar um card_body_*.png à mão):\n" + "\n".join(errors)
        )


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


def layer_y(layer_cfg: dict, card_h: int, canvas_h: int) -> int:
    """Top-left y for this card given its layer's anchor mode."""
    anchor = layer_cfg.get("anchor", "center")
    if anchor == "bottom":
        return canvas_h - layer_cfg.get("bottom_margin", 0) - card_h
    return layer_cfg["center_y"] - card_h // 2


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cards_dir")
    ap.add_argument("base_video")
    ap.add_argument("out_video")
    ap.add_argument("--config", default=None)
    args = ap.parse_args()

    cards_dir = Path(args.cards_dir)
    data = json.loads((cards_dir / "cards.json").read_text())
    cards = data["cards"]

    # cards.json (written by build_captions.py) records the FULL config it
    # actually used - font sizes, anchors, center_y/bottom_margin, colors,
    # canvas, including any resolution auto-scale. That's the only source of
    # truth for where each card's PNG should land; a --config passed
    # independently to THIS script is a different object that can silently
    # diverge (bug found in production 2026-09-09: composite ran with no
    # --config, fell back to config_default.json's generic body position -
    # anchor "bottom", bottom_margin 0 - while the PNGs themselves had been
    # rendered by build_captions.py against the real brand config, anchor
    # "center" at ~66% down; every card composited flush against the bottom
    # edge, past any safe zone, across all 8 videos in that batch). Only
    # falls back to loading --config (or the bare default) for old cards.json
    # files that predate this baked field.
    baked_cfg = data.get("config")
    if baked_cfg:
        cfg = baked_cfg
        if args.config:
            print("  aviso: cards.json já tem o config completo (o que build_captions.py REALMENTE usou) - ignorando --config passado aqui, pra nunca divergir do que foi renderizado")
    else:
        cfg = load_config(args.config)
    canvas_w = cfg["canvas_w"]

    check_canvas_matches_video(cfg, args.base_video)

    validate_cards(cards, cards_dir)

    inputs = ["-i", args.base_video]
    filter_parts = []
    prev_label = "0:v"
    for i, c in enumerate(cards, start=1):
        inputs += ["-i", str(cards_dir / c["file"])]
        layer_cfg = cfg["hook"] if c["style"] == "hook" else cfg["body"]
        x = (canvas_w - c["w"]) // 2
        y = layer_y(layer_cfg, c["h"], cfg["canvas_h"])
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
