#!/usr/bin/env python3
"""Build styled caption card PNGs from an EDL + ElevenLabs Scribe transcript.

Agnostic version - font, sizes, positions, colors, and thresholds all come
from a config JSON (see config_default.json for the validated starting point:
PT Serif Bold, big centered hook holding the whole first sentence from frame 0,
one-line-max flowing body captions positioned lower in a safe zone).

Usage:
    python build_captions.py <edl.json> <transcript.json> <out_dir> [--config config.json]

The EDL format matches video-use's (github.com/browser-use/video-use):
    {"ranges": [{"source": "...", "start": S, "end": E, ...}, ...]}

The transcript format matches ElevenLabs Scribe's word-level JSON:
    {"words": [{"text": "...", "start": S, "end": E, "type": "word"|"spacing"|"audio_event"}]}

Design notes / hard-won lessons (2026-07-21/22, see reference_legenda_padrao_video.md):
  1. Never decide line-wrap by word count - always MEASURE the rendered text at
     the real font size. A bigger font breaks any fixed word-count heuristic.
  2. Every EDL segment boundary (a cut) MUST force a caption break, regardless
     of gap size or punctuation. If the cut already removed a pause, the
     output-timeline gap between the last word of one segment and the first
     word of the next is ~0 - so a gap-only or punctuation-only rule can glue
     a sentence's end onto the START of the next segment's text, displaying
     words seconds before they're actually spoken. This was a real bug found
     in production - fixed by tagging every word with its source segment index
     and never grouping (or merging-for-min-duration) across a segment change.
  3. Filter out non-speech transcript entries (type != "word", e.g. Scribe's
     "[riso]"/"[ruido]" audio_event tags) - they should never appear as text.
  4. Enforce a minimum on-screen duration per card (default 0.70s) - even a
     single short word needs a floor, or it flashes. Prefer merging it forward
     into the next card (if the combined text still fits) over just holding it,
     and never let either the merge or the hold-extension cross a segment
     boundary (same bug class as #2).
  5. Any display-text normalization (e.g. expanding a casual contraction) must
     run BEFORE any width measurement, or line-wrap decisions will be wrong.
"""
import argparse
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PUNCT_END = (",", ".", "?", "!", ":")


def load_config(config_path: str | None) -> dict:
    default_path = Path(__file__).parent / "config_default.json"
    cfg = json.loads(default_path.read_text())
    if config_path:
        override = json.loads(Path(config_path).read_text())
        _deep_update(cfg, override)
    return cfg


def _deep_update(base: dict, override: dict) -> None:
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_update(base[k], v)
        else:
            base[k] = v


def load_words(transcript_path: str) -> list[dict]:
    data = json.loads(Path(transcript_path).read_text())
    words = data.get("words", data) if isinstance(data, dict) else data
    if isinstance(words, dict):
        words = words.get("words", [])
    words = [w for w in words if w.get("type", "word") == "word"]  # drop spacing/audio_event
    words = [w for w in words if (w.get("text") or "").strip()]
    return words


def output_timeline(edl_path: str, transcript_path: str) -> tuple[list[dict], float]:
    edl = json.loads(Path(edl_path).read_text())
    words = load_words(transcript_path)
    out_words: list[dict] = []
    seg_offset = 0.0
    for seg_idx, r in enumerate(edl["ranges"]):
        s, e = float(r["start"]), float(r["end"])
        for w in words:
            wst = w.get("start")
            wen = w.get("end", wst)
            if wst is None or wen <= s or wst >= e:
                continue
            out_start = max(wst, s) - s + seg_offset
            out_end = min(wen, e) - s + seg_offset
            out_words.append({"text": w["text"].strip(), "start": out_start, "end": max(out_end, out_start), "seg": seg_idx})
        seg_offset += (e - s)
    return out_words, seg_offset


def apply_text_rules(words: list[dict], rules: list[dict]) -> None:
    """Apply optional display-only regex replacements (e.g. tá -> estar) before
    any width measurement happens. Each rule: {"pattern": "...", "replacement": "..."}."""
    compiled = [(re.compile(r["pattern"], re.IGNORECASE), r["replacement"]) for r in rules]
    for w in words:
        for pat, repl in compiled:
            w["text"] = pat.sub(repl, w["text"])


def wrap_fits(text: str, font, max_w: int, draw, stroke_width: int) -> list[str]:
    words = text.split()
    lines, cur = [], []
    for w in words:
        trial = " ".join(cur + [w])
        bbox = draw.textbbox((0, 0), trial, font=font, stroke_width=stroke_width)
        if bbox[2] - bbox[0] > max_w and cur:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    return lines


def fits_in(words_group, font, max_w, draw, stroke_width, max_lines) -> bool:
    text = " ".join(w["text"] for w in words_group)
    return len(wrap_fits(text, font, max_w, draw, stroke_width)) <= max_lines


def split_to_fit(words_group, font, max_w, draw, stroke_width, max_lines) -> list[list[dict]]:
    result, cur = [], []
    for w in words_group:
        trial = cur + [w]
        text = " ".join(x["text"] for x in trial)
        if len(wrap_fits(text, font, max_w, draw, stroke_width)) > max_lines and cur:
            result.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        result.append(cur)
    return result


def render_card(text, out_path, font, stroke_w, max_w, canvas_w, fill, outline) -> tuple[int, int, int]:
    img = Image.new("RGBA", (canvas_w, 900), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    lines = wrap_fits(text, font, max_w, draw, stroke_w)
    line_heights, total_h = [], 0
    for ln in lines:
        bbox = draw.textbbox((0, 0), ln, font=font, stroke_width=stroke_w)
        h = bbox[3] - bbox[1]
        line_heights.append(h)
        total_h += h
    font_size = font.size
    spacing = int(font_size * 0.28)
    total_h += spacing * (len(lines) - 1)
    y = (img.height - total_h) // 2
    for ln, h in zip(lines, line_heights):
        bbox = draw.textbbox((0, 0), ln, font=font, stroke_width=stroke_w)
        w = bbox[2] - bbox[0]
        x = (canvas_w - w) // 2 - bbox[0]
        draw.text((x, y - bbox[1]), ln, font=font, fill=tuple(fill), stroke_width=stroke_w, stroke_fill=tuple(outline))
        y += h + spacing
    bbox = img.getbbox()
    pad = 20
    if bbox:
        l, t, r, b = bbox
        img = img.crop((max(0, l - pad), max(0, t - pad), min(img.width, r + pad), min(img.height, b + pad)))
    img.save(out_path)
    return img.width, img.height, len(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edl")
    ap.add_argument("transcript")
    ap.add_argument("out_dir")
    ap.add_argument("--config", default=None, help="JSON overriding config_default.json (partial - deep merged)")
    ap.add_argument("--text-rules", default=None, help="JSON list of {pattern, replacement} display-only regex rules")
    args = ap.parse_args()

    cfg = load_config(args.config)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    words, total_dur = output_timeline(args.edl, args.transcript)
    if args.text_rules:
        apply_text_rules(words, json.loads(Path(args.text_rules).read_text()))

    hook_font = ImageFont.truetype(cfg["font_path"], cfg["hook"]["font_size"], index=cfg["font_index"])
    body_font = ImageFont.truetype(cfg["font_path"], cfg["body"]["font_size"], index=cfg["font_index"])
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))

    hook_words = []
    for w in words:
        hook_words.append(w)
        if w["text"].rstrip('"\'').endswith((":", ".", "?", "!")):
            break
    hook_end_idx = len(hook_words)
    hook_text = " ".join(w["text"] for w in hook_words)
    hook_out_start = 0.0
    natural_hook_end = hook_words[-1]["end"]
    hook_out_end = natural_hook_end + 0.35
    body_words = words[hook_end_idx:]
    if body_words:
        hook_out_end = min(hook_out_end, body_words[0]["start"] - 0.02)
        hook_out_end = max(hook_out_end, natural_hook_end + 0.05)

    cards = []
    hw, hh, _ = render_card(hook_text, out_dir / "card_hook.png", hook_font, cfg["hook"]["stroke_width"],
                             cfg["hook"]["max_width"], cfg["canvas_w"], cfg["fill_color"], cfg["outline_color"])
    cards.append({"file": "card_hook.png", "start": hook_out_start, "end": hook_out_end, "style": "hook",
                  "text": hook_text, "w": hw, "h": hh})

    body_max_lines = cfg["body"]["max_lines"]
    min_dur = cfg["min_display_duration"]
    gap_thresh = cfg["phrase_break_gap"]

    # pass 1: natural phrase groups - punctuation, silence gap, OR a segment
    # (cut) boundary, which must always break regardless of gap/punctuation.
    groups, cur = [], []
    for i, w in enumerate(body_words):
        cur.append(w)
        end_here = w["text"].rstrip('"\'').endswith(PUNCT_END)
        gap = (body_words[i + 1]["start"] - w["end"]) if i + 1 < len(body_words) else 999
        seg_changes = (i + 1 < len(body_words)) and (body_words[i + 1]["seg"] != w["seg"])
        if (end_here and len(cur) >= 3) or gap >= gap_thresh or seg_changes or i == len(body_words) - 1:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)

    # pass 2: hard-split any group exceeding max_lines at the real font size
    fitted = []
    for g in groups:
        fitted.extend(split_to_fit(g, body_font, cfg["body"]["max_width"], probe, cfg["body"]["stroke_width"], body_max_lines))
    groups = fitted

    # pass 3: glue short-lived groups forward (never across a segment boundary)
    final_groups, i = [], 0
    while i < len(groups):
        g = list(groups[i])
        dur = g[-1]["end"] - g[0]["start"]
        j = i
        while dur < min_dur and j + 1 < len(groups):
            if groups[j][-1]["seg"] != groups[j + 1][0]["seg"]:
                break
            candidate = g + groups[j + 1]
            if fits_in(candidate, body_font, cfg["body"]["max_width"], probe, cfg["body"]["stroke_width"], body_max_lines):
                g = candidate
                j += 1
                dur = g[-1]["end"] - g[0]["start"]
            else:
                break
        final_groups.append(g)
        i = j + 1
    groups = final_groups

    # pass 4: extend short cards' hold into the silence before the next card
    for gi, g in enumerate(groups):
        disp_start, disp_end = g[0]["start"], g[-1]["end"]
        next_start = groups[gi + 1][0]["start"] if gi + 1 < len(groups) else disp_end + min_dur + 1
        if disp_end - disp_start < min_dur:
            disp_end = min(disp_start + min_dur, next_start - 0.02)
        g[0]["_disp_start"] = disp_start
        g[-1]["_disp_end"] = max(disp_end, disp_start + 0.2)

    for gi, g in enumerate(groups):
        text = " ".join(w["text"] for w in g)
        start = g[0]["_disp_start"]
        end = g[-1]["_disp_end"] + (0.15 if gi == len(groups) - 1 else 0)
        fname = f"card_body_{gi:03d}.png"
        bw, bh, nlines = render_card(text, out_dir / fname, body_font, cfg["body"]["stroke_width"],
                                      cfg["body"]["max_width"], cfg["canvas_w"], cfg["fill_color"], cfg["outline_color"])
        if nlines > body_max_lines:
            print(f"  AVISO: card {gi} ainda com {nlines} linhas: {text!r}")
        cards.append({"file": fname, "start": start, "end": end, "style": "body", "text": text, "w": bw, "h": bh})

    # pass 5: universal overlap safety net across ALL cards (hook included)
    for k in range(len(cards) - 1):
        if cards[k]["end"] > cards[k + 1]["start"] - 0.01:
            cards[k]["end"] = max(cards[k]["start"] + 0.15, cards[k + 1]["start"] - 0.02)

    (out_dir / "cards.json").write_text(json.dumps({"cards": cards, "total_duration": total_dur, "config": cfg},
                                                     indent=2, ensure_ascii=False))
    print(f"gerados {len(cards)} cards (1 hook + {len(groups)} body), duracao total {total_dur:.2f}s")


if __name__ == "__main__":
    main()
