# Skill: /animacao-video

Transforma uma narração já gravada (roteiro + áudio, sua própria voz) em vídeo animado com
Remotion — motion graphics em camadas (Ken Burns + elementos entrando/saindo), legendas
sincronizadas por timestamp real de palavra, sem depender de geração de vídeo por IA.

**Status:** funcional, testado ponta a ponta num vídeo real de ~67s (11 cenas, 1 personagem
recorrente, 11 assets de apoio, legendas sincronizadas, capa embutida no frame 0).

## O que faz

Cobre o fluxo completo: definição de estilo visual consistente → geração de personagem a
partir de fotos de referência → geração da biblioteca de assets de apoio (fundos, props) →
transcrição do áudio com timestamp por palavra → remoção de fundo em lote → composição em
Remotion com biblioteca de componentes reutilizáveis (Ken Burns ancorado, entrada com mola,
flutuação, oclusão de primeiro plano, legendas com reveal palavra-a-palavra) → render.

Ver [SKILL.md](./SKILL.md) para o passo a passo completo, incluindo a tabela de decisão de
custo (por que motion graphics em camadas em vez de vídeo gerado por IA) e os erros de prompt
mais comuns já mapeados (o que NÃO pedir pro gerador de imagem, e por quê).

## Por que existe

Gerar vídeo animado com IA "de verdade" (o objeto se movendo, tipo Kling/Runway) custou ~10-20x
mais caro no teste que originou este skill, pela quantidade de gerações descartadas por
inconsistência de personagem entre cenas. Motion graphics em camadas (imagens paradas + câmera
+ animação simples via código) chega perto do resultado visual por uma fração do custo, e cada
peça é 100% controlável (não depende de a IA "acertar" o movimento).

## Configurar antes de usar

- Conta no [fal.ai](https://fal.ai), variável `FAL_KEY` no ambiente ou num `.env` no diretório
  onde os scripts forem rodados
- `ffmpeg` instalado (`brew install ffmpeg`)
- `openai-whisper` instalado (`pip install openai-whisper`) se for usar legenda sincronizada
- Node.js + npm, pro Remotion

Nenhum placeholder de conta/produto pra substituir — os scripts e componentes são agnósticos,
não têm nada hardcoded de um projeto específico.

## Como instalar no Claude Code

1. Copiar a pasta inteira (`SKILL.md`, `README.md`, `scripts/`, `remotion-lib/`) para
   `.claude/skills/animacao-video/` no seu projeto
2. Criar `.claude/commands/animacao-video.md`:

```
---
name: animacao-video
description: Transforma narração gravada em vídeo animado (motion graphics em camadas) via Remotion
allowed-tools: Read, Write, Edit, Bash
---

Executar a skill `animacao-video` seguindo o SKILL.md localizado em
`.claude/skills/animacao-video/SKILL.md`.
```

3. Invocar com `/animacao-video` no Claude Code.

## Melhorias pendentes

- Testado só com o modelo `fal-ai/nano-banana`. Modelos mais novos (nano-banana-2/pro) podem
  dar resultado melhor pelo mesmo fluxo, não testado ainda.
- A geração de personagem (Fase 1) às vezes precisa de 2-3 tentativas de prompt até acertar
  pose/estilo — não tem como garantir sucesso na primeira tentativa, é iterativo por natureza.
- Sem suporte a múltiplos personagens interagindo na mesma cena (o fluxo assume 1 personagem
  central reaproveitado).
- `remover_fundo.sh` calibrado por tentativa e erro (não é uma fórmula matemática fechada) —
  pode precisar de ajuste fino nos parâmetros de similaridade conforme o asset.
