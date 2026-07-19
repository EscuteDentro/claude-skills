---
name: animacao-video
description: Transforma uma narração já gravada (roteiro + áudio) em vídeo animado (motion graphics em camadas, estilo claymation ou outro) via Remotion, com legendas sincronizadas por timestamp real de palavra.
user-invocable: true
---

> **Instalação:** copiar esta pasta para `.claude/skills/animacao-video/` no projeto, copiar
> `scripts/` e `remotion-lib/` junto (não ficam de fora — são parte da skill, não algo pra
> gerar de novo do zero). Criar o command apontando pra este SKILL.md. Ver
> [README.md](./README.md) para instruções completas de instalação.

---

# animacao-video

Pega uma narração já gravada (sua própria voz, sem depender de clonagem de voz por IA) e um
roteiro, e monta um vídeo animado em Remotion: imagens geradas por IA num estilo visual
consistente, compostas em camadas com movimento de câmera e animação simples (sem precisar de
geração de vídeo por IA, que é caro e não confiável para múltiplas cenas consistentes).

## Por que essa arquitetura (e não outra)

Existem 3 níveis de complexidade pra animar uma imagem parada, em ordem de custo:

| Nível | Técnica | Custo por vídeo | Quando usar |
|---|---|---|---|
| 1 | Ken Burns puro (câmera se move sobre 1 imagem parada) | Só a imagem, ~$0,02–0,07/asset | Cena contemplativa, sem elementos separados |
| **2** | **Motion graphics em camadas** (várias imagens com fundo transparente, cada uma animada por código — entra com mola, desliza, gira, some) | **Idem, só mais assets (~10-15/vídeo)** | **Este skill. Bom equilíbrio custo x dinamismo.** |
| 3 | Vídeo gerado por IA (Kling, Runway, etc — o objeto se move de verdade) | ~$0,04–0,11/segundo gerado, geralmente precisa de 2-3 tentativas por plano | Só quando movimento orgânico real é indispensável (ex: personagem andando) |

Na prática, o Nível 3 custou ~R$40-100 por vídeo de 60-90s no teste que originou este skill
(pela quantidade de gerações descartadas), contra ~R$3-5 do Nível 2. A steady-cam giratória +
zoom + elementos entrando/saindo já entrega bastante sensação de movimento pro custo — vale
testar Nível 2 antes de pular pro Nível 3.

## Pré-requisitos

- Conta no [fal.ai](https://fal.ai) com créditos, variável `FAL_KEY` no ambiente ou num `.env`
- `ffmpeg` instalado (`brew install ffmpeg`) — usado pra remoção de fundo e diagnóstico, evita
  depender de Pillow/Python (ver nota abaixo)
- `whisper` (pacote Python `openai-whisper`, **não** `whisper.cpp`) — só se for usar legenda
  sincronizada por palavra
- Node.js + npm — pro Remotion
- Áudio de narração já gravado e (se necessário) editado, sem trilha/efeitos ainda

**Por que ffmpeg em vez de Pillow para recorte de fundo:** em ambientes onde `pip install
Pillow` falha (ex: incompatibilidade entre versão do Python e libs de sistema), `ffmpeg` com o
filtro `colorkey` resolve o mesmo problema sem dependência de Python nenhuma. Ver
`scripts/remover_fundo.sh`.

---

## Fase 0 — Definir o estilo visual (âncora)

Antes de gerar qualquer asset, escrever um bloco de texto (em inglês, os modelos respondem
melhor) que descreve o estilo visual e que vai ser **reaproveitado em TODAS as gerações**:
material, textura, paleta de cor, iluminação. Isso é o que mantém a biblioteca de assets
coerente entre si — sem isso cada imagem gerada parece de um projeto diferente.

Exemplo (estilo claymation usado no projeto que originou este skill):
```
Claymation / stop-motion animation style, everything sculpted from soft plasticine modeling
clay, visible fingerprint and clay-tool texture, matte non-glossy clay finish, warm saturated
pastel color palette, warm soft studio lighting, gentle rim light. Vertical 9:16 aspect. No
text, no watermark, no logo.
```

## Fase 1 — Personagem (se houver)

Se o vídeo tem um personagem recorrente, ele é o asset mais reaproveitado (normalmente aparece
em várias cenas) — vale iterar mais nele antes de seguir, porque qualquer defeito se propaga
pra tudo que vem depois.

1. Gerar com `scripts/gerar_asset.py --ref foto1.jpg --ref foto2.jpg ... --prompt "..."`,
   passando 2-4 fotos de referência reais da pessoa/personagem
2. **Se o resultado sair parecido demais com a foto original** (sem estilizar): o endpoint de
   edição (`/edit`) tende a preservar a imagem original quase intacta a menos que o prompt seja
   muito explícito. Reforçar no prompt: *"DO NOT edit or retouch the reference photos. DO NOT
   output a photograph. This is a complete re-creation from scratch as a [seu estilo]"* — essa
   framing anti-fotorrealismo foi o que resolveu na prática.
3. Aprovar a pose/estilo antes de seguir. Esse PNG aprovado vira o personagem fixo — **não
   gerar de novo em cada cena** (cada geração é independente, não hà "memória" entre chamadas;
   reaproveitar o mesmo arquivo com transformações CSS é o que garante consistência visual).
4. Remover o fundo (`scripts/remover_fundo.sh`) pra poder compor o personagem sobre qualquer
   fundo depois.

## Fase 2 — Biblioteca de assets de apoio

Listar as cenas do roteiro e, pra cada uma, os elementos visuais separados que ela precisa
(fundo, props, ícones). Gerar cada um com `scripts/gerar_asset.py --prompt "..."` (sem `--ref`,
sempre incluindo o bloco de estilo da Fase 0 + descrição do objeto específico).

**Erros comuns de prompt e como evitar:**

- **Lista longa de negações** ("NOT X, NOT Y, NOT Z, NOT W...") pode fazer o modelo falhar a
  geração inteira (erro "did not generate the expected output"). Preferir framing positivo
  quando possível; usar negação só pro ponto que realmente precisa.
- **Palavras com associação forte e inesperada**: pedir um "glow/aura" abstrato pode virar uma
  criatura com asas (o modelo associa "aura" a personagem fantástico); pedir "macro/close-up
  blur" pode virar um objeto esférico definido em vez de bokeh abstrato. Testar o resultado,
  reescrever evitando a palavra-gatilho, não insistir no mesmo prompt.
- **Fundo perto do tom do sujeito** (ex: fundo bege pedido pra ficar perto de pele): sempre que
  pedir fundo sólido pra depois recortar, pedir explicitamente **verde puro tipo chroma-key**,
  nunca uma cor "neutra" — cores neutras colidem com tons de pele/roupa e o recorte come parte
  do sujeito.
- **Elementos com sentido de "leveza/positivo" x "peso/negativo"**: se o roteiro pede uma
  sensação leve (ex: "pensamentos soltando", "alívio"), especificar cor pastel clara e
  movimento ascendente no prompt — o oposto (tons escuros, formato de nuvem de tempestade) lê
  como negativo/ameaçador mesmo sem essa intenção.

## Fase 3 — Transcrição com timestamp por palavra

```bash
sh scripts/transcrever.sh audio/narracao.mp3 pt audio/
```

Gera `audio/narracao.json`. **Não usar o texto do whisper como legenda** — ele erra grafia e
pontuação. Usar só os `start`/`end` de cada palavra, mapeados por posição pro texto correto do
roteiro. Ao reconciliar:

- O whisper às vezes ouve "porque" como duas palavras ("por que") ou insere palavras extras
  ("eu", conectivos) que não estão no roteiro — quando isso acontece, funda os tokens extras no
  vizinho mais próximo (soma o intervalo de tempo) em vez de tentar re-alinhar tudo.
- Contar as palavras do roteiro e do whisper por trecho (frase a frase) antes de aceitar o
  mapeamento — se as contagens não baterem, tem token sobrando/faltando pra resolver.
- Ver `remotion-lib/helpers.tsx` (`TimedWord`, `buildGroups`) pro formato de dados esperado.

**Se for editar o áudio depois de transcrever** (cortar uma pausa, aparar o início/fim): a
transcrição inteira fica desatualizada a partir do ponto do corte, não dá pra só subtrair um
delta fixo dos timestamps porque a re-transcrição pode segmentar diferente. Reeditar o áudio
primeiro, depois rodar a transcrição de novo do zero.

## Fase 4 — Remoção de fundo em lote

Pra cada asset que vai ser composto em camada (não os fundos de tela cheia):
```bash
sh scripts/remover_fundo.sh asset-bruto.png asset-final.png
```
Ver comentários no próprio script pros parâmetros calibrados e o que fazer se sobrar franja.

## Fase 5 — Composição no Remotion

1. Criar o projeto: `npx create-video@latest --yes --blank --no-tailwind video`
2. `cd video && npm i`
3. Copiar `remotion-lib/helpers.tsx` para `video/src/helpers.tsx`
4. Copiar os assets pra `video/public/assets/` e o áudio pra `video/public/`
5. Escrever a composição principal seguindo `remotion-lib/exemplo-composicao.tsx` como
   esqueleto: fronteiras de cena em frames (a partir da Fase 3), um componente por cena
   compondo os assets com os helpers, `<Captions groups={...} />` por cima de tudo

**Testar cena por cena com `npx remotion still` antes do render completo.** Renderizar o vídeo
inteiro pra checar um detalhe é lento; um frame estático de uma cena específica (`--frame=N`)
mostra o mesmo problema em segundos.

```bash
npx remotion still src/index.ts <CompositionId> out/teste/frame.png --frame=100 --scale=0.4
npx remotion render src/index.ts <CompositionId> out/final.mp4
```

**Iteração visual barata — 4 práticas, aplicar sempre:**

1. **Calcular antes de renderizar.** Antes de chutar posição/escala, fazer a conta (campo de
   visão da câmera × distância = extensão visível na tela, por exemplo) e só então renderizar
   com um valor estimado, não um palpite. Cada render+inspeção visual tem custo real; um chute
   errado custa uma rodada inteira à toa.
2. **Lotes maiores por rodada.** Agrupar 2-3 ajustes relacionados antes de renderizar e olhar,
   em vez de 1 mudança → 1 render → 1 olhada → repetir.
3. **`--scale` baixo durante calibração, full-res só na entrega.** `out/teste/` pra
   stills/renders descartáveis de calibração (não versionar), nome final direto em `out/` pro
   resultado real.
4. **Isolar iteração pesada do fio principal da conversa** quando disponível (ex: um agente
   fork) — o ruído de várias tentativas de calibração não precisa poluir o histórico principal,
   só o resultado final importa lá.

**Parallax por profundidade (default recomendado, não só decoração):** sem isso, o fundo dá
zoom (Ken Burns) mas os elementos em camada (props, ícones) ficam com tamanho fixo a cena
inteira — só o fundo parece ter profundidade. Passar `depth` (0 a 1) e `totalFrames` pro
`PopIn` de cada elemento faz ele ganhar escala extra proporcional a quão "perto da câmera" ele
está, sincronizado com o mesmo progresso de frame do fundo. Vale usar como prática padrão em
qualquer cena com 2+ elementos em camadas diferentes, não só quando quiser um efeito especial.

## Fase 6 — Loop e capa (se for pra Reels/Shorts)

Duas coisas que fazem diferença pra retenção/algoritmo:

- **Loop sem quebra visual**: se o vídeo vai repetir automaticamente, deixar o último frame o
  mais parecido possível do frame 0 (mesmo enquadramento, mesma posição de elementos-chave) pra
  o corte de repetição ser imperceptível. E cortar qualquer silêncio residual no fim do áudio —
  terminar exatamente no fim da última palavra falada, não alguns frames depois.
- **Capa embutida no frame 0**: a maioria das plataformas não deixa subir uma imagem de capa
  separada com facilidade. Fazer o frame 0 já conter o texto-gancho completo (não uma
  revelação progressiva) resolve isso sem precisar de asset separado.

## Extra — legenda com glifos de massinha reais (em vez de CSS)

Testado e validado no título de capa de um vídeo real: em vez de simular "letra de massinha"
com CSS (`CLAY_TEXT_STYLE`, contorno grosso + sombra em camadas), usar **letras de verdade**,
geradas no mesmo estilo visual do resto do vídeo e recortadas uma a uma. Ficou visualmente mais
integrado que o CSS — lê como parte da mesma cena, não como texto sobreposto.

**Como gerar a folha de origem** (pedir a uma IA de imagem, ex: ChatGPT):
- Fundo **100% sólido** (preto ou branco), sem vinheta/gradiente — condição obrigatória pro
  recorte automático funcionar. Fundo com textura/vinheta (aconteceu nas 2 primeiras tentativas
  antes de acertar) faz o recorte falhar ou sair inconsistente.
- Conjunto de caracteres enxuto primeiro (minúsculas + diacríticos do idioma + números +
  pontuação básica, sem maiúsculas se o estilo de legenda for caixa-baixa) — mais barato de
  testar, ampliar depois se funcionar.
- Letras sem se tocar/sobrepor.

**Recorte**: `scripts/recortar_alfabeto.py` — 100% local (ffmpeg + Python stdlib, sem API, sem
Pillow). Detecta cada glifo por projeção linha/coluna (linhas de pixel com "tinta" = uma linha
de texto; colunas com tinta dentro de cada linha = um glifo), recorta e converte o fundo em
transparência. Gera `glifos.json` com largura/altura de cada caractere recortado — necessário
porque letras de massinha não são monoespaçadas, e a altura do recorte varia um pouco entre
linhas da folha original (compensar escalando cada glifo pra uma altura de linha alvo comum,
não usar a altura nativa do recorte direto).

**Tipografia** (componente `GlyphText` em `helpers.tsx`): compõe um texto com os glifos
recortados, escalando cada um pra uma altura alvo comum e quebrando linha automaticamente pra
caber numa largura máxima — cada linha centralizada. Usar `--scale` baixo (ver seção de
iteração barata acima) ao calibrar `targetHeight`/`maxWidthPx`, o ajuste fino de quantas linhas
cabem é por tentativa.

---

## Resumo de arquivos desta skill

```
animacao-video/
  SKILL.md                       este arquivo
  README.md                      instalação e configuração
  scripts/
    gerar_asset.py                fal.ai nano-banana — texto->imagem ou edição c/ referência
    remover_fundo.sh              ffmpeg colorkey — recorte de fundo sem Pillow
    transcrever.sh                whisper --word_timestamps — timing real por palavra
  remotion-lib/
    helpers.tsx                   componentes Remotion reutilizáveis (Ken Burns, PopIn, etc)
    exemplo-composicao.tsx        esqueleto de uso, conteúdo fictício
```
