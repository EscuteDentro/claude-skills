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
  6. Group by semantic unit, not just by width fit (2026-07-31, real bug found
     in production). Two concrete cases:
     a. A quoted span (reported speech) must never share a card with text
        before or after it - the closing quote mark was gluing onto the START
        of the NEXT sentence ("quero?". É tanto ruído"), reading like new
        content already started while the old quote was still resolving. Fix:
        force a card break before any word that OPENS a quote and right after
        any word that CLOSES one, regardless of width budget. The single word
        immediately introducing the quote also gets isolated into its own
        card - a beat of anticipation before the reveal reads better than
        gluing the lead-in to the preceding clause.
     b. A comma-separated enumeration (list) must chunk with a CONSTANT number
        of items per card - never 1 item, then 2, then 1 again. An
        inconsistent stride visually implies the underlying information
        changed shape, when it's really the same kind of unit repeating. Fix:
        detect runs of 3+ comma-terminated items and force one-item-per-card
        if the whole run doesn't fit together in one card - never a partial
        greedy-fill mix.
  7. Sentence-ending punctuation (.?!:) always forces a card break, even for a
     1-2 word sentence (2026-08-11, real bug found in production: "Meditação."
     - a standalone one-word sentence - glued onto the START of the next
     sentence "A meditação te coloca...", producing a card that read
     "Meditação. A" with pass-2's width-based split cutting the merged group
     at an arbitrary word with no relation to the sentence boundary. The old
     rule required len(cur) >= 3 before respecting end-of-sentence punctuation,
     meant to avoid over-fragmenting short interjections - but pass 3 already
     glues short-lived (<min_display_duration) groups forward when safe, so
     that job doesn't belong in pass 1. Never gate sentence-boundary
     recognition on how many words happen to be in the group so far.
  8. Pass 3 (glue short-lived groups forward) must never glue across a
     sentence-ending punctuation boundary, even when the resulting group is
     shorter than min_display_duration (2026-08-13, real bug: pass 1 correctly
     split "né?" and "sabedoria." into their own groups per PUNCT_END, but
     pass 3 re-merged them into the NEXT sentence purely because their own
     duration was under 0.70s - "né? Isso" and "sabedoria. Calma" rendered as
     single cards straddling two unrelated sentences). Pass 4 already extends
     a short card's on-screen hold using the following silence, so pass 3
     doesn't need to steal words from the next sentence to solve visibility.
     Fix: pass 3 now breaks on the same PUNCT_END check pass 1 uses, same as
     it already does for a segment-boundary change.
  9. "?" and "!" stay at a card's real end, "." doesn't (2026-08-13, two
     rounds of live feedback same day). First pass stripped ?/! too, on the
     theory that any end-mark breaks flow. Refined: the actual complaint was
     ?/! landing MID-card ("né? Isso") - item 8 already fixes that by forcing
     the break there. Once ?/! can only ever land on a card's real last word,
     showing them is correct (they carry the line's emotional/interrogative
     beat on purpose); "." stays stripped everywhere - a literal full stop
     reads like a caption bug regardless of position, the gap to the next
     card already signals the pause.
  10. Card breaks follow SEMANTIC coherence, not just width (2026-08-15, real feedback:
      "ver as coisas com mais clareza, clica" landed in one card, gluing the end of one clause
      to the start of an unrelated CTA sentence). `_greedy_split` packed words to the width
      limit blind to punctuation. Fix: when a group overflows, look back for the most recent
      comma already inside what fits and break there instead of at the raw width cutoff - the
      comma itself still gets stripped from display (TRAILING_GRAMMATICAL_PUNCT), only its
      position as a break point matters. Falls back to blind width-packing when no comma exists
      in the overflowing span.
  11. Fixed cohesive phrases (`COHESIVE_PHRASES`, e.g. "clica aqui") always render as their own
      isolated card, never split across cards or glued to neighboring text (same feedback). In
      real speech these carry a pause on both sides; after pause-cutting shrinks that pause in
      the final video/audio, pass 1's gap-based grouping alone no longer sees it - so isolation
      is forced structurally in pass 1, independent of the surviving gap duration.
  12. `COHESIVE_PHRASES` is NOT just about call-to-action wording (2026-08-15, generalized from
      `CTA_PHRASES`). The real principle: any brand-anchor expression whose persuasive/visual
      impact depends on being read as one unit - "sentir na pele" is the case that motivated the
      rename, same mechanism as "clica aqui" but nothing to do with CTAs. Any future phrase that
      fits this description (reads with more weight together than split) is a candidate entry,
      not just literal action phrases.
  13. A self-interrupted false start ("ti--" before the real word "tenho") is a SEPARATE ASR word
      token from the word that completes it, unlike the hyphen-glued stutter item in
      `normalize_stutter` ("auto-automatismo", one token). `normalize_stutter` operates on
      already-formed display text and can only edit a string, not delete a whole neighboring
      token - so it can't fix this case. Real bug found in production (2026-08-18, "aprendeu
      tudo isso" video): "ti--" survived to a card by itself right before "tenho dez anos". Fix:
      drop any word token that is ENTIRELY a fragment plus 1-2 trailing dashes
      (`_FALSE_START_PATTERN`) at `load_words()` time, before grouping ever sees it - the same
      class of noise as the audio_event tags item 3 already filters, just ASR-specific instead of
      Scribe-tag-specific. Fragment length cap is 1-12 chars (2026-08-18, same session, second
      real case: "ansie--" in the "ansiedade e comer" video is 5 chars - the original 1-4 cap
      missed it, same lesson as item 12's `_STUTTER_PATTERN` cap. A false start can ALSO have no
      nearby completion at all (the speaker abandons the word and starts a different sentence,
      not just a stutter-then-immediate-retry) - `_FALSE_START_PATTERN` doesn't care either way,
      it just drops any standalone fragment+dash token unconditionally.
"""
import argparse
import json
import math
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont

# Vírgula NÃO força quebra de card sozinha (2026-07-31) - só pontuação forte
# (frase completa) ou pausa/corte real quebram o agrupamento na passada 1.
# Antes a vírgula forçava quebra a cada item de uma enumeração assim que
# len(cur)>=3, o que destruía qualquer chance de agrupamento consistente de
# lista antes mesmo do split_to_fit (passada 2) rodar - a vírgula agora só
# conta como boundary "fraco", resolvido por largura real + regra de lista.
PUNCT_END = (".", "?", "!", ":")

# "." "," ":" ";" nunca fecham um card visualmente - a quebra pro card seguinte
# já comunica a pausa. "?" e "!" ficam, mas só porque item 8 (acima) garante
# que uma palavra terminada em pontuação forte SEMPRE fecha o card ali - ou
# seja, "?"/"!" só aparecem no fim real de um card, nunca colados no meio
# puxando a frase seguinte junto ("né? Isso"). Sem essa garantia, "?"/"!" no
# meio do card lê como bug; no fim real, carrega a intenção emocional/
# interrogativa de propósito (decidido 2026-08-13, revisado no mesmo dia).
TRAILING_GRAMMATICAL_PUNCT = (".", ",", ":", ";")


def strip_trailing_grammatical_punct(text: str) -> str:
    while text and text[-1] in TRAILING_GRAMMATICAL_PUNCT:
        text = text[:-1]
    return text


_CE_PATTERN = re.compile(r"\bc[êe]\b", re.IGNORECASE)


def normalize_ce_para_voce(text: str) -> str:
    """"Cê" (contração oral de "você") nunca aparece em legenda - sempre expandir
    pra "você"/"Você", preservando a capitalização do original."""
    def repl(m: re.Match) -> str:
        return "Você" if m.group(0)[0].isupper() else "você"
    return _CE_PATTERN.sub(repl, text)


_STUTTER_PATTERN = re.compile(
    r"\b(\w{1,12})-(\1\w*)\b", re.IGNORECASE
)


def normalize_stutter(text: str) -> str:
    """Gaguejo/falso início transcrito literalmente pelo ASR ("auto-automatismo",
    "cir-circunstância", "mes-mesmo", "complemen-complementar") nunca aparece em
    legenda - a legenda mostra o que foi dito, não como foi hesitado. Detecta um
    fragmento hifenizado imediatamente antes de uma palavra que começa com esse
    mesmo fragmento, e mantém só a palavra completa (2026-08-14, achado real em
    produção: "ásanas" nao é isso, é sanscrito - ver normalize_sanskrit_terms - mas
    "auto-automatismo" e "cir-circunstância" sao gaguejo genuíno). Limite do
    fragmento é 1-12 letras (2026-08-18, achado real: "complemen-complementar" tem
    fragmento de 9 letras, o limite antigo de 4 não cobria - repetição literal do
    prefixo é o que garante que a regra não bata em palavra composta legítima tipo
    "guarda-chuva", não o tamanho do fragmento)."""
    def repl(m: re.Match) -> str:
        return m.group(2)
    return _STUTTER_PATTERN.sub(repl, text)


# Termos de origem sânscrita/estrangeira que o ASR (afinado pra português)
# transcreve errado - seja por acento agudo em vez de mácron IAST ("ásana" como
# se fosse "câmera") seja por grafia simplificada. Mapa cresce sob demanda,
# conforme aparece em produção (2026-08-14, "ásanas"; 2026-08-18, "raga"/"rāga"
# e "dwesha" no vídeo de ansiedade). Cada valor já vem em minúsculo - a
# capitalização de saída é decidida por posição na frase, nunca lida daqui.
_SANSKRIT_FIXES = {
    "ásana": "āsana", "ásanas": "āsanas",
    "raga": "rāga", "dwesha": "dwesha",
}


def normalize_sanskrit_terms(text: str, sentence_start: bool = False) -> str:
    """Substitui grafia errada por IAST correto. Capitalização segue a MESMA
    regra do português - maiúscula só em início de frase (`sentence_start`),
    nunca só por ser termo estrangeiro/sânscrito (2026-08-18, correção de regra:
    a versão anterior preservava a capitalização que o ASR dava ao termo, e o
    ASR capitaliza por tratar termo estranho como nome próprio - "chamado Raga e
    Dwesha", no meio da frase, saía com maiúscula sem motivo nenhum). Quem chama
    essa função é responsável por rastrear `sentence_start` ao longo da lista de
    palavras (word anterior termina em `PUNCT_END`, ou é a primeira do vídeo)."""
    def repl(m: re.Match) -> str:
        word = m.group(0)
        core = word.strip('"\'.,:;!?')
        prefix = word[:len(word) - len(word.lstrip('"\''))]
        suffix = word[len(prefix) + len(core):]
        fixed = _SANSKRIT_FIXES.get(core.lower())
        if fixed is None:
            return word
        if sentence_start:
            fixed = fixed[0].upper() + fixed[1:]
        return prefix + fixed + suffix
    pattern = re.compile(r"[\"']?\w+[\"'.,:;!?]*")
    return pattern.sub(repl, text)


def capitalize_first(text: str) -> str:
    """Primeira letra do hook (card do frame 0) sempre maiúscula, independente
    de onde o corte começou na frase original."""
    return text[0].upper() + text[1:] if text else text


_QUOTED_WORD_PATTERN = re.compile(r'^"([^"]+)"([,.:;!?]*)$')
_CTA_TRIGGER_PATTERN = re.compile(r"^comenta", re.IGNORECASE)
_OPENS_QUOTE = re.compile(r'^"')
_CLOSES_QUOTE = re.compile(r'"[,.:;!?]*$')

# Frases fixas que carregam peso semântico/persuasivo JUNTAS e por isso sempre
# viram card isolado (item 11/12 do docstring) - nunca divididas entre cards,
# nunca coladas em outra oração. Generalizado de "CTA_PHRASES" (2026-08-14) pra
# "COHESIVE_PHRASES" (2026-08-15): não é só sobre call-to-action ("clica aqui"),
# é qualquer expressão-âncora da marca cujo impacto visual/persuasivo depende de
# ler tudo junto - "sentir na pele" é o outro exemplo real que motivou a
# generalização (variantes com "sua"/"própria" também contam, cada uma sua
# própria entrada). Cada entrada é uma tupla de 2+ palavras em minúsculo, sem
# pontuação. Cresce sob demanda conforme aparece em produção.
COHESIVE_PHRASES = [
    ("clica", "aqui"),
    ("sentir", "na", "pele"),
    ("sentir", "na", "sua", "pele"),
    ("sentir", "na", "própria", "pele"),
    ("hatha", "yoga"),
]


def _find_cohesive_spans(words: list[dict]) -> tuple[set[int], set[int]]:
    """Retorna (índices que iniciam uma frase coesa, índices que fecham uma).
    Casa frases de qualquer tamanho em COHESIVE_PHRASES, testando da mais longa
    pra mais curta em cada posição pra não parar numa correspondência parcial
    quando uma variante mais longa também se aplica ali."""
    starts: set[int] = set()
    ends: set[int] = set()
    phrases_by_len = sorted(COHESIVE_PHRASES, key=len, reverse=True)
    n = len(words)
    for i in range(n):
        for phrase in phrases_by_len:
            L = len(phrase)
            if i + L > n:
                continue
            candidate = tuple(words[i + k]["text"].rstrip('",.:;!?').lower() for k in range(L))
            if candidate == phrase:
                starts.add(i)
                ends.add(i + L - 1)
                break
    return starts, ends


def normalize_cta_quotes(words: list[dict], lookback: int = 6) -> None:
    """Quando o criador fala um CTA de comentário ("comenta aqui embaixo: 'palavra'"), a
    ASR transcreve a keyword entre aspas (trata como fala reportada). Mas aspas nesse
    contexto leem mal em legenda e competem visualmente com aspas de discurso reportado
    genuíno (ex: citando um pensamento interno, que deve continuar com aspas). Fix: só
    quando uma das últimas `lookback` palavras começa com "comenta" (comenta, comente,
    comentem...), troca aspas por CAIXA ALTA - preserva aspas em qualquer outro contexto."""
    for i, w in enumerate(words):
        m = _QUOTED_WORD_PATTERN.match(w["text"])
        if not m:
            continue
        window = words[max(0, i - lookback):i]
        if any(_CTA_TRIGGER_PATTERN.match(ww["text"]) for ww in window):
            w["text"] = m.group(1).upper() + m.group(2)


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


_FALSE_START_PATTERN = re.compile(r"^\w{1,12}-{1,2}$", re.IGNORECASE)


def load_words(transcript_path: str) -> list[dict]:
    data = json.loads(Path(transcript_path).read_text())
    words = data.get("words", data) if isinstance(data, dict) else data
    if isinstance(words, dict):
        words = words.get("words", [])
    words = [w for w in words if w.get("type", "word") == "word"]  # drop spacing/audio_event
    words = [w for w in words if (w.get("text") or "").strip()]
    words = [w for w in words if not _FALSE_START_PATTERN.match(w["text"].strip())]
    return words


def output_timeline(edl_path: str, transcript_path: str, fps: float = 24.0) -> tuple[list[dict], float]:
    """`seg_offset` acumula usando a duração de cada segmento ARREDONDADA PRA CIMA pro
    múltiplo de frame mais próximo (render.py extrai cada clipe com `-r {fps} -t <duration>`,
    reencode que sempre arredonda pra cima - nunca corta no meio de um frame). Usar a duração
    ideal do EDL direto aqui causa deriva cumulativa: cada segmento sai de alguns ms a ~1 frame
    mais longo que o pedido, e num corte com dezenas de segmentos isso soma frações de segundo
    perceptíveis (bug real: 32 segmentos, ~0.67s de deriva no card final). A posição relativa de
    cada palavra DENTRO do seu próprio segmento continua usando o tempo ideal (erro relativo
    limitado a <1 frame, não cumulativo)."""
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
        real_dur = math.ceil(round((e - s) * fps, 6)) / fps
        seg_offset += real_dur
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


def _find_list_items(words_group) -> list[list[dict]] | None:
    """Detecta uma enumeracao: 3+ 'itens' consecutivos terminados em virgula,
    seguidos do item final que fecha a lista (qualquer pontuacao terminal).
    Um item pode ter 1+ palavras (o limite e a virgula, nao a palavra).
    Retorna a lista de itens se encontrar 3+, senao None."""
    items, cur = [], []
    for w in words_group:
        cur.append(w)
        if w["text"].rstrip().endswith(","):
            items.append(cur)
            cur = []
    if cur:
        items.append(cur)
    return items if len(items) >= 3 else None


def _greedy_split(words_group, font, max_w, draw, stroke_width, max_lines) -> list[list[dict]]:
    result, cur = [], []
    for w in words_group:
        trial = cur + [w]
        text = " ".join(x["text"] for x in trial)
        if len(wrap_fits(text, font, max_w, draw, stroke_width)) > max_lines and cur:
            # Prefer breaking at the most recent comma already inside `cur` over
            # the raw width cutoff - a card that ends mid-clause because a word
            # happened to still fit reads worse than one that ends clean at the
            # clause boundary, even if a little shorter than the max.
            comma_idx = None
            for i in range(len(cur) - 1, -1, -1):
                if cur[i]["text"].rstrip().endswith(","):
                    comma_idx = i
                    break
            if comma_idx is not None and comma_idx < len(cur) - 1:
                result.append(cur[:comma_idx + 1])
                cur = cur[comma_idx + 1:] + [w]
            else:
                result.append(cur)
                cur = [w]
        else:
            cur.append(w)
    if cur:
        result.append(cur)
    return result


def split_to_fit(words_group, font, max_w, draw, stroke_width, max_lines) -> list[list[dict]]:
    items = _find_list_items(words_group)
    if items is None:
        return _greedy_split(words_group, font, max_w, draw, stroke_width, max_lines)

    # enumeracao real: ou todos os itens cabem juntos num card (stride
    # constante = tudo), ou cada item vira seu proprio card (stride constante
    # = 1) - nunca uma mistura greedy que cresce/encolhe entre cards.
    if fits_in([w for it in items for w in it], font, max_w, draw, stroke_width, max_lines):
        return [[w for it in items for w in it]]
    result = []
    for it in items:
        result.extend(_greedy_split(it, font, max_w, draw, stroke_width, max_lines))
    # marca pra passada 3 nunca reagrupar por duracao minima - colaria itens
    # de volta de forma inconsistente, o mesmo bug que essa regra corrige.
    for grp in result:
        for w in grp:
            w["_no_glue"] = True
    return result


def autosize_hook_font(text: str, font_path: str, font_index: int, base_size: int, max_size: int,
                        max_w: int, stroke_width: int, draw) -> "ImageFont.FreeTypeFont":
    """Hook curto (cabe em 1 linha no tamanho base) escala pra ocupar um espaço
    consistente da tela, em vez de ficar pequeno/esparso. Nunca reduz abaixo do
    tamanho base, nunca escala hooks que já quebram em 2+ linhas (esses já usam
    mais espaço vertical, não precisam de mais escala horizontal)."""
    base_font = ImageFont.truetype(font_path, base_size, index=font_index)
    if len(wrap_fits(text, base_font, max_w, draw, stroke_width)) != 1:
        return base_font
    bbox = draw.textbbox((0, 0), text, font=base_font, stroke_width=stroke_width)
    width = bbox[2] - bbox[0]
    if width <= 0:
        return base_font
    target_width = max_w * 0.92
    new_size = max(base_size, min(int(base_size * target_width / width), max_size))
    new_font = ImageFont.truetype(font_path, new_size, index=font_index)
    if len(wrap_fits(text, new_font, max_w, draw, stroke_width)) == 1:
        return new_font
    return base_font


def _diagonal_gradient_rgba(size: tuple[int, int], c1, c2) -> Image.Image:
    """Top-left (c1) to bottom-right (c2) linear gradient, e.g. a light highlight
    fading to a darker base tone - reads as a sheen/silk-like glint on a stroke
    rather than a flat color."""
    w, h = size
    xx, yy = np.meshgrid(np.arange(w), np.arange(h))
    t = (xx.astype(np.float32) + yy.astype(np.float32)) / max(1, (w + h - 2))
    c1a, c2a = np.array(c1, dtype=np.float32), np.array(c2, dtype=np.float32)
    grad = c1a[None, None, :] + (c2a - c1a)[None, None, :] * t[:, :, None]
    return Image.fromarray(grad.astype(np.uint8), mode="RGBA")


def render_card(text, out_path, font, stroke_w, max_w, canvas_w, fill, outline,
                 outline_gradient=None) -> tuple[int, int, int]:
    """outline_gradient: optional (color_from, color_to) RGBA pair - renders the
    stroke as a diagonal gradient (e.g. a sheen effect) instead of a flat outline
    color. Only isolates the stroke RING (full glyph+stroke silhouette minus the
    plain-fill silhouette), so the gradient never bleeds into the fill itself."""
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
    positions = []
    for ln, h in zip(lines, line_heights):
        bbox = draw.textbbox((0, 0), ln, font=font, stroke_width=stroke_w)
        w = bbox[2] - bbox[0]
        x = (canvas_w - w) // 2 - bbox[0]
        positions.append((x, y - bbox[1], ln))
        y += h + spacing

    if outline_gradient:
        mask_full = Image.new("L", img.size, 0)
        mask_fill = Image.new("L", img.size, 0)
        d_full, d_fill = ImageDraw.Draw(mask_full), ImageDraw.Draw(mask_fill)
        for x, ty, ln in positions:
            d_full.text((x, ty), ln, font=font, fill=255, stroke_width=stroke_w, stroke_fill=255)
            d_fill.text((x, ty), ln, font=font, fill=255, stroke_width=0)
        mask_stroke = ImageChops.subtract(mask_full, mask_fill)
        grad = _diagonal_gradient_rgba(img.size, outline_gradient[0], outline_gradient[1])
        img.paste(grad, (0, 0), mask_stroke)
        for x, ty, ln in positions:
            draw.text((x, ty), ln, font=font, fill=tuple(fill), stroke_width=0)
    else:
        for x, ty, ln in positions:
            draw.text((x, ty), ln, font=font, fill=tuple(fill), stroke_width=stroke_w, stroke_fill=tuple(outline))

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
    ap.add_argument("--no-hook", action="store_true", help="Skip the big hook card entirely; treat all words as body captions")
    ap.add_argument("--hook-text", default=None,
                     help="Editorial hook text overriding the verbatim transcript (e.g. a punchier "
                          "paraphrase). Shown as a short separate intro graphic (see --hook-duration) "
                          "layered over normal body captions, which keep following the real speech "
                          "from frame 0 - the hook words are NOT removed from body captioning.")
    ap.add_argument("--hook-duration", type=float, default=2.0,
                     help="Display duration in seconds for an editorial --hook-text card (default 2.0s). "
                          "Ignored when --hook-text is not set (verbatim hook times off the real words).")
    ap.add_argument("--fps", type=float, default=24.0, help="Framerate do render final (render.py usa -r 24) - usado pra arredondar duração de segmento igual ao encode real, evitando deriva cumulativa em cortes com muitos segmentos")
    args = ap.parse_args()

    cfg = load_config(args.config)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    words, total_dur = output_timeline(args.edl, args.transcript, fps=args.fps)
    normalize_cta_quotes(words)
    sentence_start = True
    for w in words:
        w["text"] = normalize_ce_para_voce(w["text"])
        w["text"] = normalize_stutter(w["text"])
        w["text"] = normalize_sanskrit_terms(w["text"], sentence_start=sentence_start)
        sentence_start = w["text"].rstrip('"\'').endswith(PUNCT_END)
    if args.text_rules:
        apply_text_rules(words, json.loads(Path(args.text_rules).read_text()))

    # hook can override font_path/font_index (e.g. a bold sans for an editorial
    # intro card, distinct from the body caption's serif) - falls back to the
    # shared top-level font when not set, so verbatim-hook videos are unaffected.
    hook_font_path = cfg["hook"].get("font_path", cfg["font_path"])
    hook_font_index = cfg["hook"].get("font_index", cfg["font_index"])
    hook_font = ImageFont.truetype(hook_font_path, cfg["hook"]["font_size"], index=hook_font_index)
    body_font = ImageFont.truetype(cfg["font_path"], cfg["body"]["font_size"], index=cfg["font_index"])
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))

    cards = []
    if args.no_hook:
        body_words = words
    else:
        hook_words = []
        for w in words:
            hook_words.append(w)
            if w["text"].rstrip('"\'').endswith((":", ".", "?", "!")):
                break
        hook_end_idx = len(hook_words)
        hook_out_start = 0.0
        if args.hook_text:
            # Editorial hook text is a separate intro graphic, not a caption for the
            # spoken hook words - it gets its own short flash duration (--hook-duration)
            # and does NOT consume the hook words from body captioning. The real speech
            # keeps flowing as normal captions underneath from frame 0, hook included.
            hook_text = args.hook_text
            hook_out_end = args.hook_duration
            body_words = words
        else:
            hook_text = strip_trailing_grammatical_punct(" ".join(w["text"] for w in hook_words))
            hook_text = capitalize_first(hook_text)
            natural_hook_end = hook_words[-1]["end"]
            hook_out_end = natural_hook_end + 0.35
            body_words = words[hook_end_idx:]
            if body_words:
                hook_out_end = min(hook_out_end, body_words[0]["start"] - 0.02)
                hook_out_end = max(hook_out_end, natural_hook_end + 0.05)

        max_auto = cfg["hook"].get("max_auto_font_size", int(cfg["hook"]["font_size"] * 1.4))
        sized_hook_font = autosize_hook_font(hook_text, hook_font_path, hook_font_index,
                                              cfg["hook"]["font_size"], max_auto,
                                              cfg["hook"]["max_width"], cfg["hook"]["stroke_width"], probe)
        hook_fill = cfg["hook"].get("fill_color", cfg["fill_color"])
        hook_outline = cfg["hook"].get("outline_color", cfg["outline_color"])
        hook_gradient = cfg["hook"].get("outline_gradient")
        hw, hh, _ = render_card(hook_text, out_dir / "card_hook.png", sized_hook_font, cfg["hook"]["stroke_width"],
                                 cfg["hook"]["max_width"], cfg["canvas_w"], hook_fill, hook_outline,
                                 outline_gradient=hook_gradient)
        cards.append({"file": "card_hook.png", "start": hook_out_start, "end": hook_out_end, "style": "hook",
                      "text": hook_text, "w": hw, "h": hh})

    body_max_lines = cfg["body"]["max_lines"]
    min_dur = cfg["min_display_duration"]
    gap_thresh = cfg["phrase_break_gap"]

    # pass 1: natural phrase groups - punctuation, silence gap, OR a segment
    # (cut) boundary, which must always break regardless of gap/punctuation.
    cohesive_starts, cohesive_ends = _find_cohesive_spans(body_words)
    groups, cur = [], []
    for i, w in enumerate(body_words):
        if _OPENS_QUOTE.match(w["text"]) and cur:
            # isola tambem a palavra que introduz a citacao (lead-in) - um
            # beat de antecipacao antes da citacao aparecer, em vez de colar
            # no final da oracao anterior.
            if len(cur) > 1:
                groups.append(cur[:-1])
                groups.append([cur[-1]])
            else:
                groups.append(cur)
            cur = []
        if i in cohesive_starts and cur:
            # frase coesa fixa (COHESIVE_PHRASES, ex. "clica aqui", "sentir na
            # pele") sempre isolada - nunca cola no final da oracao anterior.
            groups.append(cur)
            cur = []
        cur.append(w)
        closes_quote = bool(_CLOSES_QUOTE.search(w["text"]))
        end_here = w["text"].rstrip('"\'').endswith(PUNCT_END)
        is_cohesive_end = i in cohesive_ends
        gap = (body_words[i + 1]["start"] - w["end"]) if i + 1 < len(body_words) else 999
        seg_changes = (i + 1 < len(body_words)) and (body_words[i + 1]["seg"] != w["seg"])
        if closes_quote or end_here or is_cohesive_end or gap >= gap_thresh or seg_changes or i == len(body_words) - 1:
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
            if groups[j][-1]["text"].rstrip('"\'').endswith(PUNCT_END):
                break
            if groups[j][-1].get("_no_glue") or groups[j + 1][0].get("_no_glue"):
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
        text = strip_trailing_grammatical_punct(" ".join(w["text"] for w in g))
        start = g[0]["_disp_start"]
        end = g[-1]["_disp_end"] + (0.15 if gi == len(groups) - 1 else 0)
        fname = f"card_body_{gi:03d}.png"
        bw, bh, nlines = render_card(text, out_dir / fname, body_font, cfg["body"]["stroke_width"],
                                      cfg["body"]["max_width"], cfg["canvas_w"], cfg["fill_color"], cfg["outline_color"])
        if nlines > body_max_lines:
            print(f"  AVISO: card {gi} ainda com {nlines} linhas: {text!r}")
        cards.append({"file": fname, "start": start, "end": end, "style": "body", "text": text, "w": bw, "h": bh})

    # pass 5: overlap safety net WITHIN a track (hook vs. body render at different
    # screen positions and are allowed to overlap on purpose when --hook-text
    # gives the hook its own independent short flash duration - only clamp
    # overlap between two cards on the SAME track).
    for k in range(len(cards) - 1):
        if cards[k]["style"] != cards[k + 1]["style"]:
            continue
        if cards[k]["end"] > cards[k + 1]["start"] - 0.01:
            cards[k]["end"] = max(cards[k]["start"] + 0.15, cards[k + 1]["start"] - 0.02)

    (out_dir / "cards.json").write_text(json.dumps({"cards": cards, "total_duration": total_dur, "config": cfg},
                                                     indent=2, ensure_ascii=False))
    print(f"gerados {len(cards)} cards (1 hook + {len(groups)} body), duracao total {total_dur:.2f}s")


if __name__ == "__main__":
    main()
