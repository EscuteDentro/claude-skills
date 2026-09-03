"""Gera um elemento gráfico de overlay (CTA - balão de fala, badge, selo) como PNG com
transparência, a partir de texto (com suporte a emoji), pra overlay em vídeo via
`composite_overlay.py`. Agnóstico de marca E de forma - cor, fonte, borda, tamanho,
forma e rotação são todos parâmetro ou config, sem nenhum valor de identidade visual
real hardcoded neste arquivo (ver seção "Config" do SKILL.md - mesma convenção de
`build_captions.py`/`config_default.json` da skill `legenda-estilizada`: default
genérico aqui, valores reais da marca ficam num JSON PRIVADO fora deste repo).

Uso via CLI:
    python build_overlay.py "Texto aqui" --config meu_overlay.json --out overlay.png

Uso via import (mesma função, controle fino):
    from build_overlay import render_overlay
    render_overlay("Exemplo", font_size=58, max_w_target=460, out="overlay.png")
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from scipy.ndimage import distance_transform_edt

SS = 4  # fator de supersample (anti-aliasing) - todo desenho roda nessa escala, reduz no final
EMOJI_FONT_PATH = "/System/Library/Fonts/Apple Color Emoji.ttc"
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]", flags=re.UNICODE)


def dilate_uniform(mask: Image.Image, px: int) -> Image.Image:
    """Dilata a silhueta por distância euclidiana uniforme (nunca quadrada) - contorno
    fino e liso em qualquer curva/quina, sem o efeito "grosso na quina" de um MaxFilter
    (dilata com kernel quadrado, não circular).

    Retorna uma imagem MAIOR que a máscara original (+2*px em cada dimensão) - a
    silhueta encosta nas 4 bordas do array de entrada (forma ocupa a largura/altura
    inteira do canvas que a desenhou), então sem esse padding a dilatação não tem pixel
    de fundo pra crescer nos lados retos/topo e o distance_transform simplesmente não
    alcança além do array - a borda sai cortada rente à silhueta original exatamente
    nesses trechos. Bug real encontrado em produção (2026-08-19): a correção anterior
    (trocar MaxFilter por essa distância euclidiana) resolveu só a FORMA da dilatação,
    não essa falta de espaço no array - o corte continuava."""
    arr = np.array(mask) > 127
    padded = np.pad(arr, px, mode="constant", constant_values=False)
    dist = distance_transform_edt(~padded)
    out = (dist <= px).astype(np.uint8) * 255
    return Image.fromarray(out, mode="L")


def rounded_rect_tail_shape(w: int, h: int, radius: int | None = None, tail_h: int | None = None,
                             tail_x_frac: float = 0.30, tail_w: int | None = None) -> Image.Image:
    """Forma padrão: retângulo arredondado + rabicho triangular (balão de fala clássico,
    apontando pra baixo-esquerda por padrão). `radius`/`tail_h`/`tail_w` calculam um
    default proporcional a (w, h) quando None - sempre pode ser sobrescrito via
    `shape_kwargs` em `render_overlay`. Contrato de forma (pra registrar uma nova em
    `SHAPES`): `fn(w, h, **shape_kwargs) -> Image "L"` (máscara 0/255) - a imagem
    retornada pode ser MAIOR que (w, h) se a forma precisar de espaço extra (rabicho,
    decoração); o resto do pipeline deriva canvas e composição do `mask.size` real,
    nunca assume (w, h) puro."""
    radius = radius if radius is not None else min(h, w) // 4 + 20 * SS
    tail_h = tail_h if tail_h is not None else 64 * SS
    tail_w = tail_w if tail_w is not None else 76 * SS
    tail_x = int(w * tail_x_frac)

    m = Image.new("L", (w, h + tail_h), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    d.polygon([
        (tail_x, h - radius * 0.2),
        (tail_x + tail_w, h - radius * 0.05),
        (tail_x + tail_w * 0.15, h + tail_h),
    ], fill=255)
    d.ellipse([tail_x - 6 * SS, h - radius * 0.3 - 6 * SS, tail_x + 6 * SS, h - radius * 0.3 + 6 * SS], fill=255)
    return m


def rounded_rect_no_tail_shape(w: int, h: int, radius: int | None = None) -> Image.Image:
    """Forma alternativa: retângulo arredondado simples, sem rabicho - badge/etiqueta que
    não precisa apontar pra ninguém (ex: selo, contador, tag)."""
    radius = radius if radius is not None else min(h, w) // 4 + 20 * SS
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    return m


def ellipse_shape(w: int, h: int, pad_frac: float = 0.18) -> Image.Image:
    """Forma alternativa: elipse (oval) - a caixa de texto (w, h) fica inscrita com uma
    margem extra proporcional (`pad_frac`) pra a curva não cortar as letras."""
    pad = int(min(w, h) * pad_frac)
    m = Image.new("L", (w + pad * 2, h + pad * 2), 0)
    ImageDraw.Draw(m).ellipse([0, 0, m.width - 1, m.height - 1], fill=255)
    return m


# Registro de formas - assinatura obrigatória: fn(w, h, **shape_kwargs) -> Image "L" (máscara).
# Registrar uma forma nova aqui é o único passo pra deixá-la disponível via `shape="nome"`.
SHAPES = {
    "rounded_tail": rounded_rect_tail_shape,
    "rounded_no_tail": rounded_rect_no_tail_shape,
    "ellipse": ellipse_shape,
}

# Defaults genéricos (placeholder de propósito - NUNCA valores reais de marca aqui, mesma
# regra do config_default.json da skill legenda-estilizada). Todos viram parâmetro em
# `render_overlay()`.
DEFAULT_FILL = (90, 90, 90, 255)
DEFAULT_TEXT_COLOR = (255, 255, 255, 255)
DEFAULT_SHADOW_COLOR = (0, 0, 0, 120)
DEFAULT_FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def tokenize(text: str) -> list[tuple[str, str]]:
    tokens = []
    for word in text.split(" "):
        buf = ""
        for ch in word:
            if EMOJI_RE.match(ch):
                if buf:
                    tokens.append(("text", buf)); buf = ""
                tokens.append(("emoji", ch))
            else:
                buf += ch
        if buf:
            tokens.append(("text", buf))
    return tokens


def render_emoji_img(ch: str, px_size: int) -> Image.Image:
    ef = ImageFont.truetype(EMOJI_FONT_PATH, 160)
    etmp = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ImageDraw.Draw(etmp).text((10, 10), ch, font=ef, embedded_color=True)
    bbox = etmp.getbbox()
    crop = etmp.crop(bbox)
    scale = px_size / crop.height
    return crop.resize((max(1, int(crop.width * scale)), px_size), Image.LANCZOS)


def layout_lines(text, font, max_w, draw, cap_h):
    # "\n" no texto de entrada é quebra de linha FORÇADA (ex: CTA de 2 linhas exatas
    # tipo "Clica em SAIBA MAIS\ne faz uma prática gratuita") - cada segmento entre
    # quebras roda o wrap automático normal por conta própria, nunca funde com o
    # segmento vizinho mesmo que coubesse na mesma linha.
    space_w = draw.textbbox((0, 0), " ", font=font)[2]
    lines = []
    for segment in text.split("\n"):
        tokens = tokenize(segment)
        items = []
        for kind, val in tokens:
            if kind == "text":
                w = draw.textbbox((0, 0), val, font=font)[2]
                items.append(("text", val, w))
            else:
                img = render_emoji_img(val, cap_h)
                items.append(("emoji", img, img.width))
        cur, cur_w = [], 0
        for it in items:
            add_w = it[2] + (space_w if cur else 0)
            if cur_w + add_w > max_w and cur:
                lines.append(cur); cur, cur_w = [], 0
                add_w = it[2]
            cur.append(it); cur_w += add_w
        lines.append(cur)
    return lines, space_w


def render_overlay(
    text: str,
    font_size: int,
    max_w_target: int,
    *,
    shape: str = "rounded_tail",
    shape_kwargs: dict | None = None,
    fill_color=DEFAULT_FILL,
    text_color=DEFAULT_TEXT_COLOR,
    shadow_color=DEFAULT_SHADOW_COLOR,
    font_path: str = DEFAULT_FONT_PATH,
    font_index: int = 0,
    border_color=None,
    border_px: int = 10,
    rotation_deg: float = 0.0,
    out_scale: float = 1.0,
    flip_h: bool = False,
    flip_v: bool = False,
    text_stroke_px: int = 0,
    out: str = "overlay.png",
):
    """Gera o elemento de overlay como PNG. Todo eixo de customização é parâmetro:

      text          texto (emoji suportado, quebra automática em `max_w_target`)
      font_size     tamanho da fonte em px (antes do supersample)
      max_w_target  largura máxima de texto antes de quebrar linha (px)
      shape         chave em `SHAPES` - forma da silhueta ("rounded_tail" default)
      shape_kwargs  overrides pra forma escolhida (ex: {"tail_x_frac": 0.6})
      fill_color    cor de preenchimento, (r,g,b,a)
      text_color    cor do texto, (r,g,b,a)
      shadow_color  cor da sombra suave por trás do elemento, (r,g,b,a)
      font_path     caminho .ttf/.ttc
      font_index    índice do estilo dentro do arquivo (.ttc com múltiplos estilos)
      border_color  None = sem borda; (r,g,b,a) = com borda dessa cor
      border_px     espessura da borda em px (só importa se border_color setado)
      rotation_deg  rotação aplicada no final (graus). 0 = sem rotação.
      out_scale     fator de escala do PNG final (1.2 = 20% maior que o tamanho base)
      flip_h        espelha a FORMA (rabicho incluso) no eixo horizontal - texto não é afetado
      flip_v        espelha a FORMA (rabicho incluso) no eixo vertical - texto não é afetado
                    (ex: rabicho que nasce embaixo-esquerda por padrão vira em cima-direita
                    com flip_h+flip_v juntos, sem virar o texto de cabeça pra baixo - o
                    corpo do balão "anda" pro lado oposto de onde a máscara tinha espaço
                    extra, e o texto acompanha via `content_dy`, não via rotação de pixel)
      text_stroke_px  contorno do texto na MESMA cor do preenchimento (px, antes do supersample)
                    - engrossa o traço da fonte pra um efeito "leve bold" sem trocar de
                    arquivo de fonte. 0 = desativado (default, comportamento antigo idêntico).
      out           path de saída
    """
    shape_kwargs = shape_kwargs or {}
    if shape not in SHAPES:
        raise ValueError(f"forma desconhecida: {shape!r} - opções: {list(SHAPES)}")

    font = ImageFont.truetype(font_path, font_size * SS, index=font_index)
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    cap_bbox = probe.textbbox((0, 0), "Hg", font=font)
    cap_h = cap_bbox[3] - cap_bbox[1]
    line_h = font_size * SS * 1.42

    lines, space_w = layout_lines(text, font, max_w_target * SS, probe, int(cap_h))
    tw = max(sum(it[2] for it in ln) + space_w * (len(ln) - 1) for ln in lines)
    th = int(line_h * len(lines))

    pad_x, pad_y = 56 * SS, 60 * SS
    w, h = int(tw + pad_x * 2), th + pad_y * 2

    mask = SHAPES[shape](w, h, **shape_kwargs)
    if flip_h:
        mask = ImageOps.mirror(mask)
    if flip_v:
        mask = ImageOps.flip(mask)
    mw, mh = mask.size
    # deslocamento do conteúdo de texto dentro da máscara (formas sem rabicho ou com
    # padding próprio, ex. ellipse_shape, podem ser MAIORES que w/h - centraliza a
    # diferença nos dois eixos em vez de assumir que o texto começa em (0,0) da máscara).
    # Contrato de forma: corpo principal sempre em [0,h), espaço extra (rabicho) em
    # [h,mh) - com flip_v esse extra migra pro topo, então o texto desloca por (mh-h)
    # pra continuar caindo em cima do corpo, não do rabicho.
    content_dx, content_dy = (mw - w) // 2, (mh - h) if flip_v else 0

    border_extra = (border_px * SS if border_color else 0)
    shadow_offset = 8 * SS
    margin = shadow_offset + border_extra
    canvas_w = mw + margin * 2
    canvas_h = mh + margin * 2
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

    shadow_layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    shadow_solid = Image.new("RGBA", mask.size, shadow_color)
    shadow_layer.paste(shadow_solid, (margin, margin + 6 * SS), mask)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(9 * SS))
    canvas = Image.alpha_composite(canvas, shadow_layer)

    if border_color:
        border_px_ss = border_px * SS
        dilated = dilate_uniform(mask, border_px_ss)  # maior que mask.size em 2*border_px_ss
        border_layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        border_solid = Image.new("RGBA", dilated.size, border_color)
        border_layer.paste(border_solid, (margin - border_px_ss, margin - border_px_ss), dilated)
        canvas = Image.alpha_composite(canvas, border_layer)

    body = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    solid = Image.new("RGBA", mask.size, fill_color)
    body.paste(solid, (margin, margin), mask)
    canvas = Image.alpha_composite(canvas, body)

    text_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    td = ImageDraw.Draw(text_layer)
    y = margin + content_dy + pad_y
    for ln in lines:
        line_w = sum(it[2] for it in ln) + space_w * (len(ln) - 1)
        x = margin + content_dx + pad_x + (tw - line_w) / 2
        text_y = y + (line_h - cap_h) / 2 - cap_bbox[1]
        emoji_y = y + (line_h - cap_h) / 2
        for it in ln:
            if it[0] == "text":
                td.text((x, text_y), it[1], font=font, fill=text_color,
                         stroke_width=text_stroke_px * SS, stroke_fill=text_color)
                x += it[2] + space_w
            else:
                text_layer.paste(it[1], (int(x), int(emoji_y)), it[1])
                x += it[2] + space_w
        y += line_h
    canvas = Image.alpha_composite(canvas, text_layer)

    out_ss = SS / out_scale
    final = canvas.resize((max(1, int(canvas.width / out_ss)), max(1, int(canvas.height / out_ss))), Image.LANCZOS)
    if rotation_deg:
        final = final.rotate(rotation_deg, expand=True, resample=Image.BICUBIC)
    final.save(out)
    print(f"{out}: {final.size}, {len(lines)} linhas, shape={shape}")
    return final


def load_config(config_path: str | None) -> dict:
    default_path = Path(__file__).parent / "overlay_config_default.json"
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


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text", help="Texto do elemento (emoji suportado)")
    ap.add_argument("--config", default=None, help="JSON sobrescrevendo overlay_config_default.json (deep merge)")
    ap.add_argument("--out", default="overlay.png")
    ap.add_argument("--rotation-deg", type=float, default=0.0)
    ap.add_argument("--out-scale", type=float, default=1.0)
    ap.add_argument("--flip-h", action="store_true", help="Espelha a forma (rabicho) no eixo horizontal, texto fica normal")
    ap.add_argument("--flip-v", action="store_true", help="Espelha a forma (rabicho) no eixo vertical, texto fica normal")
    ap.add_argument("--text-stroke-px", type=int, default=0, help="Contorno do texto na mesma cor pra efeito 'leve bold' (px)")
    args = ap.parse_args()

    cfg = load_config(args.config)
    border_color = tuple(cfg["border_color"]) if cfg.get("border_color") else None
    render_overlay(
        args.text,
        font_size=cfg["font_size"],
        max_w_target=cfg["max_w_target"],
        shape=cfg.get("shape", "rounded_tail"),
        shape_kwargs=cfg.get("shape_kwargs"),
        fill_color=tuple(cfg["fill_color"]),
        text_color=tuple(cfg["text_color"]),
        shadow_color=tuple(cfg["shadow_color"]),
        font_path=cfg["font_path"],
        font_index=cfg.get("font_index", 0),
        border_color=border_color,
        border_px=cfg.get("border_px", 10),
        rotation_deg=args.rotation_deg,
        out_scale=args.out_scale,
        flip_h=args.flip_h,
        flip_v=args.flip_v,
        text_stroke_px=args.text_stroke_px,
        out=args.out,
    )


if __name__ == "__main__":
    main()
