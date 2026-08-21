---
name: avaliar-ideia
description: Avalia a utilidade real de uma ideia, ferramenta ou skill de terceiro (slide, post, Reddit/X, repositório de código) para qualquer ponto do processo/negócio ativo. Lê a fonte real (nunca marketing), gera o leque de oportunidades antes de filtrar por risco, separa risco em eixos (segurança, jurídico, ToS de plataforma), e dá veredito com esforço/custo. Oferece registrar em Claude Backlog se aprovada.
user-invocable: true
---

# Avaliar Ideia

Avalia se uma ideia, ferramenta ou skill que alguém compartilhou (slide, link de Reddit/X/GitHub, texto colado) vale a pena adotar em algum ponto do processo/negócio ativo. Não é brainstorm livre nem parecer técnico solto — é um processo de duas passadas em ordem fixa, porque inverter a ordem poda ideia boa antes dela aparecer.

## 0. Ler a fonte real, nunca o resumo ou o marketing

**Regra dura, já quebrada uma vez e corrigida pelo usuário:** avaliar o objeto real, não a descrição dele.

- **Link de repositório/skill (GitHub etc.):** localizar e ler o código-fonte de verdade antes de opinar. Nunca julgar pelo README, pitch ou marketing — pode ter algo genial (ou um problema grave) que só aparece no código.
- **Link de Reddit/X/artigo:** abrir o link real (WebFetch/leitura de página), não confiar só no texto que a pessoa colou — thread e comentários podem mudar a leitura.
- **Slide/screenshot:** ler visualmente, extrair a ideia central. Ignorar o quão bem produzido o slide é — isso não é sinal de qualidade da ideia.
- **Texto colado direto:** usar como está, mas checar se há link embutido que vale abrir.

Se a fonte citar número, resultado ou case ("aumentou X%", "validado por Y"), tratar como alegação a verificar, não fato — buscar a fonte primária se for decisivo pro veredito.

## 1. Passada 1 — leque de oportunidades, sem filtro de risco ainda

Objetivo: não deixar risco/custo podar uma ideia genial antes de ela ser mapeada por inteiro.

- **Contexto do negócio/processo ativo:** em que pipeline isso pode entrar (conteúdo, copy, tráfego, vídeo, CRM/leads, páginas, atendimento etc. — usar o que já existe no produto/projeto ativo como referência, não inventar categoria nova sem checar primeiro).
- **Cenário ideal:** se essa ideia funcionar 100%, o que ela substitui ou resolve? Nomear a alternativa concreta que já estava cotada ou em uso, se houver (ex: "isso substituiria a ferramenta X que eu já pago" é mais forte que "isso parece útil").
- **Além do pedido original:** que outros usos, adjacentes ao que a pessoa que compartilhou tinha em mente, isso abre no negócio? Ser exaustivo, criativo, completo — é aqui que se ganha ou perde a avaliação, não na parte de risco.
- **Pesquisar se necessário:** se faltar contexto de mercado, fluxo ou case real pra avaliar direito, buscar (WebSearch/WebFetch) em vez de chutar.

## 2. Passada 2 — filtro, aplicado por cima do leque da passada 1

Nunca fazer esta parte primeiro.

- **Redundância:** compara com o que já existe no processo — é upgrade real, é redundante com algo que já cobre isso, ou preenche gap genuíno? Nomear a skill/ferramenta irmã se houver.
- **Esforço e viabilidade:** tempo pra adotar/adaptar, dependência externa, custo de API (se em USD, converter BRL aproximado). Se a decisão for "essa ferramenta OU uma alternativa já cotada", usar os 4 critérios: qualidade, esforço, viabilidade, custo.
- **Risco — três eixos separados, nunca um "risco" genérico misturado:**
  - **Segurança/dados:** exposição de credencial, PII, exfiltração.
  - **Jurídico/regulatório:** LGPD, direitos autorais, compliance específico do nicho.
  - **ToS de plataforma:** automação/scraping em Meta (Instagram/Facebook/WhatsApp) e afins — risco de suspensão de conta é **eliminatório sozinho**, nunca entra como trade-off aceitável junto com os outros dois eixos.
- **Existe risco inadmissível?** Declarar explicitamente se algum dos três eixos acima, sozinho, já mata a ideia — não deixar implícito dentro de um parágrafo de trade-offs.
- **Corner cases:** situação em que a ideia parece boa mas quebra (volume, escala, dependência de terceiro instável, mudança de política da plataforma).

## 3. Veredito

Uma linha por critério, depois:

**Adotar** / **Adaptar** (útil, mas precisa mudança antes de usar) / **Vigiar** (não agora — falta maturidade, preço vai cair, esperar validação) / **Descartar** — com justificativa em 1-2 linhas.

Resposta final **concisa por padrão**: entregar o veredito e o essencial de cada passada, não o raciocínio completo. Aprofundar qualquer seção só se pedido depois.

## 4. Registro se aprovada

Se o veredito for **Adotar** ou **Adaptar**, oferecer (não fazer sem confirmar) salvar uma entrada em `Claude Backlog/Ideias Avaliadas.md`, formato:

```markdown
- [ ] **{{nome da ideia}}** — {{veredito}}, encaixa em {{ponto do processo}}
  - Fonte: {{link ou origem}}
  - Por quê: {{1 linha, a partir da passada 1}}
  - Próximo passo: {{ação concreta pra implementar}}
```

Se **Vigiar** ou **Descartar**, não registrar — fica só na conversa, a menos que o usuário peça explicitamente pra guardar o motivo do descarte (ex: pra não reavaliar a mesma ideia depois).
