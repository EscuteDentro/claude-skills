---
name: legenda-estilizada
description: Gera legenda estilizada (hook grande + corpo fluido de 1 linha) pra qualquer vídeo talking-head, a partir de um EDL + transcrição ElevenLabs Scribe. Agnóstico de fonte/tamanho/posição via config JSON.
---

# Legenda Estilizada

Gera cards de legenda em PNG (com transparência) a partir de uma transcrição word-level
(ElevenLabs Scribe) e um EDL de cortes (formato compatível com
[video-use](https://github.com/browser-use/video-use)), e compõe no vídeo via overlay ffmpeg.

Validado em produção real (talking-head 9:16). **O default do skill (`scripts/config_default.json`)
é genérico de propósito** — fonte (Helvetica Neue Bold) e posicionamento (corpo no rodapé, sem
margem) neutros, não a identidade visual de nenhuma marca específica. Um exemplo de configuração
com identidade própria (PT Serif Bold, ambas as camadas centralizadas em pontos fixos da tela)
fica em `scripts/config_examples/serif-editorial.json` — usar `--config` apontando pra ele (ou
copiar e ajustar) pra reproduzir esse look específico.

## Duas camadas

- **Hook**: a primeira frase inteira, na tela desde o frame 0, fonte grande, centralizada.
- **Corpo**: o resto, fonte menor, no máximo N linhas por card (default: 1), flui naturalmente
  acompanhando pausas de fala.

## Ancoragem vertical (`anchor`)

Cada camada (`hook`/`body`) escolhe um modo:

- **`"center"`**: fixa em torno de um `center_y` absoluto, igual pra qualquer card daquela
  camada, independente da altura do texto renderizado.
- **`"bottom"`**: fixa a `bottom_margin` pixels da borda inferior do canvas — a margem visual
  real fica constante mesmo comparando um card de 1 linha com um de 2, curto ou longo (um
  `center_y` fixo não consegue garantir isso, já que a altura do card muda).

Default do skill: corpo em `"bottom"` com `bottom_margin: 0` (rente ao rodapé, convenção mais
comum de legenda). O exemplo `serif-editorial.json` usa `"center"` nas duas camadas, com os
pontos específicos validados pra formato 9:16/Reels (evita a zona de ícones de UI no rodapé).

## Uso

```bash
python scripts/build_captions.py <edl.json> <transcript.json> <out_dir> \
  [--config meu_config.json] [--text-rules minhas_regras.json]

python scripts/composite_captions.py <out_dir> <video_base.mp4> <video_final.mp4> \
  [--config meu_config.json]
```

`--no-hook` (em `build_captions.py`) trata todas as palavras como corpo, sem gerar o card de
hook grande. Útil quando o hook já foi resolvido fora do script (ex: uma cena separada,
repetida de outro ponto do vídeo, que serve de abertura e não deve competir com legenda normal).

`--config` faz merge parcial (deep) sobre `config_default.json` — só precisa declarar o que
quer mudar. Ver todos os campos configuráveis em `scripts/config_default.json`: fonte
(`font_path`, `font_index` — arquivos `.ttc`/`.ttf` com múltiplos estilos usam índice),
cores (`fill_color`, `outline_color`, RGBA), tamanho de canvas, e por camada (hook/body):
`font_size`, `stroke_width`, `max_width`, `max_lines` (só body), `anchor` (`"center"` ou
`"bottom"`), `center_y` (se `anchor: "center"`) ou `bottom_margin` (se `anchor: "bottom"`).

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
6. **Nunca pontuação puramente gramatical (`.`, `,`, `:`, `;`) no fim de um card.** A quebra
   visual pro card seguinte já comunica a pausa — repetir isso com pontuação é redundante.
   Aplicado só no texto final de cada card (hook e corpo), depois de toda a lógica de
   agrupamento/quebra já ter usado a pontuação original pra decidir onde cortar. `?` e `!`
   sempre ficam (carregam intenção emocional/interrogativa, não meramente gramatical) — sem
   tentar distinguir um "?" gramatical de um emocional, todo `?`/`!` é preservado.

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
