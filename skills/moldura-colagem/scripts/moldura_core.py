#!/usr/bin/env python3
"""Nucleo da moldura de papel rasgado: recorta uma imagem/video num
retangulo com borda fibrosa irregular + aro de papel, compositado sobre um
fundo. Agnostico de projeto -- toda identidade visual (fundo, cor do papel,
proporcoes) vem de config, nao de valor hardcoded.

Uso tipico: ver aplicar_frames.py (lote de PNGs) e aplicar_video.py (video
longo, via ffmpeg, muito mais rapido que lote de frames pra >10s de video).
"""
import json
import numpy as np
from PIL import Image, ImageFilter

DEFAULT_CONFIG = {
    "canvas_w": 1080,
    "canvas_h": 1920,
    "video_inset": 0.055,     # margem do retangulo do video, fracao do canvas
    "paper_inset": 0.028,     # margem do aro de papel (menor = aro mais largo)
    "video_band_px": 16,      # irregularidade da borda do video (px)
    "paper_band_px": 26,      # irregularidade da borda do papel (px)
    "paper_color": [238, 229, 208],
    "noise_seed": 7,
}


def load_config(path=None, overrides=None):
    cfg = dict(DEFAULT_CONFIG)
    if path:
        with open(path) as f:
            cfg.update(json.load(f))
    if overrides:
        cfg.update({k: v for k, v in overrides.items() if v is not None})
    return cfg


def smooth_noise(size, blur_passes=(40, 16, 6), seed=None):
    rng = np.random.default_rng(seed)
    n = rng.random(size[::-1]).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8))
    for b in blur_passes:
        im = im.filter(ImageFilter.GaussianBlur(b))
    arr = np.array(im).astype(np.float32)
    arr = (arr - arr.min()) / (arr.max() - arr.min())
    return arr


def torn_rect_mask(canvas_size, inset_frac, noise, band_px=22, seed_offset=0.0):
    w, h = canvas_size
    x0, y0 = int(w * inset_frac), int(h * inset_frac)
    x1, y1 = w - x0, h - y0
    rect = np.zeros((h, w), dtype=np.uint8)
    rect[y0:y1, x0:x1] = 255

    from scipy.ndimage import distance_transform_edt
    dist_in = distance_transform_edt(rect > 0)
    dist_out = distance_transform_edt(rect == 0)

    n = np.clip(noise + seed_offset, 0, 1)
    threshold = n * band_px

    out = np.zeros((h, w), dtype=bool)
    out |= (rect > 0) & ~((dist_in > 0) & (dist_in < threshold) & (n < 0.5))
    out |= (rect == 0) & (dist_out < threshold) & (n > 0.5)
    return (out.astype(np.uint8) * 255)


def build_frame_layers(cfg):
    """Retorna (video_mask, paper_mask), arrays uint8 HxW prontos pra usar
    como canal alfa (video_mask fica DENTRO de paper_mask -- aro visivel
    entre os dois)."""
    canvas_size = (cfg["canvas_w"], cfg["canvas_h"])
    noise = smooth_noise(canvas_size, seed=cfg["noise_seed"])
    video_mask = torn_rect_mask(canvas_size, cfg["video_inset"], noise, band_px=cfg["video_band_px"])
    paper_mask = torn_rect_mask(canvas_size, cfg["paper_inset"], noise, band_px=cfg["paper_band_px"], seed_offset=0.03)
    return video_mask, paper_mask


def apply_moldura(video_frame_rgb, bg_rgb, video_mask, paper_mask, paper_color):
    """video_frame_rgb e bg_rgb ja no tamanho do canvas (RGB)."""
    canvas = bg_rgb.convert("RGBA")

    paper_layer = Image.new("RGBA", canvas.size, tuple(paper_color) + (255,))
    paper_layer.putalpha(Image.fromarray(paper_mask).convert("L"))
    canvas.alpha_composite(paper_layer)

    video_layer = video_frame_rgb.convert("RGBA")
    video_layer.putalpha(Image.fromarray(video_mask).convert("L"))
    canvas.alpha_composite(video_layer)

    return canvas.convert("RGB")


def export_ffmpeg_layers(cfg, out_dir):
    """Exporta video_mask.png e paper_layer.png (RGBA, cor de papel ja
    aplicada) pra uso direto no filtro ffmpeg (aplicar_video.py). Retorna os
    2 caminhos."""
    import os
    os.makedirs(out_dir, exist_ok=True)
    video_mask, paper_mask = build_frame_layers(cfg)

    video_mask_path = f"{out_dir}/moldura_video_mask.png"
    Image.fromarray(video_mask).save(video_mask_path)

    paper_color = cfg["paper_color"]
    paper_rgba = np.zeros((cfg["canvas_h"], cfg["canvas_w"], 4), dtype=np.uint8)
    paper_rgba[:, :, 0] = paper_color[0]
    paper_rgba[:, :, 1] = paper_color[1]
    paper_rgba[:, :, 2] = paper_color[2]
    paper_rgba[:, :, 3] = paper_mask
    paper_layer_path = f"{out_dir}/moldura_paper_layer.png"
    Image.fromarray(paper_rgba, "RGBA").save(paper_layer_path)

    return video_mask_path, paper_layer_path
