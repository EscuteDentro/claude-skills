# claude-skills

Skills prontos para instalar no [Claude Code](https://claude.ai/code) — construídos para builders de infoprodutos.

---

## Skills

| Skill | O que faz | Status |
|---|---|---|
| [`/subir-pagina-top`](./skills/subir-pagina-top/) | LP de infoproduto do zero ao ar: Guia, DS, Pixel + CAPI, deploy no Vercel | ✅ Pronto |
| [`/pesquisa-compras`](./skills/pesquisa-compras/) | Pesquisa de preços multi-plataforma com comparação, frete e encartes | ⚠️ Funcional — melhorias pendentes |
| [`/animacao-video`](./skills/animacao-video/) | Narração gravada → vídeo animado (motion graphics em camadas) via Remotion, com legenda sincronizada por palavra | ✅ Pronto |

Cada pasta de skill tem um `README.md` com o que faz, como instalar e o que configurar.

---

## Referências — LP de Infoproduto

Documentação de arquitetura e decisões para construir LPs de alta conversão:

| Arquivo | Conteúdo |
|---|---|
| [`Guia de Construção da Página.md`](./Guia%20de%20Construção%20da%20Página.md) | Tracking, performance, SEO/AEO, LGPD, deploy, testes A/B — guia completo |
| [`Design-System-decisoes.md`](./Design-System-decisoes.md) | Decisões fechadas de design: cores, tipografia, componentes, cache, headers |
| [`design-system.json`](./design-system.json) | Tokens visuais completos em JSON — paleta, tipografia, espaçamento, componentes |

Estes arquivos vêm preenchidos com valores de exemplo — substituir pelos dados do seu produto onde indicado (`⬜`).

---

## Como instalar um skill

1. Copiar a pasta do skill para `.claude/skills/<nome>/` no seu projeto
2. Criar `.claude/commands/<nome>.md` com o frontmatter apontando para o SKILL.md (ver README de cada skill)
3. Invocar com `/<nome>` no Claude Code

---

## Contribuindo / atualizando este repo

Após clonar, rodar uma vez:

```bash
sh setup.sh
```

Instala um pre-commit hook que bloqueia qualquer commit contendo dados pessoais. O repo é 100% agnóstico — o hook impede contaminação por acidente.
