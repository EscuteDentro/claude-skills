---
name: overlay-cta
description: Gera um elemento gráfico de overlay (balão de fala, badge, selo etc.) como PNG a partir de texto, e compõe num vídeo com SFX opcional no instante em que aparece. Agnóstico de forma/cor/fonte/borda via config JSON.
---

# Overlay CTA

Gera um elemento gráfico estático (balão de fala, badge, etiqueta) como PNG com transparência
a partir de texto (emoji suportado), e sobrepõe num vídeo via ffmpeg a partir de um timestamp,
opcionalmente mixando um SFX de entrada no mesmo instante.

Não é legenda dinâmica por palavra (isso é a skill `legenda-estilizada`) - é UM elemento gráfico
fixo que aparece uma vez, tipicamente perto do fim de um vídeo como CTA (pedido de engajamento,
selo, contador). As duas skills são independentes e compostas na ordem que fizer sentido pro
vídeo (legenda normalmente por baixo, overlay-cta por cima, já que o CTA
deve ficar sempre visível quando aparece).

Também não é a mesma coisa que os templates animados de `video-efeitos` (CTA pulsante, selo
circular, lower third — ver `ARQUITETURA.md` seção 1.3): aqueles usam GSAP+Puppeteer+browser
headless e produzem MOVIMENTO (escala pulsando, entrada animada). Esta skill é 100% estática
(PIL + overlay ffmpeg puro) - mais barata, mais rápida, sem dependência de browser, mas sem
animação. Escolha por movimento: se precisa de motion, é `video-efeitos`; se um elemento fixo
com SFX de entrada já resolve, é `overlay-cta`.

**O nome do módulo é sobre a FUNÇÃO (overlay de CTA), não a FORMA.** "Balão" é só uma das formas
possíveis (`shape="rounded_tail"`, a única usada em produção até agora) - o sistema é agnóstico
de forma desde o design (ver "Forma plugável" abaixo), por isso os arquivos/funções se chamam
`overlay`, não `balloon`. Ao documentar um USO REAL específico (ex: o balão terracota do Escute
Dentro), "balão" volta a ser o termo certo, porque é literalmente o que aquela instância é.

**O default do skill (`scripts/overlay_config_default.json`) é genérico de propósito** - cor
cinza neutra, fonte Arial Bold do sistema, sem borda. Pra reproduzir a identidade visual real de
uma marca, copie a estrutura desse JSON pra um arquivo **fora deste repo** (privado) com os
valores reais, mesma convenção da skill `legenda-estilizada`.

## Duas etapas

- **`build_overlay.py`**: texto → PNG (com transparência, sombra suave, borda opcional).
- **`composite_overlay.py`**: PNG + vídeo + timestamp (+ SFX opcional) → vídeo final.

## Forma plugável (`shape`)

A silhueta do overlay não é fixa - é um registro (`SHAPES` em `build_overlay.py`) de funções
`fn(w, h, **shape_kwargs) -> Image "L"` (máscara 0/255). Formas disponíveis hoje:

- **`"rounded_tail"`** (default): retângulo arredondado + rabicho triangular apontando pra
  baixo-esquerda (balão de fala clássico). `shape_kwargs` aceita `radius`, `tail_h`, `tail_w`,
  `tail_x_frac` (posição horizontal do rabicho, 0-1, default 0.30) pra ajustar sem tocar código.
- **`"rounded_no_tail"`**: retângulo arredondado simples, sem rabicho - badge/etiqueta/selo que
  não aponta pra ninguém.
- **`"ellipse"`**: oval. `shape_kwargs` aceita `pad_frac` (margem entre o texto e a borda da
  curva, default 0.18).

**Adicionar uma forma nova**: escrever uma função com essa assinatura, registrar em `SHAPES` no
topo de `build_overlay.py`. A função pode retornar uma máscara MAIOR que `(w, h)` se precisar de
espaço extra (rabicho, decoração) - o resto do pipeline deriva canvas, sombra, borda e
composição de texto a partir do `mask.size` real, nunca assume `(w, h)` cru. Isso é o que torna
o sistema agnóstico de forma: nenhuma outra parte do código sabe ou se importa com QUAL forma
está sendo desenhada.

## Uso

```bash
python scripts/build_overlay.py "Seu texto aqui" \
  --config meu_overlay.json --out overlay.png --rotation-deg -9 --out-scale 1.2

python scripts/composite_overlay.py video_base.mp4 overlay.png video_final.mp4 \
  --x 354 --y 10 --tstart 140.4 [--sfx som.wav]
```

`--config` faz merge parcial (deep) sobre `overlay_config_default.json` - só precisa declarar o
que quer mudar. Campos: `shape`, `shape_kwargs`, `font_path`, `font_index`, `font_size`,
`max_w_target` (largura antes de quebrar linha), `fill_color`/`text_color`/`shadow_color`
(RGBA), `border_color` (`null` = sem borda), `border_px`.

Rotação (`--rotation-deg`) e escala de saída (`--out-scale`) ficam fora do config JSON de
propósito - são parâmetros de POSICIONAMENTO no vídeo final (dependem de onde/como o overlay
vai ser usado), não de identidade visual da marca.

Via import (controle fino, mesma função usada pelo CLI):
```python
from build_overlay import render_overlay
render_overlay("Exemplo", font_size=58, max_w_target=460,
                fill_color=(40,80,160,255), text_color=(255,255,255,255),
                border_color=(255,255,255,255), border_px=10,
                rotation_deg=-9, out_scale=1.2, out="overlay.png")
```

## Regras de design

1. **Borda precisa de padding na máscara ANTES de dilatar, não depois.** A silhueta de qualquer
   forma encosta nas bordas do array que a desenha (retângulo ocupa a largura/altura inteira do
   canvas). Dilatar (`scipy.ndimage.distance_transform_edt`) sem primeiro dar `np.pad()` na
   máscara corta a borda exatamente nos trechos retos/onde a silhueta toca o array - bug real
   encontrado em produção (2026-08-19), sobreviveu a uma primeira correção (trocar dilatação
   quadrada por euclidiana) porque essa primeira correção resolveu só a FORMA da dilatação, não
   a falta de espaço no array. `dilate_uniform()` sempre retorna uma imagem maior que a entrada
   (+2×px em cada dimensão) por causa disso - o código que a chama tem que ajustar a posição de
   colagem de acordo (nunca assumir que a máscara dilatada tem o mesmo tamanho da original).
2. **Nunca hardcodar valor de identidade visual real neste repo público.** Cor, fonte, texto e
   qualquer outro valor de marca ficam num JSON privado fora do repo (mesma regra da skill
   `legenda-estilizada`, ver `config_default.json` de lá pro raciocínio completo).
3. **Emoji é token, não decoração à parte.** Layout trata cada emoji como um item de largura
   própria dentro do fluxo de texto (via `tokenize()`), alinhado verticalmente pela altura de
   caixa-alta da fonte (`cap_h`) - colar emoji como afterthought depois do texto produz
   desalinhamento vertical visível.
4. **Canvas e composição derivam do tamanho REAL da máscara (`mask.size`), nunca de `(w, h)`
   calculado a priori.** Isso é o que permite formas plugáveis sem tocar no resto do pipeline -
   uma forma que precisa de mais espaço (rabicho, decoração) simplesmente retorna uma máscara
   maior, e tudo mais (sombra, borda, canvas final) se ajusta sozinho.
