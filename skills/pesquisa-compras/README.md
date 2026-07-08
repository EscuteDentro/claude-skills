# Skill: /pesquisa-compras

Assistente de compras multi-plataforma para o Claude Code.

**Status:** funcional — melhorias pendentes (ver abaixo).

---

## O que faz

Pesquisa preços em Mercado Livre, Shopee, Amazon, Magazine Luiza e Estante Virtual (livros). Inclui pré-pesquisa de reviews e alternativas, frete estimado para o CEP configurado, parcelamento sem juros, cupons e flag de envio internacional com estimativa de imposto.

## Configurar antes de usar

Editar `SKILL.md` e substituir:
- `{SEU_CEP}` pelo seu CEP (para cálculo de frete)
- `{SUA_CIDADE}` pela sua cidade (para encartes de supermercado via Tiendeo)

## Como instalar

1. Copiar esta pasta para `.claude/skills/pesquisa-compras/` no projeto
2. Criar `.claude/commands/pesquisa-compras.md`:

```
---
name: pesquisa-compras
description: Pesquisa preços multi-plataforma com comparação, frete e encartes
allowed-tools: Read, Write, Bash, WebSearch
---

Executar a skill `pesquisa-compras` seguindo o SKILL.md localizado em
`.claude/skills/pesquisa-compras/SKILL.md`.
```

3. Invocar com `/pesquisa-compras` no Claude Code.

## Melhorias pendentes

- Scripts Python externos (`buscar.py`, `gerar-html.py`) precisam ser copiados manualmente
- Mercado Livre requer autenticação OAuth prévia
- Scraping de algumas plataformas é instável
- Sem testes automatizados
