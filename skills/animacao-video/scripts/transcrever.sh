#!/bin/bash
# Transcreve narracao.mp3 com timestamp por PALAVRA (nao so por frase).
#
# Requer: openai-whisper instalado (`pip install openai-whisper` ou `brew install whisper-cpp`
# nao serve, precisa ser o pacote Python que suporta --word_timestamps).
#
# Uso:
#   sh transcrever.sh audio/narracao.mp3 pt audio/
#
# Gera audio/narracao.json com segments[].words[] = [{word, start, end}, ...] em segundos.

set -e

AUDIO="${1:?uso: transcrever.sh <audio.mp3> [idioma=pt] [output_dir=.]}"
LANG="${2:-pt}"
OUTDIR="${3:-.}"

whisper "$AUDIO" --model small --language "$LANG" --word_timestamps True \
  --output_format json --output_dir "$OUTDIR"

echo ""
echo "Pronto. O JSON tem segments[].words[] com start/end em segundos por palavra."
echo "ATENCAO: o whisper erra a grafia de algumas palavras (ex: 'porque' vira 'por que',"
echo "'nutre amizade' pode virar uma palavra so). Use o JSON só para o TEMPO, nunca pro"
echo "TEXTO exibido — o texto exibido sempre vem do roteiro original (fonte confiavel)."
echo "Precisa reconciliar manualmente contagem de palavras roteiro x whisper por trecho"
echo "antes de usar os timestamps (ver SKILL.md, Fase 3)."
