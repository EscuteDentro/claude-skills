#!/bin/bash
# Remove o fundo de um PNG via chroma key (ffmpeg), sem depender de Pillow/Python.
# Amostra a cor do canto automaticamente e aplica colorkey com parametros calibrados
# por tentativa e erro (ver SKILL.md, "Recorte de fundo" para o porque desses valores).
#
# Uso:
#   sh remover_fundo.sh entrada.png saida.png
#
# Se sobrar franja colorida nas bordas depois, rode de novo em cima do proprio output
# (ele reamostra o canto a cada chamada, entao uma segunda passada mais suave costuma
# limpar sem precisar mexer nos parametros):
#   sh remover_fundo.sh saida.png saida.png

set -e

IN="${1:?uso: remover_fundo.sh <entrada.png> <saida.png>}"
OUT="${2:?uso: remover_fundo.sh <entrada.png> <saida.png>}"

# amostra a cor do canto superior esquerdo (pixel em x=5,y=5)
HEX=$(ffmpeg -i "$IN" -vf "crop=1:1:5:5" -f rawvideo -pix_fmt rgb24 - 2>/dev/null | xxd -p)

echo "Cor de fundo amostrada: 0x$HEX"

# similarity=0.16, blend=0.03: comeu a franja sem corroer o objeto, na pratica.
# Comecar por esses valores; se sobrar franja, subir similarity aos poucos (ate ~0.20);
# se comecar a comer o objeto (fica com "buracos" ou desbota cor solida perto da borda),
# baixar de novo. NAO usar o filtro `despill`: ele deforma a cor original do objeto
# (testado e descartado, ver SKILL.md).
ffmpeg -y -i "$IN" -vf "colorkey=0x${HEX}:0.16:0.03,format=rgba" "$OUT"

echo "Salvo: $OUT"
echo ""
echo "Se o fundo original for parecido em tom com o sujeito (ex: fundo bege perto de"
echo "pele), colorkey direto vai comer pedaco do sujeito. Nesse caso, ANTES de rodar"
echo "este script, troque o fundo por um verde puro via gerar_asset.py (modo --edit,"
echo "prompt pedindo so a troca do fundo por chroma-key verde, mantendo o resto"
echo "identico) — so entao rode este script na versao com fundo verde."
