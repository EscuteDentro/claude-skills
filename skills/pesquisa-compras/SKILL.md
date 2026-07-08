---
name: pesquisa-compras
description: Assistente de compras com pré-pesquisa, comparação de preços multi-plataforma, frete, parcelamento, cupons e encartes de supermercado.
user-invocable: true
---

> **Instalação:** copiar esta pasta para `.claude/skills/pesquisa-compras/` no projeto e criar o command apontando para o SKILL.md. Configurar `{SEU_CEP}` e `{SUA_CIDADE}` antes de usar. Ver [README.md](./README.md) para instruções completas.

---

# Pesquisa de Compras

**Restrição absoluta:** NUNCA efetuar compra, NUNCA navegar para carrinho, checkout ou pagamento.

Scripts:
- `buscar.py` — busca Apify + SerpAPI + Estante Virtual → JSON
- `gerar-html.py` — JSON → HTML visual

CEP padrão: {SEU_CEP} ({SUA_CIDADE})

**USD → BRL:** sempre mostrar estimativa em real ao lado de qualquer valor em dólar.
Ex: "custo estimado ~USD 0.09 (~R$ 0,52)". Cotação obtida via AwesomeAPI e incluída no JSON.

---

## Etapa 1 — Pré-pesquisa

Quando o usuário mencionar o produto, ANTES de fazer qualquer pergunta:

1. Fazer 2–3 WebSearches:
   - `"[produto] review brasil 2026"`
   - `"[produto] problemas reclamação"`
   - `"alternativas [produto] comparação"`

2. Apresentar ao usuário:

```
📋 O que encontrei sobre [produto]

**Pontos-chave para avaliar:**
- [ponto 1 específico da categoria]
- [ponto 2]
- [ponto 3]

**Reclamações comuns:** [resumo honesto]

**Minha opinião:** [Claude emite recomendação direta]

**Alternativas a considerar:**
- [Alt A] — [diferença principal]
- [Alt B] — [diferença principal]

Quer que eu inclua alguma alternativa na comparação de preços?
```

---

## Etapa 1.5 — Vale encarte? (somente categoria mercado)

**Quando acionar:** produto é alimento, bebida, limpeza, higiene pessoal, pet food, laticínio, carne, frios ou padaria.

| Vale encarte | Não vale encarte | Verificar caso a caso |
|---|---|---|
| Alimentos em geral | Livros | Pilhas / velas |
| Bebidas | Eletrônicos | Utensílios domésticos básicos |
| Limpeza doméstica | Roupas / calçados | Artigos de papelaria |
| Higiene pessoal | Medicamentos (preço CMED) | Ferramentas simples |
| Pet food | Cosméticos de farmácia | — |
| Laticínios / frios / carnes | Suplementos | — |

Se o produto **vale encarte**, fazer WebSearch antes de acionar qualquer actor Apify:

```
"[produto]" encarte oferta supermercado brasília site:tiendeo.com.br
```

E também busca direta nas redes do DF:
```
"[produto]" oferta "asa norte" OR "brasília" atacadão OR carrefour OR nacional supermercados 2026
```

Apresentar achados de encarte **antes** da tabela de preços online, com:
- Nome do supermercado, preço, validade da oferta, link do encarte
- Comparação direta: "Online: R$X — Encarte [loja]: R$Y → diferença de R$Z (X%)"

Site principal: **Tiendeo {SUA_CIDADE}** → https://www.tiendeo.com.br/{sua-cidade}
Redes presentes no DF: Atacadão, Carrefour, Assaí, Fort Atacadista, Nacional, Big Box, Sam's Club, Oba Hortifruti.

Se não encontrar nada no Tiendeo via WebSearch, avisar e seguir para busca online normal.

---

## Etapa 2 — Refinamento

Após pré-pesquisa, perguntar com base na categoria detectada:

**Livro:** idioma (PT/EN/outro?), edição específica ou mais barata, condição (novo/usado/qualquer)
**Medicamento:** fabricante preferido, genérico aceitável?, dosagem, forma farmacêutica
**Suplemento:** certificação exigida (IFOS/MEG-3/NSF/outro?), origem (peixe/alga/krill?), dose por cápsula (EPA+DHA alvo), forma (cápsula/softgel/líquido), nacional ou importado aceitável, marca excluída por experiência anterior
**Eletrônico:** voltagem, versão nacional vs importado, novo/lacrado ou usado aceitável
**Roupa/tênis:** tamanho, colorway específico
**Mercado:** marca preferida ou aceita genérico?, quantidade/embalagem, orgânico ou convencional?
**Genérico:** condição (novo/usado/qualquer), prazo máximo aceitável

Perguntar separadamente: "Quer que eu busque também em AliExpress e Temu? (envio da China, 15–40 dias)"

Confirmar produto final antes de buscar.

---

## Etapa 3 — Descoberta de plataformas

Fazer WebSearch: `"[produto confirmado]" site:mercadolivre.com.br OR site:shopee.com.br OR site:amazon.com.br OR site:magazineluiza.com.br`

Anotar mentalmente quais plataformas apareceram. Montar o argumento `--plataformas` com apenas as relevantes.

Para livros: sempre incluir `estante` nas plataformas.
Para mercado: ML e Shopee têm alimentos/limpeza de atacarejo — vale incluir, mas o encarte (Etapa 1.5) tem prioridade.

---

## Etapa 4 — Dry-run (estimativa de custo)

```bash
python3.12 .claude/skills/pesquisa-compras/scripts/buscar.py \
  --produto "[PRODUTO]" \
  --plataformas "[ml,shopee,amazon,magalu,estante conforme descoberta]" \
  --cep {SEU_CEP} \
  --categoria "[livro|eletronico|medicamento|roupa|mercado|generico]" \
  --condicao "[novo|usado|qualquer]" \
  --dry-run
```

Apresentar estimativa ao usuário: "Estimativa: ~$X (~R$Y). Confirmar busca? [s/N]"
(BRL calculado com cotação do JSON — campo `usd_brl_rate`)

Aguardar confirmação antes de continuar.

---

## Etapa 5 — Busca real

Após confirmação:

```bash
python3.12 .claude/skills/pesquisa-compras/scripts/buscar.py \
  --produto "[PRODUTO]" \
  --plataformas "[plataformas]" \
  --cep {SEU_CEP} \
  --categoria "[categoria]" \
  --condicao "[condicao]" \
  --max-items 15 \
  [--intl se usuário aceitou internacional] \
  --output /tmp/pc_results.json
```

Se houver erro de timeout em alguma plataforma: continuar com as demais, avisar usuário.

---

## Etapa 6 — Cupons

Fazer WebSearch para cada plataforma que retornou resultados:
- `"cupom [loja] [produto] site:pelando.com.br 2026"`
- `"cupom [loja] site:promobit.com.br"`

Se encontrar cupom com data recente (últimos 7 dias):
Montar JSON de cupons: `[{"loja":"Shopee","codigo":"SHOP10","desconto":"R$10","fonte":"Pelando","data":"2026-06-16"}]`

Se não encontrar: usar `[]`

**Saída obrigatória de cupons (independente do HTML):**
Apresentar tabela com todos os cupons encontrados, mesmo os genéricos de plataforma:

| Loja | Código | Desconto | Requisito mínimo | Validade | Fonte |
|---|---|---|---|---|---|
| ML | CUPOM123 | 20% OFF | R$79 | 08/07 | Pelando |

Se nenhum código específico encontrado: informar cupons genéricos ativos da plataforma (ex: "ML tem cupom genérico de 20% OFF hoje via Pelando — verificar no app") com link da página de cupons da loja no Pelando.

---

## Etapa 7 — Gerar HTML e abrir

```bash
python3.12 .claude/skills/pesquisa-compras/scripts/gerar-html.py \
  --input /tmp/pc_results.json \
  --output "$HOME/seuprojeto/pesquisa-compras/[slug-produto].html" \
  --cupons '[CUPONS_JSON_AQUI]'
```

```bash
open "$HOME/seuprojeto/pesquisa-compras/[slug-produto].html"
```

---

## Etapa 8 — Análise final

Após apresentar o HTML, comentar:

1. **Encarte vs online** (se categoria mercado): quanto se economiza indo ao supermercado físico
2. **Melhor compra nacional:** qual produto, por quê, considerando total + prazo + confiabilidade
3. **Atenção aos internacionais** (se houver): lembrar prazo 15–40 dias e risco de imposto
4. **Verificar status MP** se houver resultado internacional: fazer WebSearch rápido `"taxa importação brasil junho 2026"` e reportar status atual
5. **Cupons:** orientar a testar antes de finalizar compra
6. **Histórico de preço:** se Amazon aparecer, mencionar que o preço pode ter variado (CamelCamelCamel não integrado em v1 — sugerir verificar manualmente)
7. **Links diretos (obrigatório):** apresentar links clicáveis para os 2–3 melhores produtos recomendados, um por plataforma. Formato:
   - [Nome do produto — Plataforma](URL) — R$XX
   Se o script não retornar links, fazer WebSearch para obtê-los antes de encerrar.

---

## Tratamento de erros comuns

| Erro | Ação |
|---|---|
| `APIFY_API_TOKEN não encontrado` | Checar `.env` na raiz do vault. Token deve existir (já configurado). |
| Estante Virtual captcha | Avisar usuário, sugerir busca manual em estantevirtual.com.br |
| SerpAPI ausente | Avisar que Amazon/MagaLu foram pulados. Sugerir adicionar `SERPAPI_KEY` ao `.env`. |
| Actor timeout (150s) | Plataforma pulada, continuar com as demais. |
| Nenhum resultado | Sugerir query mais genérica. Tentar novamente com `--condicao qualquer`. |
| Tiendeo sem resultado | Avisar e seguir para busca online. Sugerir verificar manualmente tiendeo.com.br/{sua-cidade} |

---

## Notas de segurança

- Verificar antes de cada sessão que MAX_COST_SESSION = USD 0.50 (~R$ 2,90) no script
- Se usuário pedir busca muito ampla (>5 plataformas + intl), alertar sobre custo estimado em USD e BRL
- Nunca rodar em loop automático — sempre one-shot com confirmação
- Câmbio USD/BRL: obtido via AwesomeAPI (economia.awesomeapi.com.br), cache de 30 dias em `.usd_brl_cache.json`
