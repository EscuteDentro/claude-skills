# Skill: /subir-pagina-top

Publica uma landing page de infoproduto (Hotmart, Kiwify, etc.) no Vercel com Meta Pixel + CAPI server-side embutidos: tracking é parte obrigatória do deploy, não etapa opcional.

**Status:** funcional e pronto para uso.

## O que faz

Conduz o processo completo de publicação de uma LP de conversão em 10 passos:

1. Definição da pasta do projeto
2. Referência visual (URL ou 3 perguntas)
3. Coleta de configuração (Pixel ID, checkout URL, preço, etc.)
4. Criação da pasta de destino
5. Geração do `Guia de Construção da Página.md`
6. Geração do `design-system.json` com paleta derivada da referência
7. Checklist de responsividade (mobile-first, 390px)
8. Checklist de performance (Lighthouse mobile ≥ 90)
9. **Infraestrutura de deploy e tracking** (tudo embutido):
   - `vercel.json` com headers de segurança HTTP e cache policy
   - Deploy por push no `main` (Vercel Git) ou Vercel CLI; nunca API REST com bundle local
   - Meta Pixel snippet base
   - Eventos por tipo de página (vendas, captura, obrigado)
   - `api/capi.js`: CAPI server-side com SHA-256, normalização E.164, deduplicação
   - Helpers JS (`_cId`, `_ck`, `_capi`, `_app_eid`, `_app_pii`)
   - Microsoft Clarity custom tags (opcional)
   - VSLProgress via YouTube IFrame API
   - ScrollDepth70 listener
   - Medição própria e saúde: `api/m.js` (contador anônimo e funil), `api/tracking-health.js`, `api/selfcheck.js`, `api/monitor-status.js`, `api/_lib/redis.js`
10. Preview da paleta + orientações finais

## Por que o Pixel está embutido

Para uma LP de infoproduto, o Meta Pixel + CAPI não é opcional: sem tracking, o Meta Ads Manager não consegue otimizar campanhas e o Event Match Quality (EMQ) fica baixo. O skill trata o tracking como parte do checklist de "página publicável", não como etapa separada.

## Configurar antes de usar

No `api/capi.js` gerado pelo skill, substituir:
- `SEU_PIXEL_ID` pelo ID do seu Meta Pixel
- `https://SEU-DOMINIO.com` pela URL canônica da sua LP
- Configurar a variável de ambiente `META_CAPI_KEY` no Vercel (Settings → Environment Variables → tipo Sensitive)

No HTML da página, substituir `SEU_PIXEL_ID` pelo mesmo ID.

## Como instalar no Claude Code

1. Copiar `SKILL.md` para `.claude/skills/subir-pagina-top/SKILL.md` no seu projeto
2. Criar `.claude/commands/subir-pagina-top.md`:

```
---
name: subir-pagina-top
description: Publica LP de infoproduto no Vercel com Pixel + CAPI, domínio, headers e SEO
allowed-tools: Read, Write, Edit, Bash
---

Executar a skill `subir-pagina-top` seguindo o SKILL.md localizado em
`.claude/skills/subir-pagina-top/SKILL.md`.
```

3. Invocar com `/subir-pagina-top` no Claude Code.
