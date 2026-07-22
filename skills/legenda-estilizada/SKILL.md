---
name: legenda-estilizada
description: Gera legenda estilizada (hook grande + corpo fluido de 1 linha) pra qualquer vídeo talking-head, a partir de um EDL + transcrição ElevenLabs Scribe. Agnóstico de fonte/tamanho/posição via config JSON.
---

# Legenda Estilizada

Gera cards de legenda em PNG (com transparência) a partir de uma transcrição word-level
(ElevenLabs Scribe) e um EDL de cortes (formato compatível com
[video-use](https://github.com/browser-use/video-use)), e compõe no vídeo via overlay ffmpeg.

Validado em produção em 2026-07-21/22 (vídeo "Amigo de 20 anos", Escute Dentro) — ver o
default (`scripts/config_default.json`) como ponto de partida real, não teórico.

## Duas camadas

- **Hook**: a primeira frase inteira, na tela desde o frame 0, fonte grande, centralizada.
- **Corpo**: o resto, fonte menor, no máximo N linhas por card (default: 1), flui naturalmente
  acompanhando pausas de fala.

## Uso

```bash
python scripts/build_captions.py <edl.json> <transcript.json> <out_dir> \
  [--config meu_config.json] [--text-rules minhas_regras.json]

python scripts/composite_captions.py <out_dir> <video_base.mp4> <video_final.mp4> \
  [--config meu_config.json]
```

`--config` faz merge parcial (deep) sobre `config_default.json` — só precisa declarar o que
quer mudar. Ver todos os campos configuráveis em `scripts/config_default.json`: fonte
(`font_path`, `font_index` — arquivos `.ttc`/`.ttf` com múltiplos estilos usam índice),
cores (`fill_color`, `outline_color`, RGBA), tamanho de canvas, e por camada (hook/body):
`font_size`, `stroke_width`, `max_width`, `center_y`, `max_lines` (só body).

`--text-rules` aceita uma lista de `{"pattern": "regex", "replacement": "..."}` (regex Python,
aplicado ANTES de qualquer medição de largura — necessário pra decisão de quebra de linha ficar
certa). **Atenção ao escapar barra invertida em JSON**: `\b` sozinho em JSON é o caractere de
backspace (`\x08`), não o word-boundary de regex — sempre escrever `\\b` no arquivo de regras.

## Regras de design (por que o script é assim, não outro jeito)

1. **Nunca decidir quebra de linha por contagem de palavras.** Sempre medir o texto renderizado
   no tamanho de fonte real (`draw.textbbox`). Fonte grande quebra qualquer heurística de
   contagem fixa.
2. **Toda fronteira de corte do EDL tem que forçar quebra de card**, independente de gap de
   tempo ou pontuação. Se o corte já removeu a pausa do áudio, o gap no timeline de saída fica
   ~0 — sem essa regra, uma legenda pode colar o fim de uma frase com o início da próxima
   (que só é dita segundos depois na gravação original), fazendo o texto aparecer antes da
   fala. Implementado via tag de índice de segmento em cada palavra (`seg`), checado em TODA
   passagem de agrupamento — inclusive a que gruda cards curtos (item 4).
3. **Filtrar eventos não-verbais da transcrição** (`type != "word"` no JSON da Scribe — ela
   marca risos/ruídos como `"type": "audio_event"`, não como palavra).
4. **Duração mínima de exibição por card** (default 0.70s) — uma palavra isolada sem isso só
   pisca na tela. Tenta colar no próximo card primeiro (se ainda couber no limite de linhas E
   não cruzar uma fronteira de corte); senão, estende o tempo de exibição pro silêncio antes do
   próximo card, nunca ultrapassando o início dele.
5. **Normalização de texto sempre antes da medição de largura**, nunca depois — senão a decisão
   de quebra de linha já foi tomada com o texto errado.

## Formato dos arquivos de entrada

**EDL** (compatível com video-use):
```json
{"ranges": [{"source": "...", "start": 4.5, "end": 15.82}, ...]}
```

**Transcript** (ElevenLabs Scribe, word-level):
```json
{"words": [{"text": "...", "start": 4.52, "end": 4.9, "type": "word"}, ...]}
```

## Limitações conhecidas

- Depende de fonte instalada localmente (`.ttf`/`.ttc` com o índice de estilo certo) — não
  baixa fonte nenhuma.
- Overlay via ffmpeg puro (sem libass) — funciona em qualquer build de ffmpeg, mesmo sem
  suporte a legenda/`subtitles` filter (motivo original de existir: o ffmpeg do Homebrew não
  vem com libass por padrão).
