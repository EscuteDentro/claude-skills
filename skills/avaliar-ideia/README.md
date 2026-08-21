# Skill: /avaliar-ideia

Avaliador de ideias, ferramentas e skills de terceiros para o Claude Code.

**Status:** pronto.

---

## O que faz

Quando alguém compartilha uma ideia, ferramenta ou skill (slide, post de Reddit/X, link de repositório no GitHub, texto colado), essa skill avalia se vale a pena adotar em algum ponto do seu processo ou negócio.

Regras centrais:
- Sempre lê a fonte real (código-fonte de um repo, o link de verdade de um post) — nunca julga pela descrição ou pelo marketing.
- Processo em duas passadas na ordem certa: primeiro gera o leque completo de oportunidades sem filtro, só depois aplica risco/custo/corner cases — inverter a ordem poda ideia boa antes dela aparecer.
- Risco sempre separado em três eixos (segurança/dados, jurídico/regulatório, ToS de plataforma) em vez de um "risco" genérico misturado.
- Termina em veredito claro: Adotar / Adaptar / Vigiar / Descartar.

## Como instalar

1. Copiar esta pasta para `.claude/skills/avaliar-ideia/` no seu projeto
2. Criar `.claude/commands/avaliar-ideia.md`:

```
---
name: avaliar-ideia
description: Avalia utilidade real de uma ideia/ferramenta/skill de terceiro para o seu processo
allowed-tools: Read, Write, WebSearch, WebFetch
---

Executar a skill `avaliar-ideia` seguindo o SKILL.md localizado em
`.claude/skills/avaliar-ideia/SKILL.md`.
```

3. Invocar com `/avaliar-ideia` no Claude Code, colando o link, texto ou imagem a avaliar.

## Configurar antes de usar

Nenhuma configuração obrigatória — a skill lê o contexto do produto/projeto ativo dinamicamente. Se quiser registrar ideias aprovadas em um backlog, criar um arquivo (ex: `Backlog/Ideias Avaliadas.md`) e ajustar o caminho na seção "Registro se aprovada" do `SKILL.md`.
