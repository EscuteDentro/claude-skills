#!/usr/bin/env python3
"""
Recorta uma folha de alfabeto (fundo solido, ex: branco) em PNGs individuais
por caractere, com fundo transparente e uma tabela de largura por glifo.

100% local: ffmpeg (dump de pixel cru + crop + colorkey) + Python stdlib, sem
Pillow, sem API. Deteccao de glifo por projecao (linhas de pixel com "tinta"
= caractere; colunas com "tinta" dentro de cada linha = glifo individual).

Uso:
  python3 recortar_alfabeto.py entrada.png saida_dir/

A ordem esperada dos caracteres (deve bater com o que foi pedido na geracao)
esta em CHAR_SEQUENCE abaixo — ajustar se a folha for diferente.
"""
import json
import subprocess
import sys
from pathlib import Path

CHAR_SEQUENCE = list("abcdefghijklmnopqrstuvwxyz") + list("áàâãéêíóôõúüç") + list("0123456789") + [
    ",", ".", "!", "?", ":", ";", "-", "'",
]

# nomes seguros de arquivo pra caracteres que nao dao pra usar cru num path
SAFE_NAMES = {
    ",": "virgula", ".": "ponto", "!": "exclamacao", "?": "interrogacao",
    ":": "dois-pontos", ";": "ponto-virgula", "-": "hifen", "'": "apostrofo",
}


def run(cmd: list[str]) -> bytes:
    return subprocess.run(cmd, check=True, capture_output=True).stdout


def get_dims(path: Path) -> tuple[int, int]:
    out = run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path),
    ]).decode().strip()
    w, h = out.split(",")
    return int(w), int(h)


def get_raw_rgb(path: Path, w: int, h: int) -> bytes:
    return run([
        "ffmpeg", "-v", "error", "-i", str(path),
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
    ])


def is_ink(r: int, g: int, b: int, bg: tuple[int, int, int], threshold: int) -> bool:
    return abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2]) > threshold


def find_bands(has_ink_per_line: list[bool], min_gap: int = 3) -> list[tuple[int, int]]:
    """Acha (inicio, fim) de trechos contiguos de True, ignorando gaps curtos (ruido)."""
    bands = []
    start = None
    gap = 0
    for i, v in enumerate(has_ink_per_line):
        if v:
            if start is None:
                start = i
            gap = 0
        else:
            if start is not None:
                gap += 1
                if gap > min_gap:
                    bands.append((start, i - gap))
                    start = None
                    gap = 0
    if start is not None:
        bands.append((start, len(has_ink_per_line) - 1))
    return bands


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("uso: recortar_alfabeto.py entrada.png saida_dir/")
    src = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    w, h = get_dims(src)
    print(f"Imagem: {w}x{h}")
    raw = get_raw_rgb(src, w, h)
    assert len(raw) == w * h * 3, f"tamanho inesperado: {len(raw)} != {w*h*3}"

    def px(x: int, y: int) -> tuple[int, int, int]:
        i = (y * w + x) * 3
        return raw[i], raw[i + 1], raw[i + 2]

    bg = px(2, 2)  # amostra do canto
    print(f"Fundo detectado: rgb{bg}")
    THRESH = 40

    # projecao por linha: alguma coluna daquela linha tem tinta?
    row_has_ink = []
    for y in range(h):
        ink = False
        for x in range(0, w, 3):  # amostragem a cada 3px, mais rapido, precisao suficiente
            r, g, b = px(x, y)
            if is_ink(r, g, b, bg, THRESH):
                ink = True
                break
        row_has_ink.append(ink)

    row_bands = find_bands(row_has_ink, min_gap=4)
    print(f"Linhas de texto detectadas: {len(row_bands)}")

    glyphs = []  # (x0,y0,x1,y1)
    for (ry0, ry1) in row_bands:
        col_has_ink = []
        for x in range(w):
            ink = False
            for y in range(ry0, ry1 + 1, 2):
                r, g, b = px(x, y)
                if is_ink(r, g, b, bg, THRESH):
                    ink = True
                    break
            col_has_ink.append(ink)
        col_bands = find_bands(col_has_ink, min_gap=6)
        for (cx0, cx1) in col_bands:
            glyphs.append((cx0, ry0, cx1, ry1))

    print(f"Glifos detectados: {len(glyphs)} (esperado: {len(CHAR_SEQUENCE)})")
    if len(glyphs) != len(CHAR_SEQUENCE):
        print("AVISO: contagem nao bate. Conferindo os primeiros/ultimos detectados:", file=sys.stderr)
        for g in glyphs[:3] + glyphs[-3:]:
            print("  ", g, file=sys.stderr)
        sys.exit(1)

    meta = {}
    PAD = 6
    for char, (gx0, gy0, gx1, gy1) in zip(CHAR_SEQUENCE, glyphs):
        cx0, cy0 = max(0, gx0 - PAD), max(0, gy0 - PAD)
        cw, ch = (gx1 - gx0) + PAD * 2, (gy1 - gy0) + PAD * 2
        name = SAFE_NAMES.get(char, char)
        raw_path = out_dir / f"_raw-{name}.png"
        final_path = out_dir / f"{name}.png"
        run([
            "ffmpeg", "-y", "-v", "error", "-i", str(src),
            "-vf", f"crop={cw}:{ch}:{cx0}:{cy0}",
            str(raw_path),
        ])
        hexcolor = f"{bg[0]:02x}{bg[1]:02x}{bg[2]:02x}"
        run([
            "ffmpeg", "-y", "-v", "error", "-i", str(raw_path),
            "-vf", f"colorkey=0x{hexcolor}:0.20:0.05,format=rgba",
            str(final_path),
        ])
        raw_path.unlink()
        # largura E altura: necessario pra escalar cada glifo pra uma altura
        # de linha comum na hora de tipografar (glifos de linhas diferentes
        # da folha original tem altura de recorte levemente diferente).
        meta[char] = {"file": name, "w": cw, "h": ch}
        print(f"  '{char}' -> {name}.png ({cw}x{ch})")

    (out_dir / "glifos.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nPronto. {len(glyphs)} glifos salvos em {out_dir}, glifos.json gerado.")


if __name__ == "__main__":
    main()
