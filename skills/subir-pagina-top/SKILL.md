---
name: subir-pagina-top
description: >
  Bootstrapa e publica uma landing page de infoproduto (Hotmart, Kiwify, etc.) no
  Vercel: gera o Guia de Construção da Página e o design-system.json, configura
  domínio, headers de segurança, cache, robots.txt, sitemap, SEO, Meta Pixel +
  CAPI server-side, medição da base e monitoramento. Nunca usa valores de outro
  produto como placeholder. Tracking é parte obrigatória do deploy.
allowed-tools: Read, Write, Edit, Bash
---

> **Instalação:** copiar esta pasta para `.claude/skills/subir-pagina-top/` no projeto e criar o command apontando para o SKILL.md. Ver [README.md](./README.md) para instruções completas e pré-requisitos.


---

# /subir-pagina-top: LP de Infoproduto do Zero ao Ar

Cria os arquivos de fundação e conduz o deploy completo de uma LP de conversão:

- **`Guia de Construção da Página.md`**: regras, protocolo, checklists, SEO+AEO, performance, LGPD
- **`design-system.json`**: tokens visuais, princípios e decisões de componente
- **Meta Pixel + CAPI**: tracking obrigatório embutido no fluxo de deploy
- **Medição da base e monitoramento**: contador anônimo de chegadas, saúde dos eventos, uptime

O conteúdo agnóstico (checklists, performance, SEO+AEO, LGPD, responsividade) é gerado com base em boas práticas universais. O conteúdo específico (paleta, IDs de tracking, URLs, configuração) é coletado junto com o usuário: nunca inventado nem emprestado de outro produto.

## Usage

```
/subir-pagina-top
```

---

## Casos de uso

**Produto novo (do zero):** seguir os passos 1–10 na ordem.

**Migrando LP do Hotmart para LP customizada:** pedir a URL da LP na Hotmart. Visitar a URL com ferramentas de browser (`mcp__claude-in-chrome__navigate` + `mcp__claude-in-chrome__read_page` + `mcp__claude-in-chrome__javascript_tool`) e extrair automaticamente:
- **Paleta**: cores dominantes via `getComputedStyle` nos elementos principais (fundo, textos, CTAs)
- **Tipografia**: famílias de fonte, tamanhos e pesos em uso
- **Estrutura de seções**: ordem e tipo de cada bloco (hero, depoimentos, preço, FAQ, etc.)
- **Copy**: textos de cada seção (headline, subtítulo, corpo, CTAs, depoimentos)
- **Tracking IDs**: Pixel ID (buscar `fbq('init','`) e outros scripts de tracking presentes
- **Checkout URL**: href dos botões de CTA
- **Preço**: texto do elemento de preço

Com esses dados extraídos, pré-preencher o DS (paleta, tipografia, tracking IDs) e o Guia (configuração, checkout URL, preço) sem precisar perguntar o que já está na página. Perguntar só o que não foi possível extrair. No passo 5, atenção especial a: self-hosting de todos os assets (imagens e fontes), aviso/consentimento LGPD (ausente na Hotmart nativa), passo 9 (infraestrutura de deploy).

**LP existente querendo otimizar:** se Guia + DS já existem, pular passos 2–4 e executar o passo de revisão abaixo, depois ir aos checklists. Se Guia + DS ainda não existem, gerar agora com base na LP atual.

> **Revisão de Guia + DS existentes:** antes de ir aos checklists, verificar: (1) seção Performance do Guia: cobre as regras de performance deste skill (passo 8)? (2) DS tokens de cor: há contraste suficiente? (3) DS performance: `formato_imagem` inclui AVIF? (4) Seção LGPD: mecanismo de consentimento ou aviso implementado e documentado, e coerente com o `TRACK_MODE` (passo 9c)? (5) Tracking IDs: ainda válidos? Atualizar os campos defasados antes de rodar o checklist.

---

## O Que Fazer

### 1. Definir pasta do projeto

**Se existir `meus-produtos/.ativo` (ambiente Fluxo Criativo):** ler o arquivo para obter o produto ativo e usar `meus-produtos/{ativo}/entregas/paginas/` como pasta base. Arquivo existente sem produto ativo: perguntar qual usar.

**Se não existir `meus-produtos/.ativo`:** perguntar ao usuário:
> "Em qual pasta você quer salvar os arquivos do projeto? (ex: `meu-produto/paginas/`), ou deixe em branco para usar a pasta atual."

Usar a resposta como `{pasta-base}` para todos os passos seguintes. Criar a pasta se não existir.

### 2. Obter referência visual ou construir junto

Perguntar ao usuário:

> "Você tem uma página de referência (um site, LP ou marca cujo visual se aproxima do que você quer)? Cole o link."

**Verificar disponibilidade:** se `mcp__claude-in-chrome__*` não responder, informar ao usuário e aplicar o fallback das 3 perguntas abaixo para todo este passo. Não travar.

**Se o usuário colar uma URL:** visitar com `mcp__claude-in-chrome__navigate` + `mcp__claude-in-chrome__read_page`. Para cores e fontes, usar `mcp__claude-in-chrome__javascript_tool` com `getComputedStyle`, necessário porque muitos valores estão em CSS calculado, não no HTML estático. Extrair:
- Paleta dominante (cores de fundo, texto, CTA)
- Famílias de fonte e hierarquia tipográfica
- Tom geral: formal/informal, minimalista/denso, quente/frio
- Elementos de layout (proporções, uso de imagem, espaçamento)

Usar o que foi extraído para construir o DS; não perguntar o que já foi visto. Não copiar; usar como direção de intenção visual.

**Se a página bloquear acesso automatizado** (Cloudflare, login, erro de carregamento): informar ao usuário e cair no fallback das 3 perguntas abaixo.

**Se não tiver URL:** fazer 3 perguntas objetivas:
- Qual o tom emocional do produto? (ex: calmo e científico / vibrante e motivacional / sofisticado e premium)
- Qual a cor que o produto mais evoca? (pode ser uma sensação, não necessariamente um hex)
- Há alguma marca ou produto que admira visualmente, mesmo que de outro nicho?

### 3. Coletar configuração do site

Se existir um arquivo `perfil.md` na pasta do projeto, ler e extrair o que estiver disponível.

**Migração Hotmart:** a URL já foi visitada nos Casos de uso: não pedir de novo. Pular diretamente para extração dos campos abaixo.

**Produto novo (URL do passo 2 é de outro site, referência visual):** NÃO extrair campos abaixo dessa URL (é de outra marca, teria IDs e checkout errados). Ir direto à tabela de campos obrigatórios.

**Quando a URL visitada É a própria LP do produto:** extrair automaticamente usando `mcp__claude-in-chrome__javascript_tool` (necessário para campos em scripts dinâmicos como Pixel ID):
- Pixel ID: `document.cookie` ou buscar `fbq('init','` no source via `document.documentElement.innerHTML`
- Checkout URL: `href` dos botões de CTA principais
- Preço: texto do elemento de preço visível
- Nome do produto: `document.title` ou `og:title`
- URL canônica: `link[rel=canonical]` ou `og:url`
- YouTube Video ID: `src` de iframes YouTube presentes

Marcar como `⬜` apenas o que não foi possível extrair.

Para os campos ainda ausentes, perguntar em uma única mensagem consolidada:

| Campo | Obrigatório |
|-------|-------------|
| Nome do produto | Sim |
| URL canônica | Sim |
| Email de contato | Sim |
| CNPJ (para rodapé legal) | Sim |
| Meta Pixel ID | Sim, se usar Meta Ads |
| Meta CAPI Access Token (server-side) | Sim, se usar Meta Ads. Obter em: Meta Business Suite → Events Manager → seu Dataset → Configurações → API de Conversões → Gerar token de acesso |
| Checkout URL | Sim |
| Plataforma de vendas | Sim |
| Preço | Sim |
| Nome do professor/criador | Sim |
| Microsoft Clarity ID | Não |
| YouTube Video ID (VSL) | Não; apenas se o produto tiver VSL |
| Instagram / YouTube / TikTok | Não |
| og:title (sugerir baseado no produto) | Não |
| og:description | Não |

Campos sem resposta → marcar com `⬜ a preencher`.

### 4. Criar pasta de destino

Criar `{pasta-base}` agora se não existir. Sem perguntas; avançar.

### 5. Gerar o Guia de Construção

**Se a pasta foi criada agora (produto novo):** gerar diretamente, pois não existe nada ainda. **Se a pasta pré-existia:** verificar se `Guia de Construção da Página.md` existe; se sim, perguntar (a) atualizar seções defasadas ou (b) recriar do zero.

**Ao criar:** gerar o Guia com todo o conteúdo agnóstico (regras de performance, SEO+AEO, responsividade, LGPD, anti-padrões universais) diretamente, sem copiar de nenhum produto específico. Preencher as seções de configuração com os dados coletados no passo 3.

**Seções de configuração** (específicas do produto; preencher com dados do passo 3):
- `⬜ Configuração do site`: URL, email, Pixel ID, checkout URL, plataforma, preço, criador
- `⬜ Arquivos e caminhos`: paths do produto
- `⬜ Tracking`: IDs e nomes de CTA do produto

**Seções agnósticas** (gerar com boas práticas universais):
- Protocolo de trabalho e checklist de avaliação
- SEO + AEO completo (blocos 1 a 9)
- Schemas JSON-LD, Validação e Testes
- Anti-padrões estruturais: incluir apenas os universais de LP (afirmações não verificáveis, promessas impossíveis, jargão técnico excessivo, copy que confunde clareza com criatividade). Remover qualquer anti-padrão específico de nicho
- Performance: regras agnósticas de produto, ordenadas por impacto (base: tabela do passo 8)
- LGPD: status inicial `⬜ PENDENTE: banner a implementar` (ou, no modo `load`, política de privacidade descrevendo quando a medição começa; ver 9c)

**Salvar em:** `{pasta-base}/Guia de Construção da Página.md`

### 6. Gerar o Design System JSON

**Se a pasta foi criada agora (produto novo):** gerar diretamente. **Se a pasta pré-existia:** verificar se `design-system.json` existe; se sim, perguntar (a) atualizar paleta/tokens ou (b) recriar do zero.

**Ao criar:** gerar o DS com a estrutura completa. Preencher a configuração específica do produto; gerar o conteúdo agnóstico diretamente.

**Campos específicos do produto** (preencher com dados coletados):
- `nome`, `produto`, `gerado_em`
- `paleta`: construir com base na referência visual ou respostas do passo 2. Derivar tokens:
  - `brand` = cor dominante extraída (fundo ou elemento principal)
  - `brand_tint` = brand clareado ~80% (10–15% opacidade sobre branco)
  - `brand_mid` = brand clareado ~40%
  - `brand_vivid` = brand saturado/mais vivo (para hover/destaque)
  - `star` / accent = cor de destaque, geralmente usada no CTA
  - `ink` = preto ou azul-escuro (texto principal)
  - `ink_2` = ink em ~70% (texto secundário)
  - `ink_3` = ink em ~45% (texto terciário / placeholders)
  - `bg` = branco ou quase-branco (fundo de seção padrão)
  - `surface` = fundo alternativo sutil (cinza muito claro ou brand_tint)
  - `border` = borda sutil (ink em ~15%)
- `mood`: tom visual em 2–4 palavras
- `observacoes`: origem das cores e decisões iniciais
- `tracking`: todos os IDs como `⬜ a configurar`
- `lgpd.status_atual`: `⬜ a implementar`

**Campos agnósticos** (gerar com boas práticas universais):
- `principios`: lista de princípios do DS; verificar os que expressam tom emocional específico e adaptar ao produto
- `copy_tom`: regras de "!" e celebração (universais para LP de infoproduto)
- Toda a estrutura de tokens: `tipografia`, `icones`, `border_radius`, `espacamento`, `sombras`, `botao`, `cards`, `tabelas`, `listas`, `alternancia_secoes_8D`, `divisores_de_secao`, `performance`, `responsividade`, `ab_testing`, `lgpd`, `acessibilidade`

**Salvar em:** `{pasta-base}/design-system.json`

### 7. Checklist de responsividade: executar após construir a LP (não agora)

Após implementar ou revisar qualquer seção da LP, verificar:

| Verificação | Como checar |
|---|---|
| **Mobile 390px** | DevTools → 390px; sem overflow horizontal; sem texto cortado; CTAs tocáveis; texto de 3+ linhas alinhado à esquerda; título de seção maior que os subtítulos dela |
| **Desktop 900px+** | Abrir em 1440px; tipografia segue a escala por função do DS (tamanho pelo papel do texto; desktop parte de H1 ×2 · H2 ×1.5 · H3 ×1.22 · body +1px) |
| **Layouts multi-coluna** | Só dentro de `@media (min-width: 900px)`; CSS base (mobile) intocado |
| **Wrapper semântico** | Cada coluna tem seu wrapper HTML; nunca `grid-row`/`grid-column` em filhos |
| **Touch targets** | Todo elemento clicável com área ≥ 44×44px (WCAG 2.5.5) |
| **Imagem LCP** | `fetchpriority="high"` sem `loading="lazy"` acima da dobra |
| **Fontes desktop** | Nunca definir font-size desktop fora do bloco `@media (min-width: 900px)` |
| **Breakpoint único** | Um único bloco `@media (min-width: 900px)` consolidado, sem duplicatas |

Padrões de implementação detalhados: seção "Padrões de composição desktop" no Guia (multi-coluna, masonry, watermark, br-desktop, logo clip).

### 8. Checklist de performance: executar antes do primeiro deploy (não agora)

Performance mobile é princípio central: impacto direto em conversão de tráfego pago. Meta: Lighthouse mobile ≥ 90. Verificar:

| Verificação | Como executar |
|---|---|
| **Self-hosting total** | `grep -o 'src="https://[^"]*"' index.html` não deve retornar nenhuma imagem. Exceções: thumbnails YouTube (facades, não carregam no load) |
| **Fontes self-hosted** | `grep "fonts.google\|fonts.gstatic" index.html` não deve aparecer nada |
| **Ícones SVG inline** | `grep "font-awesome\|fa-" index.html` não deve aparecer nada |
| **Thumbnail LCP self-hosted** | Thumbnail do VSL: arquivo WebP local em `assets/`, não URL do YouTube. srcset com versão mobile (<= 780px) |
| **CSS reset imagens** | `img { display: block; max-width: 100%; height: auto; }` no reset global |
| **width + height em todas as imgs** | `grep -c '<img' index.html` vs `grep -c 'width=' index.html` devem ser iguais |
| **loading=lazy em tudo abaixo do fold** | `grep -n '<img' index.html \| grep -v 'loading='` só hero logo e LCP thumbnail devem aparecer |
| **Nada abaixo da dobra antes do load** | `loading="lazy"` não basta: em rede lenta o Chrome baixa imagem lazy até ~2.500 px abaixo da tela, inclusive `<source srcset>` de `<picture>`, e tudo que começa antes do evento load atrasa o que depende dele (pixel disparado no load, LPV). Imagem abaixo da dobra a menos de ~2.500 px do fim da 1ª tela: `data-src`/`data-srcset` trocados no load, com width/height. Conferir em rede lenta (celular e computador) a lista do que baixa antes do load: só capa, logo do topo e fonte. Refazer a cada seção de cima encurtada, removida ou reordenada |
| **Imagem do LCP: o arquivo que o celular baixa** | Com `srcset` por largura e `sizes="100vw"`, tela densa (3x) pede 3 × a largura e escolhe a versão de computador. Declarar no celular um `sizes` menor (ex: `50vw`) faz o navegador pegar a versão leve; o mesmo valor vai no `<link rel="preload" imagesizes>` e no `<img sizes>`, senão baixa duas vezes. Conferir na aba Network, em 4G lento, qual arquivo desce |
| **font-display pelo elemento LCP** | LCP imagem: `swap` + `@font-face` reserva com `size-adjust`/`ascent-override`/`descent-override`/`line-gap-override` (calcular no woff2), uma sobre Arial e outra sobre `local('Roboto')` (Android não tem Arial), mais `@supports not (font-size-adjust: from-font)` com a mesma face em `optional` (navegador sem `size-adjust`); conferir o pulo em várias larguras com a fonte bloqueada e carregada; LCP texto: `optional`. `optional` deixa a 1ª visita em rede móvel na fonte do sistema |
| **preconnect LGPD** | `grep 'preconnect' index.html`: DEVE ter ZERO preconnects para tracking domains (Meta, Clarity, GA) no `<head>`. `preconnect` estabelece TCP+TLS, expõe o IP do usuário ao servidor remoto e conta como transferência de dado pessoal sob LGPD antes do aceite. Apenas checkout/plataforma de pagamento aceita pré-consent. Tracking domains: injetar `preconnect` dinamicamente dentro de `loadTracking()` via `document.createElement('link')`. `dns-prefetch` (sem handshake) é aceitável pré-consent |
| **vercel.json com cache headers** | Arquivo existe na raiz do deploy com `max-age=31536000, immutable` para `/assets/(.*)` |
| **HTML minificado (opcional)** | O deploy da Vercel não minifica nada. Se quiser minificar, rodar antes do commit: `npx html-minifier-terser --collapse-whitespace --remove-comments --conserve-collapse -o src/index.html fonte/index.html` (sem `--minify-js`: o JS inline do tracking e do contador não deve ser reescrito). Manter o HTML-fonte legível fora de `src/` |
| **Iframes de vídeo com facade** | `grep -c '<iframe' index.html`: depoimentos devem ser 0 (injetados no clique via `innerHTML`). VSL principal: facade é obrigatório por performance (nenhum iframe carrega antes da interação). Se VSLProgress implementado, o iframe pode ser pré-existente com `enablejsapi=1` (Opção A) ou criado via `YT.Player` na div-container (Opção B); ambos valem como facade, pois o player só inicializa no clique |
| **Tracking fora do `<head>`** | `grep -n "fbq\|clarity\|gtag" index.html \| grep -v "loadTracking\|function\|//"` nenhuma ocorrência fora da função de carregamento do tracking (as exceções são o bloco de sandbox e o contador do início do `<head>`, 9n) |
| **AVIF com fallback WebP** | `grep -c 'type="image/avif"' index.html`: imagens grandes devem ter `<picture>` com source AVIF + img WebP. Exceção: VSL thumbnail (LCP + preload) |
| **Sem redirects desnecessários** | `curl -I https://SEU-DOMINIO.com/` sem `Location:` na resposta do apex |
| **Payload total** | `du -sh assets/` com meta < 1.6MB total |
| **Legível por agente de IA** | Preço, prova e oferta no HTML bruto (`curl -s URL \| sed 's/<script.*<\/script>//'` ainda mostra o texto); depoimento em imagem tem a transcrição integral no `llms.txt` (alegação de saúde arriscada, como substância, remédio, suicídio ou cura, sai do texto e do alt com `(…)`); depoimento em vídeo tem a transcrição no `llms.txt` e no `transcript` de um `VideoObject` (JSON-LD no fim do `<body>`); vídeo longo entra só como resumo por parte com minutagem (`llms.txt`) e `Clip` no `hasPart`, nunca a transcrição inteira; `dateModified` no JSON-LD atualizado no deploy |
| **Prefetch checkout** | `grep 'rel="prefetch"' index.html` deve retornar a URL do checkout |
| **Prefetch pixel-js + dns-prefetch** | `grep 'prefetch.*pixel-js\|dns-prefetch' index.html` deve retornar `<link rel="prefetch" href="/api/pixel-js">` e `dns-prefetch` para os domínios de tracking (`www.facebook.com`, `www.clarity.ms`) e de suporte (`www.youtube.com`, `www.youtube-nocookie.com`, domínio do checkout da plataforma). O prefetch pré-baixa o script antes do consent (LGPD-safe: domínio próprio); `dns-prefetch` resolve DNS sem handshake TCP/TLS (LGPD-safe pré-consent) |
| **Gatilhos do consent gate (só no modo `gate`)** | `grep -n 'touchstart' index.html`: conferir que existem o `addEventListener`, o `removeEventListener` e o guard `e.type === 'touchstart'` do `_policyFocused`. Não contar o total de ocorrências: o contador do `<head>` (9n) também escuta `touchstart`. No celular, `touchstart` dispara antes de `scroll` e cobre o primeiro toque. No modo `load` não há gate |
| **sw.js: CACHE_NAME versionado** | `grep CACHE_NAME sw.js`: se `sw.js` foi editado neste deploy, o valor **deve ter sido incrementado** (`v1` → `v2` etc.). Sem o bump, usuários continuam servindo a versão antiga do cache indefinidamente: `no-cache` no header do arquivo detecta a mudança de SW mas não limpa o Cache API interno |
| **Lighthouse mobile** | DevTools → Lighthouse → Mobile, aba anônima, URL de produção. Score ≥ 90, perseguir 95+ |

**Dependências** (instalar se não tiver): `brew install webp libavif`
**Conversão WebP:** `cwebp -q 65 foto.png -o foto.webp` (fotos); `cwebp -q 80 logo.png -o logo.webp` (logos).
**Conversão AVIF:** `dwebp foto.webp -o /tmp/tmp.png && avifenc -q 65 --speed 6 /tmp/tmp.png foto.avif`; sempre comparar tamanhos; se avif >= webp, descartar avif e usar WebP puro.
**Recomprimir WebP grande:** `dwebp imagem.webp -o /tmp/tmp.png && cwebp -q 65 /tmp/tmp.png -o imagem.webp`
**Diagnóstico LCP:** Lighthouse → expandir "Largest Contentful Paint element" → ver breakdown TTFB/load delay/load duration/render delay.
**Referência completa:** regras de performance ordenadas por impacto na seção `## Performance` do Guia de Construção da Página.

### 9. Infraestrutura de deploy e tracking (obrigatório antes de ir ao ar)

#### 9a. vercel.json

Criar na raiz de `{pasta-base}/` (os arquivos estáticos ficam em `{pasta-base}/src/`; `api/` fica na raiz):
```json
{
  "outputDirectory": "src",
  "cleanUrls": true,
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options",   "value": "nosniff" },
        { "key": "X-Frame-Options",           "value": "SAMEORIGIN" },
        { "key": "X-XSS-Protection",          "value": "0" },
        { "key": "Referrer-Policy",           "value": "strict-origin-when-cross-origin" }
      ]
    },
    { "source": "/",            "headers": [{"key": "Cache-Control", "value": "public, max-age=0, s-maxage=86400, stale-while-revalidate=86400"}] },
    { "source": "/(.*)\\.html", "headers": [{"key": "Cache-Control", "value": "public, max-age=0, s-maxage=86400, stale-while-revalidate=86400"}] },
    { "source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, s-maxage=31536000, immutable"}] },
    { "source": "/sw.js",       "headers": [{"key": "Cache-Control", "value": "no-cache"}] },
    { "source": "/robots.txt",  "headers": [{"key": "Cache-Control", "value": "public, max-age=86400"}] },
    { "source": "/sitemap.xml", "headers": [{"key": "Cache-Control", "value": "public, max-age=86400"}] }
  ],
  "rewrites": [
    { "source": "/fbcdn/:path*", "destination": "https://connect.facebook.net/:path*" }
  ]
}
```

> `X-Frame-Options: SAMEORIGIN`: padrão seguro para LP standalone. Remover **apenas** se a LP precisar ser embarcada em iframe por domínio externo (ex: funil de terceiros que carrega a página dentro de um frame).
>
> O `rewrites` de `/fbcdn/` serve à configuração do pixel pelo seu domínio (9c). Os arquivos `robots.txt`, `sitemap.xml` e `llms.txt` ficam em `src/` e precisam ser criados junto com a página.

#### 9b. Deploy, repositório e CI/CD

**Pré-requisito de infra:** conta na [Vercel](https://vercel.com) (plano gratuito suficiente para LP). Necessário para criar o projeto, configurar a env var `META_CAPI_KEY` e publicar. Sem conta Vercel, o deploy e o CAPI não funcionam.

**Não existe script de deploy a gerar.** A Vercel monta as funções de `api/` e publica `src/` sozinha. Dois caminhos válidos:
1. **Push no `main` (Vercel Git), caminho normal.** Conectar o repositório GitHub ao projeto Vercel (vercel.com → integração GitHub → instalar na conta/organização do produto). Cada push no `main` publica em produção; outros ramos geram prévia.
	- Requisito: `git config user.email` no diretório do projeto com o email de um membro da equipe Vercel. Se o email do commit não corresponder a nenhum membro, o CI/CD rejeita o deploy em silêncio
2. **Vercel CLI**, para publicar sem push ou quando o gatilho Git falha: `npm i -g vercel`, `.vercel/project.json` na raiz (com `projectId` e `orgId`), e na raiz do projeto: `vercel deploy --prod --yes`
	- Autenticação: CLI já logada (`vercel whoami`). `VERCEL_TOKEN` só é preciso fora de uma CLI logada; exportar na hora (`VERCEL_TOKEN="..." vercel deploy --prod --yes`), nunca salvar em arquivo nem em texto

**Proibido: API REST de deploy com bundle local** (`POST /v13/deployments` com arquivos montados por você). Ela gera SHA-1 UIDs nas funções Lambda via `ncc` local e dá 500 em runtime, mas o deploy aparece como READY no dashboard e o CDN continua servindo o HTML em cache. O erro é silencioso e difícil de diagnosticar. Push no `main` e CLI não têm esse problema.

Manter o projeto em **diretório permanente**, nunca `/tmp` (arquivos desaparecem no restart de ambiente). Se o usuário não tiver `.vercel/project.json`, gerar agora (`vercel link`); não deixar como `⬜ a fazer`.

**Env vars:** configurar `META_CAPI_KEY` no projeto Vercel (Settings → Environment Variables → tipo Sensitive). **Nunca colocar o token no código nem em arquivos commitados.**

**Verificação obrigatória após cada deploy:**
```bash
curl -s -o /dev/null -w "%{http_code}" https://SEU-DOMINIO.com/                    # 200
curl -s https://SEU-DOMINIO.com/api/healthcheck                                     # {"ok":true,"ts":...}
curl -s https://SEU-DOMINIO.com/api/capi -X POST \
  -H "Content-Type: application/json" \
  -d '{"event_name":"PageView","event_id":"test"}'                                  # {"ok":true}
curl -s https://SEU-DOMINIO.com/api/capi-check                                      # {"ok":true,"token_valid":true}
```
O `POST` de teste acima envia um `PageView` de verdade em produção. Para testar sem poluir as estatísticas, usar `test_event_code` do Events Manager (campo no body ou env `META_CAPI_TEST_CODE`; ver 9e). Em prévia (ramo que não é `main`) a função devolve `{"ok":true,"sandbox":true}` e não envia nada.

**Repositório Git (backup e histórico).** Versionar o diretório permanente em repositório GitHub privado, na conta do produto. Regras:
- **`git add -p` ou arquivo específico, nunca `git add -A`/`git add .`**: revisar o diff antes de qualquer commit
- Tokens (`META_CAPI_KEY`, `VERCEL_TOKEN`) permanecem exclusivamente como env var: nunca no código, nunca no commit
- Nenhum dado de usuário/lead/cliente entra no diretório do projeto: CSV, JSON de CRM, qualquer arquivo com nome/email/telefone ficam em outro diretório
- Debug com dados reais: usar `test_event_code` do painel do pixel; nunca salvar PII localmente
- `.gitignore`: adicionar `out/`, `.DS_Store`, `*.log`, `.env*`, `src/vercel.json`, `*.csv`, `*.xlsx`, `*leads*`, `*export*`
- `.vercelignore`: scripts operacionais que não precisam ser deployados (ex: scripts de monitoramento local, `preview-paleta.html`)
- `.vercel/project.json` pode ser commitado em repo privado (contém só IDs de projeto, não tokens)
- Fluxo normal de edição: editar no diretório local → `git add -p && git commit` → `git push` (publica pela Vercel Git)

**Confirmar que o deploy saiu.** O gatilho Git→Vercel falha em silêncio: o commit entra no repositório e nenhum deploy é criado, com o CDN servindo a versão antiga por horas. Depois de todo push, conferir pelo conteúdo: o hash do HTML servido (`curl -s https://SEU-DOMINIO.com/ | shasum -a 256`) igual ao do arquivo commitado (`git show HEAD:src/index.html | shasum -a 256`), e `/api/selfcheck` (9n) ok. Um commit vazio reativa o gatilho. `?query` na URL não fura o cache do CDN: conferir `age` e `x-vercel-cache` no `curl -sI`.

#### 9c. Meta Pixel: snippet base (obrigatório)

Inserir no `<head>` depois do bloco de sandbox e do contador de 9n, antes de qualquer outro script de tracking. Substituir `SEU_PIXEL_ID` pelo Pixel ID coletado no passo 3. Não duplicar se já existir (procurar por `fbq('init'`). Em produção o snippet vive dentro de `loadTracking()` (modo `load`: no evento `load`; modo `gate`: depois do consentimento), não solto no `<head>`; a forma solta abaixo é a versão mínima:

```html
<!-- Meta Pixel -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'/api/pixel-js');  /* proxy first-party, ver 9e.1; fallback: 'https://connect.facebook.net/en_US/fbevents.js' */
fbq('set', 'cdn', location.origin + '/fbcdn/');  /* configuração do pixel pelo seu domínio, ver abaixo */
fbq('skipOpenbridge', 'SEU_PIXEL_ID');  /* desliga o espelho de servidor da Meta, ver abaixo */
fbq('init', 'SEU_PIXEL_ID');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=SEU_PIXEL_ID&ev=PageView&noscript=1"/></noscript>
<!-- End Meta Pixel -->
```

**Configuração do pixel pelo seu domínio.** `fbq('set', 'cdn', location.origin + '/fbcdn/')` antes do `fbq('init')` e o `rewrites` de `/fbcdn/` no `vercel.json` (9a). Comando nativo do fbevents. Sem isso, quem tem `connect.facebook.net` bloqueado (DNS bloqueador, lista de rastreador) carrega o pixel e nunca envia evento, porque a configuração não chega. O CDN da Vercel guarda a resposta (~20 min), o que ainda encurta o caminho até o primeiro envio. Medido numa página real: nenhum ganho geral na taxa de carregamento; fica como proteção contra bloqueio. O envio (`facebook.com/tr`) continua direto do navegador: nunca repassar `/tr` pelo seu servidor (perde o IP real do visitante).

**Não rodar espelho de servidor em cima do seu próprio CAPI.** A "Conversions API: Supported by Meta" (ativação em um clique) duplica cada evento do navegador como evento de servidor: a razão servidor:navegador vai a ~2,5:1 sem recuperar conversão nenhuma, e a leitura dos números fica confusa. Se você já tem CAPI próprio, desligue o espelho **no site**, com `fbq('skipOpenbridge', 'SEU_PIXEL_ID')` antes do `fbq('init')` (comando nativo do fbevents, reversível apagando a linha). Evite o botão de excluir o conjunto no Gerenciador de Negócios: o diálogo diz *"will prevent it from receiving data through Conversions API"*, texto que também comporta bloquear toda a ingestão por CAPI. Validar no navegador: com o comando, zero requisições ao endpoint do espelho, e `facebook.com/tr` e o seu `/api/capi` seguem disparando.

**Modo de carregamento do tracking (`window.TRACK_MODE`, definido no início do `<head>`, ver 9n).** O template deixa escolher; a decisão é do usuário e tem peso jurídico.
- **`load` (recomendado pelo ganho de cobertura):** pixel e analytics carregam no evento `load` (com rede de segurança de ~4 s), sem barra de cookies. Maior alavanca de tracking medida (ver "Taxa de carregamento" em 9n). Exige política de privacidade dizendo que a medição começa ao acessar o site ("Ao acessar o site você consente com o uso dessas ferramentas"). A decisão jurídica é do dono da página: a ANPD não reconhece "continuar navegando" como consentimento, então o usuário precisa aceitar esse risco conscientemente. Avisar isso ao usuário antes de fixar `load`
- **`gate` (mais conservador):** pixel só depois de uma interação que conta como consentimento. Gatilhos base: `scroll`, `click` e `touchstart` (passive); `touchstart` cobre o celular antes do scroll, defensável como "ao navegar". O guard do banner aplica `click` e `touchstart` juntos no mesmo bloco. Enquanto `_policyFocused = true`, `click` e `touchstart` dentro da seção de política de privacidade (ex: `#politica-privacidade`) são suprimidos; fora dela, concedem consentimento normalmente
- Os dois modos convivem no mesmo HTML (`if (window.TRACK_MODE !== 'load' && ...)` guarda o gate), então voltar de um para o outro é trocar uma linha mais o texto da política, no mesmo commit
- Em ambos: `loadTracking()` é a única porta de entrada do tracking; chama `window._mConsent()` (contador), grava o cookie de consentimento (9f) e cria os `preconnect` de tracking (8)

#### 9d. Eventos por tipo de página

**Página de vendas:** listeners nos botões de CTA para `InitiateCheckout` + `ViewContent`:
```js
document.querySelectorAll('[data-cta], a.cta, .btn-cta, button.cta').forEach(function(el){
  el.addEventListener('click', function(){
    fbq('track', 'InitiateCheckout');
  });
});
fbq('track', 'ViewContent');
```
Adicionar `data-cta` em todos os botões/links que levam ao checkout, caso ainda não tenham classe identificável. Se a plataforma de pagamento já envia `InitiateCheckout` por servidor, não duplicar na LP (ver 9g).

**Página de captura:** listener no submit do formulário:
```js
var f = document.querySelector('form');
if (f) f.addEventListener('submit', function(){ fbq('track', 'Lead'); });
```

**Página de obrigado de venda:**
```js
fbq('track', 'Purchase', {value: 0.00, currency: 'BRL'});
// substituir 0.00 pelo valor do produto
```

**Página de obrigado de captura:**
```js
fbq('track', 'CompleteRegistration');
```

Nunca incluir evento que não faça sentido para o tipo de página.

#### 9e. CAPI: Meta Conversions API (obrigatório para campanha de ads)

**Por que CAPI:** Pixel browser é bloqueado por adblockers e Safari ITP. CAPI envia os mesmos eventos server-side, garantindo cobertura completa e melhorando o EMQ (Event Match Quality) na Meta. É uma Vercel serverless function em paralelo ao pixel do navegador.

Criar `api/capi.js` na raiz de `{pasta-base}/`. Substituir `SEU_PIXEL_ID` e `SEU-DOMINIO.com` pelos valores do passo 3; verificar a versão estável atual da Graph API antes de usar. Pontos do template:
- **Trava de sandbox:** fora de `production` (prévia da Vercel) responde `ok` sem enviar nada à Meta, para teste nunca poluir a base
- **IPv6:** prefere o IPv6 de `x-real-ip`/`x-forwarded-for` quando houver (o pixel usa IPv6 para clientes IPv6; IPv4 contra IPv6 reduz o EMQ)
- **Retry** até 2x em 5xx e 429
- **`fbp` server-side** gerado se ausente e renovado por `Set-Cookie` HTTP (imune ao cap de 7 dias do ITP), então o `api/fbp-init.js` (9e.3) é desnecessário
- **`test_event_code`:** a env `META_CAPI_TEST_CODE` tem prioridade e redireciona TODOS os eventos para Test Events; remover a env para voltar à produção. O body aceita `test_event_code` para teste manual pelo console
- **`normPhone` e `country`** assumem Brasil (DDI 55, `br`): adaptar para outros países

```js
const crypto = require('crypto');

const PIXEL_ID = 'SEU_PIXEL_ID';
const API_VER  = 'v26.0'; // verificar versão estável atual: developers.facebook.com/docs/graph-api/changelog

function sha256(val) {
  if (!val) return undefined;
  return crypto.createHash('sha256').update(String(val).toLowerCase().trim()).digest('hex');
}

// Normaliza para E.164 sem o '+' (exigido pela Meta). Cobre números brasileiros com ou sem DDI.
// Para outros países, adaptar a lógica de DDI e comprimento.
function normPhone(phone) {
  if (!phone) return undefined;
  var d = String(phone).replace(/\D/g, '');
  if (d.startsWith('0'))  d = '55' + d.slice(1);
  if (d.length === 11)    d = '55' + d; // celular com DDD, sem DDI
  if (d.length === 10)    d = '55' + d; // fixo com DDD, sem DDI
  if (d.startsWith('5555') && d.length >= 14) d = d.slice(2); // DDI duplo
  return (d.length === 12 || d.length === 13) ? d : undefined;
}

async function sendToMeta(payload, attempt) {
  var token = process.env.META_CAPI_KEY;
  if (!token) return { ok: false, error: 'token ausente' };
  var url = 'https://graph.facebook.com/' + API_VER + '/' + PIXEL_ID + '/events';
  attempt = attempt || 0;
  try {
    var res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(Object.assign({}, payload, { access_token: token }))
    });
    var data = await res.json();
    if (res.ok) return { ok: true, data };
    // Retry até 2x em erro de servidor (5xx) ou rate limit (429)
    if ((res.status >= 500 || res.status === 429) && attempt < 2) return sendToMeta(payload, attempt + 1);
    return { ok: false, data };
  } catch (e) {
    if (attempt < 2) return sendToMeta(payload, attempt + 1);
    return { ok: false, error: e.message };
  }
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();
  // Sandbox (prévia da Vercel, preview deploy): nunca envia evento à Meta fora de produção
  if (process.env.VERCEL_ENV && process.env.VERCEL_ENV !== 'production') return res.status(200).json({ ok: true, sandbox: true });

  var b = req.body || {};
  if (!b.event_name || !b.event_id) {
    return res.status(400).json({ error: 'event_name e event_id obrigatórios' });
  }

  // Prefere IPv6 quando disponível: o pixel usa IPv6 para clientes IPv6, e IPv4 aqui contra IPv6 lá reduz o EMQ
  var _xri      = (req.headers['x-real-ip'] || '').trim();
  var _fwdFirst = (req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  var _v6 = function(s) { return (s && s.indexOf(':') !== -1) ? s : null; };
  var ip = _v6(_xri) || _v6(_fwdFirst) || _xri || _fwdFirst || '';
  var ua = req.headers['user-agent'] || '';

  var ud = { client_ip_address: ip, client_user_agent: ua };

  // PII: SHA-256 com lowercase+trim (campo ausente é ignorado)
  var em = sha256(b.email);              if (em) ud.em = [em];
  var ph = sha256(normPhone(b.phone));   if (ph) ud.ph = [ph];
  if (b.name) {
    var parts = String(b.name).trim().split(/\s+/);
    ud.fn = [sha256(parts[0])];
    if (parts.length > 1) ud.ln = [sha256(parts.slice(1).join(' '))];
  }

  // Cookies da Meta: enviados sem hash (identificadores opacos)
  // Gera fbp no servidor se ausente (adblocker, primeira visita) e renova via Set-Cookie HTTP (imune ao cap de 7 dias do ITP)
  // Domain=.SEU-DOMINIO.com: sobrescreve o cookie do pixel (mesmo nome+domain+path = 1 cookie só)
  var fbpValue = (b.fbp && b.fbp.length > 0) ? b.fbp : ('fb.1.' + Date.now() + '.' + Math.floor(Math.random() * 2147483647));
  ud.fbp = fbpValue;
  res.setHeader('Set-Cookie', '_fbp=' + fbpValue + '; Max-Age=' + (90 * 24 * 3600) + '; Path=/; Domain=.SEU-DOMINIO.com; SameSite=Lax; Secure');
  if (b.fbc) ud.fbc = b.fbc;

  // País: ajustar para o ISO 3166-1 alpha-2 do público ('br', 'us', 'pt'...); fixo eleva o EMQ em eventos sem PII
  ud.country = [sha256('br')];

  // external_id: UUID persistente pós-consentimento (localStorage); conecta sessões do mesmo visitante
  if (b.external_id) ud.external_id = [sha256(b.external_id)];

  var eventData = {
    event_name:       b.event_name,
    event_time:       Math.floor(Date.now() / 1000),
    event_id:         b.event_id,
    action_source:    'website',
    event_source_url: b.page_url || 'https://SEU-DOMINIO.com', // page_url permite várias páginas sem hardcode
    user_data:        ud
  };
  if (b.value !== undefined || b.currency) {
    eventData.custom_data = {};
    if (b.value !== undefined) eventData.custom_data.value = parseFloat(b.value);
    if (b.currency) eventData.custom_data.currency = String(b.currency);
  }
  var payload = { data: [eventData] };
  // test_event_code: a env var tem prioridade (redireciona TODOS os eventos para Test Events);
  // o body serve a testes manuais pelo console. Remover a env var para voltar à produção.
  var testCode = process.env.META_CAPI_TEST_CODE || (b.test_event_code && typeof b.test_event_code === 'string' ? b.test_event_code : null);
  if (testCode) payload.test_event_code = testCode;

  var result = await sendToMeta(payload);
  if (!result.ok) {
    console.error('[CAPI] falha:', b.event_name, b.event_id, JSON.stringify(result));
    return res.status(500).json({ error: 'CAPI falhou' });
  }
  return res.status(200).json({ ok: true });
};
```

Após criar: configurar `META_CAPI_KEY` como env var encrypted no projeto Vercel (Settings → Environment Variables → tipo Sensitive). **Nunca colocar o token no código ou em arquivos commitados.**

#### 9e.1: Proxy de pixel first-party (`api/pixel-js.js`), RECOMENDADO

Serve `fbevents.js` do mesmo domínio via `/api/pixel-js`, em vez de `connect.facebook.net`. Bypassa adblockers que bloqueiam o domínio da Meta mas não o do site. Cache de navegador 1h (`max-age`), CDN 24h (`s-maxage=86400`): aquece o nó do CDN uma vez ao dia em vez de a cada request. Adicionar `<link rel="prefetch" href="/api/pixel-js">` no `<head>` para pré-baixar o script antes do tracking carregar.

**RC-B1 crítico:** o catch block DEVE ter `Cache-Control: no-store`. Sem isso o CDN cacheia o script de fallback de erro por até 24h e nenhum evento browser dispara nesses dias.

```js
// api/pixel-js.js: proxy de primeiro partido do fbevents.js
module.exports = async function handler(req, res) {
  var PIXEL_URL = 'https://connect.facebook.net/en_US/fbevents.js';
  var ctrl = new AbortController();
  var timeout = setTimeout(function() { ctrl.abort(); }, 4000);
  try {
    var upstream = await fetch(PIXEL_URL, { signal: ctrl.signal });
    clearTimeout(timeout);
    // Sempre 200: tag <script> com resposta não-200 não executa
    var body = await upstream.text();
    if (!upstream.ok) body = '// upstream error ' + upstream.status;
    // Navegador 1h (max-age); CDN 24h (s-maxage) aquece o nó uma vez ao dia
    var upstreamCC = upstream.headers.get('cache-control') || '';
    var browserAge = 3600;
    var m = upstreamCC.match(/max-age=(\d+)/);
    if (m) browserAge = Math.min(parseInt(m[1], 10), 3600);
    res.setHeader('Content-Type', 'application/javascript; charset=utf-8');
    res.setHeader('Cache-Control', 'public, max-age=' + browserAge + ', s-maxage=86400');
    res.setHeader('Access-Control-Allow-Origin', '*');
    return res.status(200).send(body);
  } catch (e) {
    clearTimeout(timeout);
    // RC-B1: no-store impede o CDN de cachear o fallback de erro por até 24h
    res.setHeader('Content-Type', 'application/javascript');
    res.setHeader('Cache-Control', 'no-store');
    return res.status(200).send('// pixel proxy unavailable');
  }
};
```

No snippet HTML (9c), a URL do script é `/api/pixel-js` (`t.src='/api/pixel-js'` dentro do IIFE). Registrar o SW (9l) para cache-first offline do proxy.

#### 9e.2: Não criar relay de `facebook.com/tr`

Não usar `fbq('set', 'endpoint', ...)` apontando para uma função que repassa hits a `facebook.com/tr`. A função sai do IP de datacenter da Vercel e a Meta não documenta aceitar `X-Forwarded-For`: o IP real do visitante se perde em todos os eventos de navegador. Cobertura para usuários com adblocker vem do CAPI no mesmo domínio (`api/capi.js`, 9e) e, se ativado no Events Manager, do Conversions API Gateway. O pixel envia direto para `facebook.com/tr`.

#### 9e.3: ITP bypass para `_fbp` (`api/fbp-init.js`), OPCIONAL

O `api/capi.js` do template já renova `_fbp` por `Set-Cookie` em todo evento: **omitir este endpoint** nesse caso. Criar só se o projeto não tiver CAPI consolidado. Safari ITP capa cookies definidos via JavaScript a 7 dias; `Set-Cookie` por header HTTP não sofre o cap (vida útil de 90 dias). Não chamar do frontend: renovação standalone.

Adaptar `Domain=.SEU-DOMINIO.com` e o nome do cookie de consentimento (`SEU_COOKIE_CONSENT=1`).

```js
// api/fbp-init.js: renova _fbp por Set-Cookie HTTP (ITP não aplica o cap de 7 dias)
module.exports = function handler(req, res) {
  var cookies = req.headers.cookie || '';
  if (cookies.indexOf('SEU_COOKIE_CONSENT=1') === -1) {
    return res.status(200).json({ ok: false }); // sem consentimento: não opera
  }
  var fbpMatch = cookies.match(/_fbp=([^;]+)/);
  var fbpValue = fbpMatch ? fbpMatch[1] : ('fb.1.' + Date.now() + '.' + Math.floor(Math.random() * 2147483647));
  res.setHeader('Set-Cookie', '_fbp=' + fbpValue + '; Max-Age=' + (90 * 24 * 3600) + '; Path=/; Domain=.SEU-DOMINIO.com; SameSite=Lax; Secure');
  return res.status(200).json({ ok: true });
};
```

#### 9f. Helpers JS no HTML (obrigatório com CAPI)

Adicionar no HTML antes do `loadTracking()`:

```js
// UUID para event_id e external_id
window._cId = function() { return crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2); };

// Ler cookie por nome
window._ck = function(n) {
  var m = document.cookie.match('(^|;)\\s*' + n + '\\s*=\\s*([^;]+)');
  return m ? m.pop() : '';
};

// external_id persistente pós-consentimento (conecta sessões do mesmo visitante)
window._extId = (function() {
  try {
    var k = '_app_eid';
    var v = localStorage.getItem(k);
    if (!v) { v = window._cId(); localStorage.setItem(k, v); }
    return v;
  } catch(e) { return ''; }
})();

// Envia evento ao CAPI server-side; retorna a promise do fetch (necessária para aguardar antes de um redirect)
window._capi = function(evName, evId, extra) {
  var fbc = window._ck('_fbc');
  // Fallback: reconstruir _fbc do fbclid da URL se o cookie não existe
  if (!fbc) {
    try {
      var _fc = new URLSearchParams(window.location.search).get('fbclid');
      if (_fc) fbc = 'fb.1.' + Date.now() + '.' + _fc;
    } catch(e) {}
  }
  var body = { event_name: evName, event_id: evId, fbp: window._ck('_fbp'), page_url: location.href };
  if (fbc) body.fbc = fbc;
  if (window._extId) body.external_id = window._extId;
  // PII de retorno: lida do localStorage se o visitante já converteu antes
  try {
    var _sp = JSON.parse(localStorage.getItem('_app_pii') || 'null');
    if (_sp) {
      if (_sp.em) body.email = _sp.em;
      if (_sp.ph) body.phone = _sp.ph;
      if (_sp.fn) body.name = _sp.fn;
    }
  } catch(e) {}
  if (extra) { for (var k in extra) if (extra.hasOwnProperty(k)) body[k] = extra[k]; }
  return fetch('/api/capi', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body), keepalive: true }).catch(function(){});
};
```

**Após Lead com PII:** salvar no localStorage para elevar o EMQ em eventos futuros do mesmo visitante:
```js
try { localStorage.setItem('_app_pii', JSON.stringify({ em: email, ph: phoneClean, fn: nome })); } catch(e) {}
```

**Cookie de consentimento (além de localStorage):** ao conceder consentimento (no modo `load`, ao rodar `loadTracking()`), gravar também `document.cookie = 'SEU_COOKIE_CONSENT=1; max-age=31536000; path=/; SameSite=Lax'`. É o que o servidor (`api/fbp-init.js`, CAPI antecipado) lê. Migração dentro de `loadTracking()`: setar o cookie se ausente (cobre usuários com consentimento antigo só em localStorage).

**CAPI antecipado para returning users:** IIFE antes do bloco de consentimento. Lê o cookie de consentimento; se presente, dispara `PageView` CAPI imediatamente (sem esperar scroll/clique). Grava `window._pvId`; `loadTracking()` usa `window._pvId = window._pvId || window._cId()` para preservar o ID e garantir deduplicação correta com o pixel.

**Advanced Matching** (`fbq('init')` com PII): ao chamar `fbq('init', PIXEL_ID, initData)`, ler a PII fornecida antes no lead form (guardada em `localStorage.SEU_STORAGE_PII` após o Lead). Injetar `em` (email lowercase), `ph` (E.164 digits), `fn`/`ln` (nome partido) quando disponíveis. A Meta hasheia internamente. Eleva o EMQ do PageView e de todos os eventos das sessões de quem já converteu:
```js
var _initData = window._extId ? { external_id: window._extId } : {};
try {
  var _pii = JSON.parse(localStorage.getItem('SEU_STORAGE_PII') || 'null');
  if (_pii) {
    if (_pii.em) _initData.em = _pii.em.toLowerCase().trim();
    if (_pii.ph) _initData.ph = _pii.ph; // já E.164 digits (ex: 5511999999999)
    if (_pii.fn) { var _nm = String(_pii.fn).trim().split(/\s+/); _initData.fn = _nm[0].toLowerCase(); if (_nm.length > 1) _initData.ln = _nm.slice(1).join(' ').toLowerCase(); }
  }
} catch(e) {}
fbq('init', 'SEU_PIXEL_ID', _initData);
```

#### 9g. Deduplicação obrigatória

Para cada evento rastreado: gerar `event_id` **antes** do par `fbq()` + `_capi()`. Sem `event_id` idêntico em ambos, a Meta conta o evento em dobro:

```js
var evId = window._cId();
fbq('track', 'Lead', { /* custom data */ }, { eventID: evId });
var leadCapi = window._capi('Lead', evId, { email: email, phone: phone, name: nome, value: 0, currency: 'BRL' });
// Se o Lead redireciona (checkout): aguardar entrega antes de sair
var go = function(){ location.href = checkoutUrl; };
Promise.race([leadCapi, new Promise(function(r){ setTimeout(r, 800); })]).then(go, go); setTimeout(go, 1500);
```

**Evento seguido de navegação** (Lead → checkout): `_capi()` retorna a promise do fetch; aguardar `Promise.race([capi, 800ms])` antes do redirect, com rede de segurança de 1,5 s. Navegação imediata cancela envios do pixel (img/iframe) e, em alguns navegadores in-app, o fetch keepalive.

**Eventos recomendados com CAPI** (LP de vendas): `PageView`, `ViewContent`, `ScrollDepth70`, `FAQOpen`, `PrecheckoutOpen`, `PrecheckoutEmailDigitado`, `PrecheckoutAbandono`, `Lead` (com PII: email + phone + nome). `VSLPlay`, `VSLProgress25`, `VSLProgress75`: apenas se o produto tiver VSL.

`InitiateCheckout` e `Purchase`: tipicamente disparados pela plataforma de pagamento (Hotmart, Kiwify) por servidor. Verificar se a plataforma já tem CAPI antes de duplicar na LP; não duplicar. O monitor de saúde (9n) vigia a cobertura de servidor do `InitiateCheckout` e denuncia se a plataforma parar de enviar.

**Origem da venda no checkout** (página de vendas externa → checkout da plataforma): o UTM da LP não chega ao checkout sozinho; a plataforma só registra a origem que vier no próprio link do checkout. No redirect, repassar `utm_source/medium/campaign/content/term` e, na Hotmart, também `sck` (`origem|meio|campanha`, é o que aparece em cada venda). Limpar cada valor antes: sem acento, só letras, números, ponto e hífen, até 30 caracteres (a Hotmart limita a 30, reserva `_`, e caractere especial pode impedir o checkout de abrir; nome de campanha de anúncio costuma ter espaço e colchete). Bloco em `try/catch`: nunca pode impedir o redirect. Validar com teste local da função que monta o link, nunca abrindo o checkout de produção (dispara InitiateCheckout real). Em outras plataformas, usar o parâmetro de origem equivalente.

**Compra de teste nunca no checkout de produção com pixel ativo**: vira Purchase real e contamina a otimização de campanha.

#### 9h. Microsoft Clarity (opcional: mapas de calor e gravações)

Instalar via `loadTracking()`. Custom tags para enriquecer gravações:

```js
clarity('set', 'vsl_played', 'true');          // no VSLPlay
clarity('set', 'vsl_progress', '25');           // no VSLProgress25
clarity('set', 'vsl_progress', '75');           // no VSLProgress75
clarity('set', 'scroll_depth_70', 'true');      // no ScrollDepth70
clarity('set', 'modal_opened', 'true');         // no PrecheckoutOpen
clarity('set', 'lead_captured', 'true');        // no Lead
clarity('set', 'traffic_source', utm_source);   // extraído da URL
clarity('set', 'exit_intent', 'true');          // via mouseleave clientY < 5 (desktop only)
```

**Analytics de sessão depois do pixel.** Injetar o script de gravação de sessão só quando a configuração do pixel chega (teto de 3 s), com a fila (`window.clarity`) criada antes para nenhuma tag se perder. O pixel + analytics (~340 KB) disputam rede com o elemento do LCP; o Clarity depois do pixel poupa o pixel. Custo: não grava quem sai antes. Avisar o contador (`window._mEv('cl')`, 9n) quando o script do Clarity carregar.

#### 9i. VSLProgress: padrão YouTube IFrame API

Adicionar `enablejsapi=1` no src do iframe. Criar `new YT.Player('id-do-iframe')` com `onReady` callback. Poll via `setInterval(5000)` verificando `getCurrentTime() / getDuration()`. Usar fila `onYouTubeIframeAPIReady` se a API ainda não carregou.

#### 9j. ScrollDepth70

Listener passivo no scroll, one-shot, dispara ao atingir 70%:
```js
var _sd70 = false;
window.addEventListener('scroll', function() {
  if (_sd70) return;
  var scrolled = (window.scrollY + window.innerHeight) / document.documentElement.scrollHeight;
  if (scrolled >= 0.7) {
    _sd70 = true;
    var evId = window._cId();
    fbq('trackCustom', 'ScrollDepth70', {}, { eventID: evId });
    window._capi('ScrollDepth70', evId);
  }
}, { passive: true });
```

#### 9k. Snapshots de portabilidade (antes do primeiro deploy)

Artefatos a gerar junto com a página (não existem prontos):
- `modal-precheckout.html`: modal standalone com CSS/HTML/JS isolados (sem dependências externas)
- `checkout-config.md`: copy do checkout, config do timer, imagem do produto, URL de oferta, parâmetros de pré-preenchimento testados, tracking IDs

#### 9l. Service Worker (`src/sw.js`): cache-first para pixel proxy

Cache-first com background revalidation para `/api/pixel-js`. Serve do cache instantaneamente e atualiza em segundo plano; cache miss vai à rede. `skipWaiting` + `clients.claim()` ativam e tomam controle da aba atual sem esperar reload. Intercepta só esse path (`pathname` check); tudo mais passa direto. Fallback duplo: Cache API falha → rede; rede falha → script vazio. O iOS Safari limpa o cache após 7 dias de inatividade: degradação graciosa para o CDN. O arquivo vai em `src/sw.js` (sai na raiz do site, escopo `/`); não há lista de arquivos a editar.

**RC-B2 crítico:** antes de `cache.put`, verificar `Cache-Control: no-store`. Sem isso o SW cacheia o script de fallback de erro do pixel proxy e o problema persiste mesmo após o upstream ser corrigido.

**Versionamento obrigatório:** ao mudar qualquer comportamento do SW, bumpar `CACHE_NAME` (ex: `app-pixel-v1` → `app-pixel-v2`). O activate handler deleta caches antigos via `skipWaiting`; sem o bump, visitantes com aba aberta continuam com o cache ruim até fechar o browser. Use um nome próprio do produto em `CACHE_NAME`.

```js
// src/sw.js: cache-first com revalidação em segundo plano, só para /api/pixel-js
var CACHE_NAME = 'app-pixel-v1'; // bumpar ao mudar comportamento: o activate apaga as versões anteriores
var PIXEL_PATH = '/api/pixel-js';

self.addEventListener('install', function(e) { self.skipWaiting(); });

self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(ks) {
      return Promise.all(
        ks.filter(function(k) { return k !== CACHE_NAME; })
          .map(function(k) { return caches.delete(k); })
      );
    }).then(function() { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function(e) {
  if (new URL(e.request.url).pathname !== PIXEL_PATH) return;
  e.respondWith(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.match(e.request).then(function(cached) {
        var networkRequest = fetch(e.request).then(function(r) {
          // RC-B2: não cachear resposta com no-store (fallback de erro do proxy)
          var cc = r.headers.get('cache-control') || '';
          if (r.ok && !cc.includes('no-store')) cache.put(e.request, r.clone());
          return r;
        }).catch(function() {
          return new Response('// pixel proxy unavailable',
            { headers: { 'Content-Type': 'application/javascript' } });
        });
        if (cached) { e.waitUntil(networkRequest); return cached; }
        return networkRequest;
      });
    }).catch(function() {
      // Cache API indisponível (ex: Safari privado): cai para a rede
      return fetch(e.request).catch(function() {
        return new Response('// pixel proxy unavailable',
          { headers: { 'Content-Type': 'application/javascript' } });
      });
    })
  );
});
```

Registrar no HTML (antes de `</body>`):
```html
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/sw.js').catch(function() {});
  });
}
</script>
```

`vercel.json` já deve ter `{ "source": "/sw.js", "headers": [{"key": "Cache-Control", "value": "no-cache"}] }` (ver 9a).

#### 9m. Healthcheck endpoints (`api/healthcheck.js` + `api/capi-check.js`)

Canary endpoints para monitoring automático (UptimeRobot, intervalo 5 min).

`api/healthcheck.js` confirma que o runtime Lambda carrega. Separado do CAPI porque um deploy com método errado pode deixar o HTML servindo (cache do CDN) enquanto todas as serverless functions retornam 500 em silêncio; o healthcheck é o que o monitor de uptime pinga para detectar esse cenário:

```js
// api/healthcheck.js: confirma que a Lambda carrega
module.exports = function handler(req, res) {
  res.status(200).json({ ok: true, ts: Date.now() });
};
```

`api/capi-check.js` testa a stack CAPI: Lambda carrega, `META_CAPI_KEY` presente, Graph API alcançável, token válido. Separado do `healthcheck.js` porque a CAPI pode falhar em silêncio (token inválido, deploy com bundles errados) enquanto o healthcheck básico retorna ok. **Nunca enviar evento ao pixel no healthcheck**: com monitor de 5 em 5 min são 288 eventos falsos por dia nas estatísticas de produção (mesmo com `test_event_code`), derrubando o EMQ e distorcendo a razão navegador:servidor. `debug_token` valida o token sem gerar evento:

```js
// api/capi-check.js: testa a stack CAPI sem gerar evento (debug_token valida o token)
const API_VER = 'v26.0';

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  var token = process.env.META_CAPI_KEY;
  if (!token) return res.status(500).json({ ok: false, error: 'META_CAPI_KEY ausente' });
  var ctrl = new AbortController();
  var t = setTimeout(function() { ctrl.abort(); }, 8000);
  try {
    var r = await fetch(
      'https://graph.facebook.com/' + API_VER + '/debug_token?input_token=' + encodeURIComponent(token) +
        '&access_token=' + encodeURIComponent(token),
      { signal: ctrl.signal }
    );
    clearTimeout(t);
    var data = await r.json(); var d = data && data.data;
    if (r.ok && d && d.is_valid === true) return res.status(200).json({ ok: true, token_valid: true });
    // sem detalhe do token na resposta (endpoint aberto)
    return res.status(500).json({ ok: false, error: (d && d.error && d.error.message) || (data.error && data.error.message) || 'token inválido' });
  } catch (e) {
    clearTimeout(t);
    return res.status(500).json({ ok: false, error: e.name === 'AbortError' ? 'timeout Graph API' : e.message });
  }
};
```

**Monitoramento de uptime** (após o primeiro deploy bem-sucedido): configurar quatro monitores em serviço gratuito (ex: UptimeRobot) com intervalo de 5 minutos e alerta por email:
1. `https://SEU-DOMINIO.com/`: HTTP monitor; detecta LP fora do ar (404/5xx)
2. `https://SEU-DOMINIO.com/api/healthcheck`: HTTP monitor; detecta Lambda quebrado (o caso em que o HTML serve pelo cache do CDN mas as serverless functions retornam 500)
3. `https://SEU-DOMINIO.com/api/tracking-health`: **Keyword monitor**; keyword `"ok":true`; detecta queda de cobertura de servidor ou dedup por `event_id` (resposta cacheada 10 min); EMQ baixo só aparece em `warnings`, sem alerta
4. `https://SEU-DOMINIO.com/api/capi-check`: **Keyword monitor** (tipo Keyword, não HTTP); keyword `"ok":true`; condição "keyword does not exist"; detecta falha na stack CAPI (token ausente, token inválido, Graph API fora). Não envia evento ao pixel

Com `api/selfcheck.js` (9n), acrescentar um quinto Keyword monitor nele (`"ok":true`).

Na API v3 do UptimeRobot, o monitor keyword exige `httpMethodType=GET` (o padrão é HEAD, que não devolve corpo, e o alerta dispararia sempre) e `timeout` no corpo da criação. Monitor recém-criado demora alguns segundos para entrar na listagem: esperar antes de atribuir contatos de alerta, senão ele nasce sem avisar ninguém.

Se `/api/healthcheck` cair: serverless functions quebradas → verificar o método de deploy (push no `main` ou CLI, nunca API REST com bundle local) e reverter por um deles.
Se `/api/capi-check` cair: stack CAPI com falha → verificar `META_CAPI_KEY` nas env vars da Vercel antes de reverter o deploy.

**Ler a razão navegador:servidor pela Graph API** (`GET /SEU_PIXEL_ID/stats?aggregation=event_source`), que conta só eventos de visitantes. Servidor > navegador é normal com CAPI + Conversions API Gateway ativos. A estatística por nome de evento da Meta só cobre ~26 h.

#### 9n. Medição da base e saúde dos eventos (obrigatório em página com tracking sob consentimento)

Por quê: a taxa de carregamento da Meta só registra visita com pixel disparado. Com consentimento, ela mede chegada × consentimento e não basta para avaliar a página. Proporção bruta servidor:navegador também engana (ver abaixo). As peças abaixo separam "ferramenta quebrada" de "base quebrada".

**Contador anônimo de chegadas** (`api/m.js` + snippet inline logo no início do `<head>`):
- Contagens diárias agregadas em Redis (Upstash gratuito via Vercel Marketplace, que injeta `UPSTASH_REDIS_REST_URL/TOKEN` ou `KV_REST_API_URL/TOKEN`). Eventos: chegou, carregou (`load`), interagiu, tracking ativo (chamar `window._mConsent()` dentro de `loadTracking()`), faixa de permanência na saída. Tráfego pago separado por `utm_source`/`utm_term` quando `utm_medium=paid` (url_tags dos anúncios: `utm_source={{site_source_name}}&utm_medium=paid&utm_term={{placement}}`; é a convenção que o snippet lê, adaptar nos dois lados se mudar)
- Recortes que explicam a taxa de carregamento: sistema do aparelho (`o=ios|and|out`, só a família), 1ª chegada do clique (`n=1`: fbclid da URL diferente do guardado em `localStorage.SEU_STORAGE_FBCLID`, gravado dentro de `loadTracking()`; nada sai do aparelho), configuração do pixel carregada (`cfg`), tempo até o envio (faixa fina `lt1|1to2|2to3` abaixo de 3 s) e até a saída (`lt3|3to6|6to10|gt10`)
- Medição independente da Meta: `px` (fbevents carregou), `cfg` (configuração do pixel baixada), `tr` (requisição a `facebook.com/tr` vista por `PerformanceObserver` de recursos), `err` (erro de script do próprio domínio), `lcp` (faixa do LCP, enviada ao esconder a página; aba oculta não gera LCP), `cl` (script do Clarity carregou)
- Funil da página, mesma via `window._mEv(evento, marco)`: `play` (capa do vídeo clicada), `vw` (marco do vídeo: tempo ou porcentagem), `sec` (seção que apareceu na tela, via `IntersectionObserver`, `x` = id da seção), `cta` (botão de compra clicado, `x` = posição do botão), `pc` (formulário do pré-checkout enviado, `x=send`). Chave `evento:marco`: um envio por marco, e o servidor valida o marco (regex por evento em `EXTRA`). Os ids de `sec` e de `cta` dependem da sua página: ajustar o `EXTRA` do `api/m.js`
- `tr` só é confiável no Android: no iPhone o Resource Timing quase nunca reporta a requisição a `facebook.com/tr`. Nunca concluir "o evento não chega à Meta" pelo `tr` sem separar por sistema; conferir com a Meta por `impression_device`
- Chrome headless carrega o pixel e não envia `/tr`: laboratório valida carregamento e configuração (`fbq.instance.configsLoaded`), envio só em aparelho real
- Saída: registrar também na primeira `visibilitychange` para `hidden`. No navegador do app, fechar a página nem sempre dispara `pagehide`
- Leitor de chegada soma só a chave principal (`<fonte>:arrive`): as chaves por posicionamento e por sistema são recortes da mesma chegada, e somá-las dobra o número
- Privacidade: sem cookie, ID, IP ou UA gravados; o contador só lê o fbclid já guardado no navegador e envia 0 ou 1. Dado agregado sem identificador não é dado pessoal. Nunca logar body/headers
- Corner cases: reload e voltar não contam (`navigation.type !== 'navigate'`); página prerender/`hidden` só conta ao ficar visível ou na primeira interação (webview pode reportar `hidden` por engano); fonte fora do padrão é descartada; sem env de storage o endpoint vira no-op (deploy seguro antes do storage)
- Sandbox: o bloco do início do `<head>` desliga pixel, Clarity, contador e checkout fora do domínio oficial (prévia da Vercel, localhost), com selo vermelho na tela. A trava equivalente no servidor é a do `api/capi.js`
- Relatório: `GET /api/m?k=METRICS_REPORT_KEY&days=N` (env própria, mín. 24 caracteres). Comparar chegadas pagas com cliques de saída do Ads Manager por dia e plataforma

**Monitor de saúde** (`api/tracking-health.js`): Dataset Quality API (`GET /dataset_quality?dataset_id=`, funciona com o mesmo token do CAPI) → EMQ, cobertura de servidor (meta da Meta: 75%) e dedup por `event_id`, incluindo InitiateCheckout (vigia a CAPI do checkout). Cache de CDN 10 min. UptimeRobot Keyword monitor `"ok":true`. Cobertura só reprova após `ENFORCE_FROM`, para a janela da Meta renovar depois de correções. EMQ baixo nunca reprova: oscila com volume pequeno e não pede ação, fica em `warnings`.

**Monitor local sem painel** (opcional, quando o dono não olha painéis; a skill não fornece o script local, só os endpoints): um script agendado na máquina do dono (launchd, cron) faz as verificações que exigem token de anúncios (espelho da CAPI religado, checkout sem servidor, proporção servidor:navegador, taxa de carregamento, chegada real, posicionamento indesejado, evento de teste, campanha sem entrega) e grava cada resultado num endpoint protegido por chave (`POST /api/monitor-status` → Redis, hash `mon`). O `api/tracking-health.js` lê esses resultados e reprova se algum falhar (exceto verificações só informativas, como taxa de carregamento, que vão para `warnings`) ou se o script ficar 26h+ sem notícia (verificação de nome `vigia`); o UptimeRobot já existente manda o e-mail. Token de anúncios nunca vai para a nuvem, nenhum monitor novo. Regras: resposta vazia da API conta como erro; erro de API só alerta na 3ª hora seguida.

**Contrato de tracking verificado por máquina** (`api/selfcheck.js`): a função busca o próprio HTML servido pelo CDN e confere marcas obrigatórias (init do pixel, PageView, helper do CAPI, contador, proxy do fbevents, modal, consentimento) e proibidas (o que foi removido e não pode voltar). Keyword monitor do UptimeRobot na resposta `"ok":true` manda e-mail quando algo sai do lugar. Motivo: marca removida por engano só apareceria dias depois no Events Manager.

**Guardião de deploy** (script local no launchd/cron, 1h; a skill não o fornece): compara o deploy no ar com o último commit, checa o contrato e a saúde dos eventos e, após duas falhas seguidas, reverte o commit (`git revert`) e dá push. Travas obrigatórias: só commit recente (24h), nunca o mesmo duas vezes, nunca reverter uma reversão.

**Proporção servidor:navegador é diagnóstico, não meta.** Servidor > navegador é o esperado com CAPI próprio + CAPI da Meta (se ativa) + visitantes com bloqueador. Nunca desligar fonte correta nem criar canal duplicado (ex: relay de `/tr`) para aproximar o número. Saúde = cobertura ≥75%, dedup por `event_id` ≥90% nos dois lados, nenhum evento indevido.

**Alerta só com ação.** Métrica que oscila (taxa de carregamento, EMQ) fica em `warnings` e é lida no acompanhamento; e-mail e notificação só para falha com ação clara (deploy fora de sincronia, contrato quebrado, fonte de evento parada). Pausa automática de campanha baseada em compra atribuída pela Meta é proibida: a atribuição chega com horas de atraso e venda real passa despercebida.

**Taxa de carregamento (visualizações da página ÷ cliques de saída): o que move e onde está o teto.**
- Pixel ao abrir a página (evento `load`) em vez de após interação é a maior alavanca de tracking: +16 pontos medidos numa página real, comparando o modo `gate` com o `load`
	- Exige política dizendo que a medição começa ao acessar (decisão jurídica do dono, ver 9c)
- Teto do tracking: parte das visitas pagas sai em menos de 3 s sem interagir, antes de configuração + envio do pixel (medido numa página real: ~4 em cada 10). Acima de ~70%, a alavanca é a intenção do clique (criativo, público, posicionamento)
- Enviar antes do `load` pode recuperar parte dessa perda (não testado) e custa ~25% no LCP em 4G lento: decidir com A/B de laboratório
- Leitura na Meta: por posicionamento sem Audience Network, por `impression_device`, só anúncios com destino no site (CTA "ver perfil" soma clique sem saída do app)
- Mix de criativo mudando durante o teste move a taxa sozinho: manter a campanha como está e registrar a participação de cada anúncio na leitura

**Imagem do LCP e o pixel no `load`.** O pixel no `load` depende de o `load` chegar cedo: uma imagem do LCP leve (ver passo 8) antecipa o evento. Medido numa página real em 4G lento: LCP 28% menor e pixel enviando 0,4 s antes.

**Procedimento para experimento no tracking com volta automática** (usar quando for mudar o comportamento do pixel, ex: carregar ao abrir a página em vez de após interação):
1. Colocar a mudança atrás de uma chave única no `<head>` (`window.TRACK_MODE`), enviada pelo contador em cada evento (`v=`): separa as versões mesmo com as duas no ar durante a troca de cache
2. Ordem dos commits: medição primeiro (fica mesmo se o teste voltar), ferramentas depois, experimento por último e sozinho. Tag de checkpoint antes do experimento
3. A política de privacidade muda no mesmo commit do comportamento: o texto precisa descrever quando a medição começa
4. Medir A/B em laboratório antes de publicar (Chrome headless, 4G lento, CPU 4x, eventos reais bloqueados): pixel + analytics (~340 KB) disputam rede com o elemento do LCP, e por isso o pixel dispara no `load` (com rede de segurança de alguns segundos), não na hora
5. Reversão. **Duas rotas, para dois casos:** o guardião de deploy desfaz uma quebra de contrato com `git revert` do commit que a causou. Já a volta do experimento é feita por substituição exata de texto (o modo e a política), não por `git revert`: o HTML minificado tem poucas linhas físicas, e outro commit na mesma linha faz o revert conflitar
6. Vigia local (script agendado, 1h; a skill não o fornece) reverte após 2h seguidas de quebra técnica: contrato, CAPI, tracking ativo < 80% das chegadas, pixel carregado < 60% das chegadas ou pixel enviado < 15% dos carregados, erro de script ≥ 20%, LCP > 4 s em ≥ 25% das visitas, chegadas < 70% dos cliques. Confere o deploy depois do push. Taxa de carregamento pior não reverte: amostra pequena é ruído, decisão humana
	- Limite de envio medido sobre as chegadas reverte por engano: a saída precoce deixa o envio em 45–65% das chegadas sem nada quebrado (medido numa página real). Medir o envio sobre os carregados
7. Fim de teste por amostra, nunca por data. Calcular antes quantos cliques de saída detectam a diferença esperada (exemplo: base de 52% e alvo de 67% pedem ~84), com parada antecipada só a 99% de confiança. Ler com intervalo de Wilson, em dias fechados (o dia corrente ainda assenta na Meta) e sem o dia da troca. Teto de gasto de campanha na Meta conta o acumulado desde o início: dimensionar por cliques × custo por clique + um dia de folga, somado ao já gasto

**Verificar mudança sem teste A/B:** uma mudança por vez; prova mecânica na página publicada (o que o celular baixa, em que ordem, se o evento sai); pisos de "não piorou" tirados do pior dia da linha de base em proporções que dependem só da página (pixel ÷ chegadas, configuração ÷ pixel, envio ÷ pixel, erros), lidos com tolerância a oscilação (uma leitura abaixo do piso pede nova leitura com mais chegadas e conferência da mistura de origem e sistema; desfazer só com queda sustentada em duas leituras seguidas ou quebra evidente); sinais de melhora independentes de campanha (PageView navegador ÷ servidor em `stats?aggregation=event_source`, LCP por fonte).

**Caminhos testados em laboratório e descartados:** pré-carregar a configuração do pixel (LCP +0,4 s), pré-carregar o pixel só depois da imagem do LCP (envio +0,5 s), configuração direto de `connect.facebook.net` em vez do rewrite (+0,1 s).

**Templates desta seção.** Snippet (início do `<head>`: modo do tracking, sandbox e contador anônimo):
```html
<script>
/* Modo do tracking: 'gate' = pixel só após interação (consentimento); 'load' = pixel ao abrir a página. Lido pelo bloco de consentimento e enviado ao contador. */
window.TRACK_MODE='load';
/* Sandbox: fora do domínio oficial (prévia da Vercel, localhost) nada sai para Meta, Clarity, contador nem checkout. Tudo vira aviso no console e um selo fixo na tela. */
window.LP_SANDBOX=!/(^|\.)SEU-DOMINIO\.com$/.test(location.hostname);
if(window.LP_SANDBOX){window.fbq=function(){try{console.info('[sandbox] pixel bloqueado:',[].slice.call(arguments,0,2).join(' '));}catch(e){}};window.clarity=function(){};
window._sandboxAviso=function(t){try{console.info('[sandbox] '+t);var d=document.createElement('div');d.textContent=t;d.style.cssText='position:fixed;left:50%;top:16px;transform:translateX(-50%);z-index:2147483647;background:#b00020;color:#fff;font:600 14px/1.4 system-ui,sans-serif;padding:10px 14px;border-radius:8px;max-width:90vw;box-shadow:0 4px 16px rgba(0,0,0,.3)';document.body.appendChild(d);setTimeout(function(){d.remove();},4000);}catch(e){}};
document.addEventListener('DOMContentLoaded',function(){var b=document.createElement('div');b.textContent='SANDBOX · tracking desligado';b.style.cssText='position:fixed;left:8px;bottom:8px;z-index:2147483647;background:#b00020;color:#fff;font:700 11px/1 system-ui,sans-serif;padding:6px 8px;border-radius:6px;opacity:.85;pointer-events:none';document.body.appendChild(b);});
document.addEventListener('click',function(e){var a=e.target&&e.target.closest&&e.target.closest('a[href*="DOMINIO-DO-CHECKOUT.com"]');if(a&&!e.defaultPrevented){e.preventDefault();window._sandboxAviso('Checkout bloqueado no sandbox');}});}
/* Contador anônimo de chegadas (api/m.js): sem cookie, sem ID enviado. Só lê o fbclid já guardado no navegador para saber se é 1ª chegada do clique. Mede a base independente da Meta. */
(function(){try{
if(window.LP_SANDBOX||navigator.webdriver||!navigator.sendBeacon||!window.URLSearchParams)return;
var n=performance.getEntriesByType&&performance.getEntriesByType('navigation')[0];
if(n&&n.type&&n.type!=='navigate')return;
var q=new URLSearchParams(location.search),paid=q.get('utm_medium')==='paid';
var s=paid?(q.get('utm_source')||'na'):'org',p=paid?(q.get('utm_term')||'na'):'';
var fbv=q.get('fbclid'),fb=fbv?1:0,ua=navigator.userAgent,os=/iPhone|iPad|iPod/.test(ua)?'ios':/Android/.test(ua)?'and':'out',nv=0;
try{nv=fbv&&localStorage.getItem('SEU_STORAGE_FBCLID')!==fbv?1:0}catch(e){}/* 1ª chegada deste clique neste aparelho: compara com o fbclid já guardado; nada sai do aparelho */
var rf=/(^|\.)(facebook|instagram|threads)\.com$/.test((function(){try{return new URL(document.referrer).hostname}catch(e){return ''}})())?1:0;
var sent={},eng=0,t0=0,on=0;
var M={vw:1,sec:1,cta:1,pc:1};/* eventos com marco: um envio por marco (chave evento:marco, ex. vw:5m, sec:preco) */
function b(e,x){var k=M[e]?e+':'+x:e;if(sent[k])return;sent[k]=1;navigator.sendBeacon('/api/m','e='+e+'&s='+encodeURIComponent(s.slice(0,40))+'&p='+encodeURIComponent(p.slice(0,40))+'&g='+eng+'&f='+fb+'&r='+rf+'&v='+window.TRACK_MODE+'&o='+os+(e==='arrive'?'&n='+nv:'')+(x?'&x='+x:''));}
window._mConsent=function(){if(on)b('consent');};
/* px = fbevents carregou; tr = requisição a facebook.com/tr saiu do navegador (evento do pixel de fato enviado); cl = Clarity carregou; play/vw/sec/cta/pc = funil: capa do vídeo clicada, marco do vídeo, seção vista, botão de compra, formulário enviado */
var pend=[];window._mEv=function(e,x){if(!/^(px|tr|cl|play|vw|sec|cta|pc)$/.test(e))return;if(on)b(e,x);else pend.push([e,x]);};/* antes do start (página oculta): guarda e envia no start */
var lcp=0;function lcpOut(){if(lcp)b('lcp',lcp<1500?'lt1500':lcp<2500?'1500to2500':lcp<4000?'2500to4000':'gt4000');}
function dt(){var d=(Date.now()-t0)/1000;return d<3?'lt3':d<6?'3to6':d<10?'6to10':'gt10';}
function dtf(){var d=(Date.now()-t0)/1000;return d<1?'lt1':d<2?'1to2':d<3?'2to3':dt();}/* envio do pixel: faixa fina abaixo de 3 s */
function start(){if(on)return;on=1;t0=Date.now();b('arrive');
if(document.readyState==='complete')b('loaded');else addEventListener('load',function(){b('loaded');});
['scroll','click','touchstart','keydown'].forEach(function(ev){addEventListener(ev,function(){if(!eng){eng=1;b('engaged');}},{passive:true,capture:true});});
if(window._trackingLoaded)b('consent');
pend.forEach(function(a){b(a[0],a[1]);});
/* cfg = configuração do pixel carregou (connect.facebook.net ou /fbcdn/); tr com faixa de tempo desde a chegada */
try{new PerformanceObserver(function(l){l.getEntries().forEach(function(en){if(/facebook\.com\/tr/.test(en.name))b('tr',dtf());else if(/signals\/config\//.test(en.name)&&en.responseEnd>0&&(en.transferSize>0||en.decodedBodySize>0||en.responseStatus===200))b('cfg');});}).observe({type:'resource',buffered:true});}catch(e){}
try{new PerformanceObserver(function(l){var es=l.getEntries();if(es.length)lcp=es[es.length-1].startTime;}).observe({type:'largest-contentful-paint',buffered:true});}catch(e){}
addEventListener('error',function(ev){if(ev.filename&&ev.filename.indexOf(location.origin)===0)b('err');},true);
document.addEventListener('visibilitychange',function(){if(document.visibilityState==='hidden'){lcpOut();b('exit',dt());}});/* no app, fechar o navegador nem sempre dispara pagehide: a primeira ocultação vale como saída */
addEventListener('pagehide',function(){lcpOut();b('exit',dt());});}
if(document.prerendering)document.addEventListener('prerenderingchange',start,{once:true});
else if(document.visibilityState==='hidden'){document.addEventListener('visibilitychange',function(){if(document.visibilityState==='visible')start();});
['focus','pointerdown','touchstart','scroll','keydown'].forEach(function(ev){addEventListener(ev,function(e){start();if(e.type!=='focus'&&!eng){eng=1;b('engaged');}},{passive:true,capture:true,once:true});});}/* webview que reporta hidden por engano: interação prova que é visível */
else start();
}catch(e){}})();
</script>
```

`api/_lib/redis.js` (compartilhado; o `_` no nome impede a Vercel de expor como rota):
```js
// Acesso ao Upstash Redis (REST) compartilhado pelas funções. Arquivo com "_" não vira rota na Vercel.
// Aceita os nomes padrão e qualquer prefixo da integração Upstash/KV (mesma regra de api/m.js).
var crypto = require('crypto');

function pick(re, skip) {
  var keys = Object.keys(process.env).filter(function(k) { return re.test(k) && !skip.test(k); });
  keys.sort(function(a, b) { return a.length - b.length; });
  return keys.length ? process.env[keys[0]] : null;
}

function redisCfg() {
  var url = process.env.UPSTASH_REDIS_REST_URL || process.env.KV_REST_API_URL ||
    pick(/(REST_API_URL|REDIS_REST_URL)$/, /READ_ONLY/);
  var token = process.env.UPSTASH_REDIS_REST_TOKEN || process.env.KV_REST_API_TOKEN ||
    pick(/(REST_API_TOKEN|REDIS_REST_TOKEN)$/, /READ_ONLY/);
  if (!url || !token || !/^https:\/\//.test(url)) return null;
  return { url: url.replace(/\/$/, ''), token: token };
}

async function redis(cfg, commands) {
  var r = await fetch(cfg.url + '/pipeline', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + cfg.token, 'Content-Type': 'application/json' },
    body: JSON.stringify(commands),
  });
  return r.json();
}

// Compara com METRICS_REPORT_KEY (mín. 24 caracteres) em tempo constante.
function keyOk(given) {
  var k = process.env.METRICS_REPORT_KEY;
  given = String(given || '');
  return !!k && k.length >= 24 && given.length === k.length &&
    crypto.timingSafeEqual(Buffer.from(given), Buffer.from(k));
}

module.exports = { redisCfg: redisCfg, redis: redis, keyOk: keyOk };
```

`api/m.js`:
```js
const crypto = require('crypto');

// Contador anônimo de chegadas: mede a base (quem realmente chega à página), independente da Meta.
// Grava SÓ contagens diárias agregadas (Redis hash m:AAAA-MM-DD). Sem cookie, sem ID, sem IP/UA gravados.
// LGPD: dado agregado sem identificador não é dado pessoal. NUNCA logar body nem headers aqui.
//
// POST (sendBeacon text/plain): e=<evento>&s=<fonte>&p=<posicionamento>&x=<faixa>&g=<0|1>
//   e: arrive | loaded | engaged | consent | exit | px | tr | err | lcp | play | vw | sec | cta | pc
//      play = capa do vídeo clicada; vw = marco do vídeo (x=1m|5m|10m|20m|25|50|75|100); sec = seção apareceu (x=id sem 'secao-');
//      cta = botão de compra clicado (x=hero|preco|final|float); pc = formulário enviado (x=send)
//      consent = tracking carregado; px = fbevents carregou; tr = requisição a facebook.com/tr saiu;
//      err = erro de script do próprio site; lcp = faixa do LCP (x=lt1500|1500to2500|2500to4000|gt4000)
//   v: modo do tracking (gate | load): separa as versões mesmo com as duas no ar durante a troca do cache
//   s: utm_source quando utm_medium=paid (ig, fb, an, msg...) ou "org"
//   p: utm_term ({{placement}} dos anúncios): só tráfego pago
//   x: faixa de permanência no exit (lt3 | 3to10 | 10to30 | gt30); g: já tinha interagido (1) ou não (0)
//   f: URL tinha fbclid (clique de anúncio); r: referrer é domínio da Meta
//   o: sistema do aparelho (ios | and | out), só a família, sem versão nem UA
//   n (só arrive): 1ª chegada deste clique neste aparelho (fbclid diferente do já guardado no navegador)
//   cfg: configuração do pixel carregou; x em tr e exit: segundos desde a chegada (lt3 | 3to6 | 6to10 | gt10)
//   Chaves extras por modo: v:<modo>:<pago|org>:os:<o>:<evento>, :arrive_first, :tr_t:<x>, :exit:<eng|noeng>:<x>
// GET ?k=<METRICS_REPORT_KEY>&days=N → relatório agregado
//
// Sem as env vars do Redis (qualquer prefixo da integração Upstash/KV) → no-op silencioso.

const EVENTS = new Set(['arrive', 'loaded', 'engaged', 'consent', 'exit', 'px', 'cfg', 'tr', 'err', 'lcp', 'cl']);  // cl = script do Clarity carregou
// Funil de vídeo, seções e cliques: um campo <fonte>:<evento>[:<marco>] por envio, marco validado aqui
const EXTRA = {
  play: /^$/,
  vw:   /^(1m|5m|10m|20m|25|50|75|100)$/,
  sec:  /^[a-z-]{2,20}$/,
  cta:  /^(hero|meio|preco|final|float)$/,  // ajustar aos ids dos seus botões de compra
  pc:   /^send$/,
};
const OSES   = new Set(['ios', 'and', 'out']);
const TEMPOS = new Set(['lt1', '1to2', '2to3', 'lt3', '3to6', '6to10', 'gt10']);  // tr usa faixa fina abaixo de 3 s
const POR_OS = new Set(['arrive', 'loaded', 'engaged', 'px', 'cfg', 'tr']);
const LCPS   = new Set(['lt1500', '1500to2500', '2500to4000', 'gt4000']);
const MODES  = new Set(['gate', 'load']);
const EXITS  = new Set(['lt3', '3to6', '6to10', 'gt10', '3to10', '10to30', 'gt30']);  // faixas antigas mantidas pro histórico
const TTL    = 180 * 24 * 3600;

// Aceita os nomes padrão e qualquer prefixo da integração Upstash/KV da Vercel
// (ex: STORAGE_KV_REST_API_URL): o nome varia conforme o "Custom Prefix" escolhido na instalação.
function pick(re, skip) {
  var keys = Object.keys(process.env).filter(function(k) { return re.test(k) && !skip.test(k); });
  keys.sort(function(a, b) { return a.length - b.length; });
  return keys.length ? process.env[keys[0]] : null;
}
function redisCfg() {
  var url = process.env.UPSTASH_REDIS_REST_URL || process.env.KV_REST_API_URL ||
    pick(/(REST_API_URL|REDIS_REST_URL)$/, /READ_ONLY/);
  var token = process.env.UPSTASH_REDIS_REST_TOKEN || process.env.KV_REST_API_TOKEN ||
    pick(/(REST_API_TOKEN|REDIS_REST_TOKEN)$/, /READ_ONLY/);
  if (!url || !token || !/^https:\/\//.test(url)) return null;
  return { url: url.replace(/\/$/, ''), token: token };
}

// Dia no fuso da conta de anúncios (aqui UTC-3; ajustar)
function dayKey(offsetDays) {
  var d = new Date(Date.now() - 3 * 3600 * 1000 - (offsetDays || 0) * 86400 * 1000);
  return d.toISOString().slice(0, 10);
}

function token(s) {
  s = String(s || '');
  return /^[A-Za-z0-9_.-]{1,40}$/.test(s) ? s : 'x';
}

async function redis(cfg, commands) {
  var r = await fetch(cfg.url + '/pipeline', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + cfg.token, 'Content-Type': 'application/json' },
    body: JSON.stringify(commands),
  });
  return r.json();
}

// Chave do relatório: env METRICS_REPORT_KEY (mín. 24 caracteres). Sem ela, relatório desativado (404).
function reportKey() {
  var k = process.env.METRICS_REPORT_KEY;
  return k && k.length >= 24 ? k : null;
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  var cfg = redisCfg();

  if (req.method === 'GET') {
    var expected = reportKey();
    var given = String((req.query && req.query.k) || '');
    if (!expected || given.length !== expected.length ||
        !crypto.timingSafeEqual(Buffer.from(given), Buffer.from(expected))) {
      return res.status(404).end();
    }
    if (!cfg) return res.status(200).json({ ok: false, error: 'storage não configurado' });
    if (req.query.selfcheck) { // diagnóstico: escreve, lê e apaga uma chave própria
      try {
        var out = await redis(cfg, [['HINCRBY', 'm:selfcheck', 'ping', 1], ['HGETALL', 'm:selfcheck'], ['DEL', 'm:selfcheck']]);
        return res.status(200).json({ ok: true, host: cfg.url.replace(/^https:\/\//, '').slice(0, 28), redis: out });
      } catch (e2) {
        return res.status(200).json({ ok: false, host: cfg.url.replace(/^https:\/\//, '').slice(0, 28), error: String(e2 && e2.message) });
      }
    }
    var days = Math.min(Math.max(parseInt(req.query.days, 10) || 14, 1), 90);
    var keys = []; for (var i = 0; i < days; i++) keys.push(dayKey(i));
    try {
      var out = await redis(cfg, keys.map(function(d) { return ['HGETALL', 'm:' + d]; }));
      var data = {};
      keys.forEach(function(d, idx) {
        var arr = (out[idx] && out[idx].result) || [], obj = {};
        for (var j = 0; j + 1 < arr.length; j += 2) obj[arr[j]] = parseInt(arr[j + 1], 10);
        if (arr.length) data[d] = obj;
      });
      return res.status(200).json({ ok: true, days: data });
    } catch (e) {
      return res.status(502).json({ ok: false, error: 'storage indisponível' });
    }
  }

  if (req.method !== 'POST') return res.status(405).end();
  if (!cfg) return res.status(204).end();

  // sendBeacon manda text/plain (string); curl/form manda objeto já parseado pela Vercel: aceitar os dois
  var b = req.body, q;
  if (typeof b === 'string') {
    if (!b || b.length > 300) return res.status(204).end();
    q = new URLSearchParams(b);
  } else if (b && typeof b === 'object' && !Array.isArray(b)) {
    if (JSON.stringify(b).length > 400) return res.status(204).end();
    q = new URLSearchParams(Object.keys(b).reduce(function(a, k) { a[k] = String(b[k]); return a; }, {}));
  } else {
    return res.status(204).end();
  }
  var e = q.get('e');
  if (!EVENTS.has(e) && !EXTRA[e]) return res.status(204).end();

  var s = token(q.get('s'));
  if (s === 'x') return res.status(204).end(); // fonte inválida: descarta em vez de poluir a contagem
  var key = 'm:' + dayKey(0);
  if (EXTRA[e]) {
    var xe = q.get('x') || '';
    if (!EXTRA[e].test(xe)) return res.status(204).end();
    try { await redis(cfg, [['HINCRBY', key, s + ':' + e + (xe ? ':' + xe : ''), 1], ['EXPIRE', key, TTL]]); } catch (err) {}
    return res.status(204).end();
  }
  var fields = [s + ':' + e];
  if (s !== 'org') fields.push(s + ':' + token(q.get('p')) + ':' + e);
  // chegada com fbclid = clique de anúncio de verdade (não revisita com UTM no histórico);
  // referrer da Meta confirma que veio do app. Numerador mais estrito para o teste de chegada.
  if (e === 'arrive') {
    if (q.get('f') === '1') fields.push(s + ':arrive_fbclid');
    if (q.get('r') === '1') fields.push(s + ':arrive_ref');
  }
  var o = OSES.has(q.get('o')) ? q.get('o') : 'x';
  if (POR_OS.has(e)) fields.push(s + ':os:' + o + ':' + e);
  if (e === 'arrive' && q.get('n') === '1') { fields.push(s + ':arrive_first', s + ':os:' + o + ':arrive_first'); }
  if (e === 'exit') {
    var x = EXITS.has(q.get('x')) ? q.get('x') : 'x';
    var g = q.get('g') === '1' ? 'eng' : 'noeng';
    fields = [s + ':exit:' + g + ':' + x];
  }
  // por modo do tracking: v:<gate|load>:<pago|org>:<evento>[:faixa]
  var v = MODES.has(q.get('v')) ? q.get('v') : 'x', vk = 'v:' + v + ':' + (s === 'org' ? 'org' : 'pago') + ':';
  if (e === 'lcp') {
    var l = LCPS.has(q.get('x')) ? q.get('x') : 'x';
    fields = [s + ':lcp:' + l];
    if (s !== 'teste' && s !== 'selftest') fields.push(vk + 'lcp:' + l);
  } else if (s !== 'teste' && s !== 'selftest') {  // validações ficam fora do recorte por modo
    if (e === 'exit') fields.push(vk + 'exit:' + g + ':' + x);
    else {
      fields.push(vk + e);
      if (POR_OS.has(e)) fields.push(vk + 'os:' + o + ':' + e);
      if (e === 'arrive' && q.get('n') === '1') fields.push(vk + 'arrive_first', vk + 'os:' + o + ':arrive_first');
      if (e === 'tr' && TEMPOS.has(q.get('x'))) fields.push(vk + 'tr_t:' + q.get('x'));
    }
  }

  var cmds = fields.map(function(f) { return ['HINCRBY', key, f, 1]; });
  cmds.push(['EXPIRE', key, TTL]);
  try { await redis(cfg, cmds); } catch (err) { /* falha silenciosa: contador nunca afeta o visitante */ }
  return res.status(204).end();
};
```

`api/tracking-health.js` (substituir `SEU_PIXEL_ID` e `ENFORCE_FROM`; sem monitor local, remover o bloco `monitor` e o `require` de `_lib/redis`):
```js
const API_VER = 'v26.0';
const lib = require('./_lib/redis');
const DATASET = 'SEU_PIXEL_ID';

// GET /api/tracking-health: saúde dos eventos pela Dataset Quality API da Meta (token META_CAPI_KEY).
// UptimeRobot Keyword monitor ("ok":true). Resposta cacheada 10 min no CDN: o monitor de 5 min não martela a Graph API.
//
// Também reprova pelo monitor local (script agendado → /api/monitor-status → Redis, hash "mon"):
// verificação com ok=false, "vigia" sem notícia há 26h+ (máquina desligada ou agendador parado) ou verificação velha (72h+).
// Sem monitor local, remova o bloco "monitor" e o lib/redis.
//
// Falha imediata: API inacessível; deduplicação por event_id < 90% (navegador ou servidor) em evento-chave.
// Aviso (sem e-mail): nota de correspondência (EMQ) < 6 em PageView/ViewContent.
// Falha a partir de ENFORCE_FROM: cobertura de servidor < 75% (meta da própria Meta) em evento-chave.
// A data existe porque a janela da Meta ainda contém dados de antes das correções; reprovar cedo gera alarme falso.
// InitiateCheckout: vem da CAPI da plataforma de checkout; a cobertura dele denuncia se o checkout parar de enviar por servidor.
const KEY_EVENTS   = ['PageView', 'ViewContent', 'PrecheckoutOpen', 'Lead', 'InitiateCheckout'];
const EMQ_EVENTS   = ['PageView', 'ViewContent'];
const ENFORCE_FROM = 'AAAA-MM-DD'; // 7 dias após o deploy (janela da Meta)
// Só reprova (e manda e-mail) o que pede ação. Métrica que oscila com volume pequeno vira aviso em "warnings".
const INFO_CHECKS  = ['carregamento'];

module.exports = async function handler(req, res) {
  var token = process.env.META_CAPI_KEY;
  if (!token) { res.setHeader('Cache-Control', 'no-store'); return res.status(500).json({ ok: false, error: 'META_CAPI_KEY ausente' }); }

  var fields = 'web{event_name,event_match_quality{composite_score},event_coverage{percentage,goal_percentage},' +
    'dedupe_key_feedback{dedupe_key,browser_events_with_dedupe_key{percentage},server_events_with_dedupe_key{percentage}}}';
  var url = 'https://graph.facebook.com/' + API_VER + '/dataset_quality?dataset_id=' + DATASET +
    '&fields=' + encodeURIComponent(fields) + '&access_token=' + encodeURIComponent(token);

  var ctrl = new AbortController();
  var t = setTimeout(function() { ctrl.abort(); }, 9000);
  var data;
  try {
    var r = await fetch(url, { signal: ctrl.signal });
    clearTimeout(t);
    data = await r.json();
    if (!r.ok || !data.web) throw new Error((data.error && data.error.message) || 'resposta sem web');
  } catch (e) {
    clearTimeout(t);
    res.setHeader('Cache-Control', 'public, s-maxage=300');
    return res.status(500).json({ ok: false, error: 'Dataset Quality API: ' + (e.name === 'AbortError' ? 'timeout' : e.message) });
  }

  var enforce = new Date().toISOString().slice(0, 10) >= ENFORCE_FROM;
  var failures = [], warnings = [], events = {};
  data.web.forEach(function(w) {
    if (KEY_EVENTS.indexOf(w.event_name) === -1) return;
    var emq = w.event_match_quality && w.event_match_quality.composite_score;
    var cov = w.event_coverage && w.event_coverage.percentage;
    var dd  = (w.dedupe_key_feedback || []).filter(function(x) { return x.dedupe_key === 'event_id'; })[0];
    var ddB = dd && dd.browser_events_with_dedupe_key && dd.browser_events_with_dedupe_key.percentage;
    var ddS = dd && dd.server_events_with_dedupe_key && dd.server_events_with_dedupe_key.percentage;
    events[w.event_name] = { emq: emq, coverage: cov, dedup_event_id_browser: ddB, dedup_event_id_server: ddS };

    if (ddB != null && ddB < 90) failures.push(w.event_name + ': event_id em ' + ddB + '% dos eventos de navegador');
    if (ddS != null && ddS < 90) failures.push(w.event_name + ': event_id em ' + ddS + '% dos eventos de servidor');
    var list = enforce ? failures : warnings;
    if (cov != null && cov < 75) list.push(w.event_name + ': cobertura de servidor ' + cov + '% (meta 75%)');
    if (EMQ_EVENTS.indexOf(w.event_name) !== -1 && emq != null && emq < 6) warnings.push(w.event_name + ': EMQ ' + emq + ' (mínimo 6)');
  });
  KEY_EVENTS.forEach(function(n) { if (!events[n]) warnings.push(n + ': sem dados na janela da Meta'); });

  var monitor = {};
  try {
    var cfg = lib.redisCfg();
    if (!cfg) throw new Error('storage não configurado');
    var rr = await lib.redis(cfg, [['HGETALL', 'mon']]);
    var flat = (rr[0] && rr[0].result) || [];
    for (var i = 0; i < flat.length; i += 2) monitor[flat[i]] = JSON.parse(flat[i + 1]);
    var agora = Date.now(), H = 3600 * 1000;
    if (!monitor.vigia) failures.push('monitor local: nunca reportou');
    else if (agora - monitor.vigia.ts > 26 * H) failures.push('monitor local parado há ' + Math.round((agora - monitor.vigia.ts) / H) + 'h: máquina desligada ou agendador parado');
    Object.keys(monitor).forEach(function(c) {
      var m = monitor[c];
      if (!m.ok) (INFO_CHECKS.indexOf(c) !== -1 ? warnings : failures).push('[' + c + '] ' + m.msg + (m.acao ? ' → ' + m.acao : ''));
      else if (c !== 'vigia' && agora - m.ts > 72 * H) failures.push('[' + c + '] sem atualização há ' + Math.round((agora - m.ts) / H) + 'h');
    });
  } catch (e) {
    failures.push('monitor local: leitura falhou (' + e.message + ')');
  }

  res.setHeader('Cache-Control', 'public, s-maxage=600, stale-while-revalidate=300');
  return res.status(200).json({ ok: failures.length === 0, enforce_from: ENFORCE_FROM, failures: failures, warnings: warnings, events: events, monitor: monitor });
};
```

`api/monitor-status.js` (só com monitor local; envs `METRICS_REPORT_KEY` e as do Redis):
```js
// api/monitor-status.js: resultado das verificações do monitor local, guardado no Redis (hash "mon").
// POST (header x-k = METRICS_REPORT_KEY) {check, ok, msg, acao} → grava com carimbo de hora.
// GET  (?k=METRICS_REPORT_KEY) → todas as verificações.
// Quem avisa é o /api/tracking-health: reprova se alguma verificação falhou ou se o monitor parou de reportar.
// O token de anúncios nunca sai da máquina local.
var lib = require('./_lib/redis');

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  var cfg = lib.redisCfg();
  if (req.method === 'POST') {
    if (!lib.keyOk(req.headers['x-k'])) return res.status(404).end();
    if (!cfg) return res.status(500).json({ ok: false, error: 'storage não configurado' });
    var b = req.body || {};
    if (typeof b === 'string') { try { b = JSON.parse(b); } catch (e) { b = {}; } }
    if (!/^[a-z0-9-]{2,40}$/.test(String(b.check || ''))) return res.status(400).json({ error: 'check inválido' });
    if (b.remove === true) { await lib.redis(cfg, [['HDEL', 'mon', b.check]]); return res.status(200).json({ ok: true }); }
    var v = { ok: b.ok === true, msg: String(b.msg || '').slice(0, 400), acao: String(b.acao || '').slice(0, 400), ts: Date.now() };
    await lib.redis(cfg, [['HSET', 'mon', b.check, JSON.stringify(v)]]);
    return res.status(200).json({ ok: true });
  }
  if (req.method === 'GET') {
    if (!lib.keyOk(req.query && req.query.k)) return res.status(404).end();
    if (!cfg) return res.status(500).json({ ok: false, error: 'storage não configurado' });
    var r = await lib.redis(cfg, [['HGETALL', 'mon']]);
    var flat = (r[0] && r[0].result) || [], out = {};
    for (var i = 0; i < flat.length; i += 2) out[flat[i]] = JSON.parse(flat[i + 1]);
    return res.status(200).json({ ok: true, checks: out });
  }
  return res.status(405).end();
};
```

`api/selfcheck.js` (ajustar as marcas ao HTML servido da sua página):
```js
// api/selfcheck.js: verifica o CONTRATO DE TRACKING na página que o visitante realmente recebe.
// Busca o próprio HTML servido pelo CDN e confere marcas obrigatórias e proibidas, além das env vars críticas.
// UptimeRobot monitora como Keyword ("ok":true). Resposta cacheada 5 min.
// Marcas = trechos literais do HTML servido (minificado): ajustar à sua página.
const OBRIGATORIAS = [
  ["fbq('init'", 'init do pixel'],
  ['window._capi', 'helper do CAPI'],
  ["fbq('track','PageView'", 'PageView no pixel'],
  ['_mConsent', 'contador anônimo de chegadas'],
  ['skipOpenbridge', 'desligamento do espelho da Meta'],
  ['/api/pixel-js', 'proxy de primeiro partido do fbevents'],
  ['SEU_COOKIE_CONSENT', 'controle de consentimento'],
  ['window.TRACK_MODE=', 'modo do tracking (gate/load)'],
  ['_mEv', 'medição independente do envio do pixel (px/tr)'],
];
const PROIBIDAS = [
  ['fb-relay', 'relay de facebook.com/tr (removido de propósito)'],
];

module.exports = async function handler(req, res) {
  var host = req.headers['x-forwarded-host'] || req.headers.host || 'www.SEU-DOMINIO.com';
  var falhas = [];

  if (!process.env.META_CAPI_KEY) falhas.push('env META_CAPI_KEY ausente');

  var ctrl = new AbortController();
  var t = setTimeout(function() { ctrl.abort(); }, 8000);
  try {
    var r = await fetch('https://' + host + '/', { signal: ctrl.signal });
    clearTimeout(t);
    if (!r.ok) throw new Error('home respondeu ' + r.status);
    var html = await r.text();
    if (html.length < 20000) falhas.push('HTML servido tem ' + html.length + ' bytes (ajustar o piso ao tamanho real da página)');
    OBRIGATORIAS.forEach(function(m) { if (html.indexOf(m[0]) === -1) falhas.push('faltando: ' + m[1]); });
    PROIBIDAS.forEach(function(m) { if (html.indexOf(m[0]) !== -1) falhas.push('não deveria estar presente: ' + m[1]); });
  } catch (e) {
    clearTimeout(t);
    falhas.push('não consegui ler a home: ' + (e.name === 'AbortError' ? 'timeout' : e.message));
  }

  res.setHeader('Cache-Control', falhas.length ? 'public, s-maxage=60' : 'public, s-maxage=300');
  return res.status(200).json({ ok: falhas.length === 0, falhas: falhas, verificado_em: new Date().toISOString() });
};
```

### 10. Confirmar e orientar

Informar ao usuário:
1. Caminhos dos arquivos gerados (Guia, DS, vercel.json, api/capi.js e demais `api/`)
2. Lista de campos `⬜` que restaram
3. **Gerar preview da paleta**, sem esperar pedido: criar `preview-paleta.html` em `{pasta-base}/` (fora de `src/`, portanto fora do deploy) com swatches de todas as cores do DS, exemplos de tipografia (H1, H2, H3, body) e variantes do botão CTA. Se browser disponível: abrir com `mcp__claude-in-chrome__navigate`. Se browser indisponível: exibir tabela markdown com nome do token, hex e papel semântico. Em ambos os casos perguntar: "Essa paleta está certa?" e só avançar com aprovação
4. Próximo passo após a paleta aprovada: construir a copy da LP e depois o HTML com tracking completo. Avisar que dois itens precisam ser providenciados antes do deploy: (a) a copy completa da LP (textos de todas as seções, headline, CTAs, depoimentos); (b) instalação do Meta Pixel no HTML e configuração dos eventos de conversão (PageView, Lead, etc.) conforme o passo 9 deste skill
5. **Análise de performance:** com Clarity e a planilha do Apps Script, o Claude consegue analisar heatmap de atenção por scroll, dados de leads (criativo, canal, botão de origem, evolução temporal) e performance de campanhas no Meta Ads (CPL, criativo, placement) diretamente via API.

---

## Regras

- **Nunca** usar valores de nenhum produto como placeholder: nem paleta, nem Pixel ID, nem URLs, nem copy. Cada produto começa do zero.
- O Guia e o DS são documentos vivos: atualizar conforme a LP evolui.
- **Tracking não é opcional em LPs de infoproduto.** Sem Pixel + CAPI, o Meta Ads Manager não consegue otimizar campanhas e o EMQ fica baixo. Verificar `api/capi.js` + `META_CAPI_KEY` antes de qualquer deploy que vá receber tráfego pago.
- **`META_CAPI_KEY` fica no `.env` da raiz do projeto (para uso local) e como env Sensitive na Vercel.** O `.env` precisa estar no `.gitignore`, e a chave nunca é commitada. Ao gravar, usar `CHAVE=VALOR` sem aspas e sem espaços ao redor do `=`. Se a chave já existir no `.env`, atualizar o valor (não duplicar a linha). `VERCEL_TOKEN`, quando preciso, é exportado na hora e nunca salvo.
- **Nunca peça login ou senha do Facebook Business.** Só o Pixel ID e o Access Token, que o usuário cola no chat.
- Nunca inclua eventos sem que façam sentido para o tipo de página.
- **Self-hosting de assets, sem exceções:** toda imagem, fonte e ícone deve estar em `assets/` e subir no deploy. Thumbnails YouTube: baixar e converter para WebP + AVIF onde menor. Google Fonts: self-hospedar subset latin WOFF2. Ícones: SVG inline.
- Quando boas práticas universais evoluírem (nova regra de performance, novo padrão de consentimento LGPD), atualizar este skill para que todos os produtos futuros se beneficiem.
