---
name: moldura-colagem
description: Recorta um vídeo (ou imagem) num retângulo com borda de papel rasgado irregular, compositado sobre um fundo — como se fosse uma foto colada numa página de scrapbook. Parametrizável via config JSON (fundo, proporção, cor do papel, irregularidade da borda). Dois modos de aplicação: lote de frames PNG (clipes curtos) ou ffmpeg direto (vídeo longo, muito mais rápido).
---

# Moldura Colagem

Recorta o quadro de um vídeo/imagem num retângulo com borda fibrosa irregular (não uma linha
reta) + um aro de papel entre o vídeo e o fundo, dando a sensação de "foto colada numa página".
Nasceu do projeto Buda e Eleições (Escute Dentro, 2026-09) como solução pro pedido "a parede
branca real nunca aparece, sempre tem colagem no lugar" — em vez de tentar recortar a pessoa do
fundo (rotoscopia, caro e arriscado com cabelo/movimento), a peça inteira vira um retângulo
"colado", com o fundo aparecendo só na margem. Zero dependência de matting/IA.

**O default do skill (`scripts/config_default.json`) é genérico de propósito** — fundo em
`null` (skill não funciona sem você apontar um fundo real), cor de papel creme neutra, sem
nenhuma identidade de marca específica. Pra reproduzir um look de marca real, copie a estrutura
pra um config **fora deste repo** (privado) com o fundo e a paleta reais — mesma convenção já
usada em `legenda-estilizada`.

## Como funciona

Duas máscaras (arrays de alpha) geradas a partir do MESMO campo de ruído suavizado, cada uma
com seu próprio raio de irregularidade (`band_px`):

1. **`video_mask`**: retângulo interno, onde o vídeo aparece.
2. **`paper_mask`**: retângulo um pouco maior, preenchido com `paper_color` — o "aro de papel"
   visível entre a borda do vídeo e o fundo.

Camadas compostas de baixo pra cima: fundo → papel (com sua máscara) → vídeo (com sua máscara).
Usar o mesmo campo de ruído nas duas garante que as duas bordas tenham a mesma "caligrafia"
fibrosa, em vez de padrões desencontrados.

## Dois modos de aplicação

- **`aplicar_frames.py`**: processa um diretório de frames PNG/JPG já extraídos (`f0000.ext`,
  `f0001.ext`...). Rápido pra clipes curtos (até ~15-20s) ou quando os frames já passaram por
  outro processamento frame a frame (ex: um sticker composto em cima, como o Buda na mão do
  projeto original).
- **`aplicar_video.py`**: aplica direto num arquivo de vídeo via filtro ffmpeg
  (`alphamerge`+`overlay`, mesma técnica documentada em `.claude/videosys/ARQUITETURA.md` seção
  1.2 pra esse tipo de bloqueio). **Muito mais rápido** pra vídeo longo (corpo inteiro de um
  episódio, minutos de duração) — um único pass de encode, não gera milhares de PNGs em disco.
  Essa é a opção default pra qualquer coisa acima de ~20s.

Ambos leem a mesma config e produzem resultado idêntico (mesma matemática de máscara) — a
escolha entre os dois é só sobre performance/practicalidade, não sobre resultado visual.

## Uso

```bash
# clipe curto, frames ja extraidos
python3 scripts/aplicar_frames.py <frames_dir> <out_dir> <n_frames> \
  --config minha_config.json [--start-index N] [--ext jpg]

# video longo, direto do arquivo fonte
python3 scripts/aplicar_video.py <video_entrada.mp4> <video_saida.mp4> \
  --config minha_config.json [--ss INICIO] [--t DURACAO] [--fps 30]
```

`--background` em qualquer um dos dois sobrescreve o `background_image` do config, sem precisar
duplicar o arquivo de config só pra trocar de fundo.

## Parâmetros do config

| Campo | O que controla |
|---|---|
| `canvas_w`, `canvas_h` | Resolução/proporção final. Qualquer aspect ratio, não só 9:16. |
| `video_inset` | Margem do retângulo do vídeo (fração do canvas). Maior = vídeo menor/mais afastado da borda. |
| `paper_inset` | Margem do aro de papel. Menor que `video_inset` = aro mais largo visível. |
| `video_band_px` / `paper_band_px` | Irregularidade da borda fibrosa, em pixels. Maior = rasgo mais agressivo/orgânico. |
| `paper_color` | Cor do aro de papel, `[R, G, B]`. |
| `noise_seed` | Determinístico — mesma seed = mesmo padrão de rasgo (útil pra manter consistência entre clipes do mesmo projeto). |
| `background_image` | Caminho absoluto da imagem de fundo (a "página" onde o vídeo é colado). Único campo sem default genérico — obrigatório informar. |

## Corner cases / decisões já tomadas

- **CRÍTICO — `-shortest` obrigatório no `aplicar_video.py`**: fundo/máscara/papel são inputs em
  loop infinito (`-loop 1`). Sem `-shortest` no output, o ffmpeg não para quando o vídeo
  principal (finito) acaba — bug real (2026-09-02): rodou 47min de encode pra uma fonte de 60s,
  só parou porque foi morto manualmente. Já corrigido no script; se algum fork/cópia não tiver
  o `-shortest`, adicionar antes de rodar em produção.
- **Fundo/vídeo com proporção diferente do canvas distorcia (stretch), não cortava**: tanto
  `aplicar_video.py` (`scale=w:h` no ffmpeg) quanto `aplicar_frames.py` (`.resize()` do PIL)
  esticavam a imagem pra caber exatamente no canvas em vez de recortar preservando proporção —
  bug real (2026-09-03), passou despercebido porque os 2 primeiros fundos usados em produção
  coincidiam exatamente com a proporção do canvas (9:16). Confirmado com imagem de teste
  quadrada (círculo virava oval). Fix: `scale=w:h:force_original_aspect_ratio=increase,
  crop=w:h` no ffmpeg; função `cover_resize()` (crop central preservando proporção) no PIL —
  aplicado a fundo E vídeo/frame de entrada nos dois scripts. Testado: resultado idêntico
  (diferença de recompressão apenas, média <1/255) nos vídeos já entregues cuja proporção já
  batia, e círculo perfeito preservado no teste com proporção deliberadamente diferente.
- **Fps do vídeo de saída**: sempre force `--fps` explicitamente igual ao do vídeo de entrada.
  As imagens de fundo/máscara em loop (`-loop 1`) não têm fps próprio — sem isso, o ffmpeg
  negocia um fps default (25) pro grafo de filtros inteiro, dessincronizando com o vídeo fonte
  (bug real, 2026-09-01: corpo saiu a 25fps quando a fonte era 30fps, quebrou concatenação
  posterior com outros trechos a 30fps).
- **`-t` (duração) só como opção de OUTPUT**, nunca duplicado como opção de input antes do
  `-i` do vídeo principal — os inputs em loop (fundo/máscaras) são tecnicamente infinitos, quem
  define a duração real de saída é o corte no vídeo principal + o `-t` de saída.
- **Concatenar o resultado com outros trechos**: usar o filtro `concat` (`filter_complex`), não
  o demuxer `concat` por lista de arquivo — o demuxer por lista mostrou inflar a duração final
  de forma inconsistente quando os arquivos vêm de pipelines diferentes com timestamps internos
  não uniformes (bug real, 2026-09-01/02, ver `videosys/ARQUITETURA.md`).
