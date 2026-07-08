# Guia de Construção de Landing Pages — Template Universal

Template completo para construir, publicar e manter landing pages de alta performance com Meta Pixel, CAPI server-side, Design System e deploy no Vercel.

## Arquivos

| Arquivo | O que é |
|---|---|
| **[Guia de Construção da Página.md](./Guia%20de%20Construção%20da%20Página.md)** | Guia completo: tracking, performance, SEO/AEO, LGPD, deploy, testes A/B |
| **[Design-System-decisoes.md](./Design-System-decisoes.md)** | Decisões fechadas de design: cores, tipografia, componentes, performance |
| **[design-system.json](./design-system.json)** | Tokens visuais completos em JSON — paleta, tipografia, espaçamento, componentes |

## Skills para Claude Code

| Skill | O que faz | Status |
|---|---|---|
| `/subir-pagina-top` | LP de infoproduto do zero ao ar: Guia, DS, Pixel + CAPI, deploy no Vercel | ✅ Pronto para uso |
| `/pesquisa-compras` | Pesquisa de preços multi-plataforma com comparação e fretes | ⚠️ Funcional — precisa de melhorias |

Ver `skills/` para instruções de instalação de cada skill.

## Como usar

1. Copiar os arquivos para o seu projeto
2. Substituir todos os valores de exemplo (marcados com `⬜` no Guia) pelos dados do seu produto
3. Para o `design-system.json`: ajustar tokens de cor e tipografia para sua identidade visual
4. Para os skills: copiar pasta de `skills/nome-da-skill/` para `.claude/skills/` do seu projeto

## Contribuindo / atualizando este repo

Após clonar, rodar uma vez:

```bash
sh setup.sh
```

Isso instala um pre-commit hook que **bloqueia automaticamente qualquer commit com dados pessoais** (e-mails, caminhos de sistema, IDs de pixel, etc.). O repo deve permanecer 100% agnóstico — o hook impede que dados pessoais entrem por acidente.
