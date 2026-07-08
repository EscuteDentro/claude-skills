---
name: subir-pagina-top
description: >
  Bootstrapa e publica uma landing page de infoproduto (Hotmart, Kiwify, etc.) no
  Vercel com domínio personalizado, Meta Pixel + CAPI server-side, headers de
  segurança HTTP, cache de assets, robots.txt, sitemap e checklist de SEO.
  Tracking é parte obrigatória do deploy — não é etapa opcional.
allowed-tools: Read, Write, Bash
---

> **Instalação:** copiar esta pasta para `.claude/skills/subir-pagina-top/` no projeto e criar o command apontando para o SKILL.md. Ver [README.md](./README.md) para instruções completas e pré-requisitos.

---

# /subir-pagina-top — LP de Infoproduto do Zero ao Ar

Cria os arquivos de fundação e conduz o deploy completo de uma LP de conversão:

- **`Guia de Construção da Página.md`** — regras, protocolo, checklists, SEO+AEO, performance, LGPD
- **`design-system.json`** — tokens visuais, princípios e decisões de componente
- **Meta Pixel + CAPI** — tracking obrigatório embutido no fluxo de deploy

O conteúdo agnóstico (checklists, performance, SEO+AEO, LGPD, responsividade) é gerado com base em boas práticas universais. O conteúdo específico (paleta, IDs de tracking, URLs, configuração) é coletado junto com o usuário — nunca inventado nem emprestado de outro produto.

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
- **Copy**: textos de cada seção — headline, subtítulo, corpo, CTAs, depoimentos
- **Tracking IDs**: Pixel ID (buscar `fbq('init','`) e outros scripts de tracking presentes
- **Checkout URL**: href dos botões de CTA
- **Preço**: texto do elemento de preço

Com esses dados extraídos, pré-preencher o DS (paleta, tipografia, tracking IDs) e o Guia (configuração, checkout URL, preço) sem precisar perguntar o que já está na página. Perguntar só o que não foi possível extrair. No passo 5, atenção especial a: self-hosting de todos os assets (imagens e fontes), cookie banner LGPD (ausente na Hotmart nativa), passo 9 (infraestrutura de deploy).

**LP existente querendo otimizar:** se Guia + DS já existem, pular passos 2–4 e executar o passo de revisão abaixo, depois ir aos checklists. Se Guia + DS ainda não existem, gerar agora com base na LP atual.

> **Revisão de Guia + DS existentes:** antes de ir aos checklists, verificar: (1) seção Performance do Guia — está nas 19 regras atuais? (2) DS tokens de cor — há contraste suficiente? (3) DS performance — `formato_imagem` inclui AVIF? (4) Seção LGPD — banner implementado e mecanismo de consent documentado? (5) Tracking IDs — ainda válidos? Atualizar os campos defasados antes de rodar o checklist.

---

## O Que Fazer

### 1. Definir pasta do projeto

**Se estiver no ambiente Fluxo Criativo:** ler `meus-produtos/.ativo` para obter o produto ativo. Se não houver produto ativo, perguntar qual usar. Usar `meus-produtos/{ativo}/entregas/paginas/` como pasta base.

**Se não houver `meus-produtos/`:** perguntar ao usuário:
> "Em qual pasta você quer salvar os arquivos do projeto? (ex: `meu-produto/paginas/`) — ou deixe em branco para usar a pasta atual."

Usar a resposta como `{pasta-base}` para todos os passos seguintes. Criar a pasta se não existir.

### 2. Obter referência visual ou construir junto

Perguntar ao usuário:

> "Você tem uma página de referência — um site, LP ou marca cujo visual se aproxima do que você quer? Cole o link."

**Verificar disponibilidade:** se `mcp__claude-in-chrome__*` não responder, informar ao usuário e aplicar o fallback das 3 perguntas abaixo para todo este passo — não travar.

**Se o usuário colar uma URL:** visitar com `mcp__claude-in-chrome__navigate` + `mcp__claude-in-chrome__read_page`. Para cores e fontes, usar `mcp__claude-in-chrome__javascript_tool` com `getComputedStyle` — necessário porque muitos valores estão em CSS calculado, não no HTML estático. Extrair:
- Paleta dominante (cores de fundo, texto, CTA)
- Famílias de fonte e hierarquia tipográfica
- Tom geral: formal/informal, minimalista/denso, quente/frio
- Elementos de layout (proporções, uso de imagem, espaçamento)

Usar o que foi extraído para construir o DS — não perguntar o que já foi visto. Não copiar; usar como direção de intenção visual.

**Se a página bloquear acesso automatizado** (Cloudflare, login, erro de carregamento): informar ao usuário e cair no fallback das 3 perguntas abaixo.

**Se não tiver URL:** fazer 3 perguntas objetivas:
- Qual o tom emocional do produto? (ex: calmo e científico / vibrante e motivacional / sofisticado e premium)
- Qual a cor que o produto mais evoca? (pode ser uma sensação, não necessariamente um hex)
- Há alguma marca ou produto que admira visualmente, mesmo que de outro nicho?

### 3. Coletar configuração do site

Se existir um arquivo `perfil.md` na pasta do projeto, ler e extrair o que estiver disponível.

**Migração Hotmart:** a URL já foi visitada nos Casos de uso — não pedir de novo. Pular diretamente para extração dos campos abaixo.

**Produto novo (URL do passo 2 é de outro site, referência visual):** NÃO extrair campos abaixo dessa URL — é de outra marca, teria IDs e checkout errados. Ir direto à tabela de campos obrigatórios.

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
| Meta Pixel ID | Sim — se usar Meta Ads |
| Meta CAPI Access Token | Sim — se usar Meta Ads. Obter em: Meta Business Suite → Events Manager → Dataset → Configurações → API de Conversões → Gerar token de acesso |
| Checkout URL | Sim |
| Plataforma de vendas | Sim |
| Preço | Sim |
| Nome do professor/criador | Sim |
| Microsoft Clarity ID | Não |
| YouTube Video ID (VSL) | Não — apenas se produto tiver VSL |
| Instagram / YouTube / TikTok | Não |
| og:title (sugerir baseado no produto) | Não |
| og:description | Não |

Campos sem resposta → marcar com `⬜ a preencher`.

### 4. Criar pasta de destino

Criar `{pasta-base}` agora se não existir. Sem perguntas — avançar.

### 5. Gerar o Guia de Construção

**Se pasta foi criada agora (produto novo):** gerar diretamente. **Se pasta pré-existia:** verificar se `Guia de Construção da Página.md` existe; se sim, perguntar (a) atualizar seções defasadas ou (b) recriar do zero.

**Ao criar:** gerar o Guia com todo o conteúdo agnóstico (regras de performance, SEO+AEO, responsividade, LGPD, anti-padrões universais) diretamente, sem copiar de nenhum produto específico. Preencher as seções de configuração com os dados coletados no passo 3.

**Seções de configuração** (específicas do produto — preencher com dados do passo 3):
- `⬜ Configuração do site` — URL, email, Pixel ID, checkout URL, plataforma, preço, criador
- `⬜ Arquivos e caminhos` — paths do produto
- `⬜ Tracking` — IDs e nomes de CTA do produto

**Seções agnósticas** (gerar com boas práticas universais):
- Protocolo de trabalho e checklist de avaliação
- SEO + AEO completo (blocos 1 a 9)
- Schemas JSON-LD, Validação e Testes
- Anti-padrões estruturais — apenas os universais de LP
- Performance (19 regras) — agnóstica de produto
- LGPD — status inicial `⬜ PENDENTE — banner a implementar`

**Salvar em:** `{pasta-base}/Guia de Construção da Página.md`

### 6. Gerar o Design System JSON

**Se pasta foi criada agora (produto novo):** gerar diretamente. **Se pasta pré-existia:** verificar se `design-system.json` existe; se sim, perguntar (a) atualizar paleta/tokens ou (b) recriar do zero.

**Ao criar:** gerar o DS com a estrutura completa. Preencher a configuração específica do produto; gerar o conteúdo agnóstico diretamente.

**Campos específicos do produto** (preencher com dados coletados):
- `nome`, `produto`, `gerado_em`
- `paleta` — construir com base na referência visual ou respostas do passo 2. Derivar tokens:
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
- `mood` — tom visual em 2–4 palavras
- `observacoes` — origem das cores e decisões iniciais
- `tracking` — todos os IDs como `⬜ a configurar`
- `lgpd.status_atual` — `⬜ a implementar`

**Campos agnósticos** (gerar com boas práticas universais):
- `principios` (12 itens) — verificar os que expressam tom emocional específico e adaptar ao produto
- `copy_tom` — regras de "!" e celebração (universais para LP de infoproduto)
- Toda a estrutura de tokens: `tipografia`, `icones`, `border_radius`, `espacamento`, `sombras`, `botao`, `cards`, `tabelas`, `listas`, `alternancia_secoes_8D`, `divisores_de_secao`, `performance`, `responsividade`, `ab_testing`, `lgpd`, `acessibilidade`

**Salvar em:** `{pasta-base}/design-system.json`

### 7. Checklist de responsividade — executar após construir a LP (não agora)

| Verificação | Como checar |
|---|---|
| **Mobile 390px** | DevTools → 390px; sem overflow horizontal; sem texto cortado; CTAs tocáveis |
| **Desktop 900px+** | Abrir em 1440px; tipografia segue escala DS (×1.75 · ×1.5 · ×1.22 · +1px) |
| **Layouts multi-coluna** | Só dentro de `@media (min-width: 900px)` — CSS base (mobile) intocado |
| **Wrapper semântico** | Cada coluna tem seu wrapper HTML; nunca `grid-row`/`grid-column` em filhos |
| **Touch targets** | Todo elemento clicável com área ≥ 44×44px (WCAG 2.5.5) |
| **Imagem LCP** | `fetchpriority="high"` sem `loading="lazy"` acima da dobra |
| **Fontes desktop** | Nunca definir font-size desktop fora do bloco `@media (min-width: 900px)` |
| **Breakpoint único** | Um único bloco `@media (min-width: 900px)` consolidado — sem duplicatas |

### 8. Checklist de performance — executar antes do primeiro deploy (não agora)

Performance mobile é princípio central — impacto direto em conversão de tráfego pago. Meta: Lighthouse mobile ≥ 90.

| Verificação | Como executar |
|---|---|
| **Self-hosting total** | `grep -o 'src="https://[^"]*"' index.html` — não deve retornar nenhuma imagem |
| **Fontes self-hosted** | `grep "fonts.google\|fonts.gstatic" index.html` — não deve aparecer nada |
| **Ícones SVG inline** | `grep "font-awesome\|fa-" index.html` — não deve aparecer nada |
| **Thumbnail LCP self-hosted** | WebP local em `assets/`, não URL do YouTube. srcset com versão mobile |
| **CSS reset imagens** | `img { display: block; max-width: 100%; height: auto; }` no reset global |
| **width + height em todas as imgs** | `grep -c '<img' index.html` vs `grep -c 'width=' index.html` — iguais |
| **loading=lazy em tudo abaixo do fold** | `grep -n '<img' index.html \| grep -v 'loading='` — só hero e LCP thumbnail |
| **font-display: optional** | `grep 'font-display' index.html` — nunca `swap` |
| **preconnect para 3rd parties** | heatmap, pixel de ads, domínio do checkout |
| **vercel.json com cache headers** | `max-age=31536000, immutable` para `/assets/(.*)` |
| **HTML minificado no deploy** | html-minifier-terser antes de codificar (sem `--minify-js`) |
| **Iframes de vídeo com facade** | depoimentos: 0 iframes no HTML. VSL principal: facade obrigatório |
| **Tracking fora do `<head>`** | `grep -n "fbq\|clarity\|gtag" index.html \| grep -v "loadTracking\|function\|//"` — zero fora do consent |
| **AVIF com fallback WebP** | imagens grandes com `<picture>` source AVIF + img WebP. Exceção: VSL thumbnail (LCP) |
| **Sem redirects desnecessários** | `curl -I https://SEU-DOMINIO.com/` — sem `Location:` no apex |
| **Payload total** | `du -sh assets/` — meta < 1.6MB total |
| **Prefetch checkout** | `grep 'rel="prefetch"' index.html` — URL do checkout presente |
| **Lighthouse mobile** | DevTools → Lighthouse → Mobile, aba anônima, URL de produção. Score ≥ 90, perseguir 95+ |

**Dependências** (instalar se não tiver): `brew install webp libavif`
**Conversão WebP:** `cwebp -q 65 foto.png -o foto.webp` (fotos); `cwebp -q 80 logo.png -o logo.webp` (logos).
**Conversão AVIF:** `dwebp foto.webp -o /tmp/tmp.png && avifenc -q 65 --speed 6 /tmp/tmp.png foto.avif` — sempre comparar tamanhos; se avif >= webp, descartar avif e usar WebP puro.

### 9. Infraestrutura de deploy e tracking (obrigatório antes de ir ao ar)

#### 9a. vercel.json

Criar na raiz de `{pasta-base}/`:
```json
{
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
    { "source": "/robots.txt",  "headers": [{"key": "Cache-Control", "value": "public, max-age=86400"}] },
    { "source": "/sitemap.xml", "headers": [{"key": "Cache-Control", "value": "public, max-age=86400"}] }
  ]
}
```

> `X-Frame-Options: SAMEORIGIN` — padrão seguro para LP standalone. Remover apenas se a LP precisar ser embarcada em iframe por domínio externo.

#### 9b. Script de deploy (deploy.py)

Script Python que lê os arquivos da pasta, minifica o HTML com `html-minifier-terser`, codifica em base64 e faz POST na API da Vercel (`/v13/deployments`). Configurar: path da pasta, token da Vercel, lista de arquivos raiz, lista de assets a excluir. Incluir o diretório `api/` no payload.

**Pré-requisito:** conta na [Vercel](https://vercel.com) (plano gratuito suficiente para LP). Necessário para: criar o projeto, configurar a env var `META_CAPI_KEY` e obter o token de deploy.

> Se o usuário não tiver um `deploy.py` existente, gerar o script completo agora.

#### 9c. Meta Pixel — snippet base (obrigatório)

Inserir logo após o `<head>`, antes de qualquer outro script. Substituir `{PIXEL_ID}` pelo Pixel ID coletado no passo 3. Não duplicar se já existir (procurar por `fbq('init'`):

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
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '{PIXEL_ID}');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id={PIXEL_ID}&ev=PageView&noscript=1"/></noscript>
<!-- End Meta Pixel -->
```

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
Adicionar `data-cta` em todos os botões/links que levam ao checkout, caso ainda não tenham classe identificável.

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

#### 9e. CAPI — Meta Conversions API (obrigatório para campanha de ads)

**Por que CAPI:** Pixel browser é bloqueado por adblockers e Safari ITP. CAPI envia os mesmos eventos server-side, garantindo cobertura completa e melhorando o EMQ (Event Match Quality) no Meta.

Criar `api/capi.js` na raiz de `{pasta-base}/`. Substituir `{PIXEL_ID}` e `https://SEU-DOMINIO.com` pelos valores reais:

```js
const crypto = require('crypto');

const PIXEL_ID = '{PIXEL_ID}';
const API_VER  = 'v20.0';

function sha256(val) {
  if (!val) return undefined;
  return crypto.createHash('sha256').update(String(val).toLowerCase().trim()).digest('hex');
}

// Normaliza para E.164 sem o '+'. Cobre números brasileiros.
// Para outros países: adaptar a lógica de DDI e comprimento.
function normPhone(phone) {
  if (!phone) return undefined;
  var d = String(phone).replace(/\D/g, '');
  if (d.startsWith('0'))  d = '55' + d.slice(1);
  if (d.length === 11)    d = '55' + d;
  if (d.length === 10)    d = '55' + d;
  if (d.startsWith('5555') && d.length >= 14) d = d.slice(2);
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
    if ((res.status >= 500 || res.status === 429) && attempt < 2) return await sendToMeta(payload, attempt + 1);
    return { ok: false, data };
  } catch (e) {
    if (attempt < 2) return await sendToMeta(payload, attempt + 1);
    return { ok: false, error: e.message };
  }
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();
  var b = req.body || {};
  if (!b.event_name || !b.event_id) return res.status(400).json({ error: 'event_name e event_id obrigatórios' });

  // x-real-ip primeiro (captura IPv6 quando disponível); x-forwarded-for como fallback
  var ip = (req.headers['x-real-ip'] || req.headers['x-forwarded-for'] || '').split(',')[0].trim() || '';
  var ua = req.headers['user-agent'] || '';
  var ud = { client_ip_address: ip, client_user_agent: ua };

  var em = sha256(b.email);             if (em) ud.em = [em];
  var ph = sha256(normPhone(b.phone));  if (ph) ud.ph = [ph];
  if (b.name) {
    var parts = String(b.name).trim().split(/\s+/);
    ud.fn = [sha256(parts[0])];
    if (parts.length > 1) ud.ln = [sha256(parts.slice(1).join(' '))];
  }
  if (b.fbp) ud.fbp = b.fbp;
  if (b.fbc) ud.fbc = b.fbc;
  ud.country = [sha256('br')];  // ajustar para ISO 3166-1 alpha-2 do país ('us', 'pt', etc.)
  if (b.external_id) ud.external_id = [sha256(b.external_id)];

  var eventData = {
    event_name: b.event_name, event_time: Math.floor(Date.now() / 1000),
    event_id: b.event_id, action_source: 'website',
    event_source_url: 'https://SEU-DOMINIO.com',  // substituir pela URL canônica
    user_data: ud
  };
  if (b.value !== undefined || b.currency) {
    eventData.custom_data = {};
    if (b.value !== undefined) eventData.custom_data.value = parseFloat(b.value);
    if (b.currency) eventData.custom_data.currency = String(b.currency);
  }

  var result = await sendToMeta({ data: [eventData] });
  if (!result.ok) {
    console.error('[CAPI] falha:', b.event_name, b.event_id, JSON.stringify(result));
    return res.status(500).json({ error: 'CAPI falhou' });
  }
  return res.status(200).json({ ok: true });
};
```

Após criar: configurar `META_CAPI_KEY` como env var encrypted no projeto Vercel (Settings → Environment Variables → tipo Sensitive). **Nunca colocar o token no código ou em arquivos commitados.**

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

// external_id persistente pós-consent (conecta sessões cross-visit)
window._extId = (function() {
  try {
    var k = '_app_eid';
    var v = localStorage.getItem(k);
    if (!v) { v = window._cId(); localStorage.setItem(k, v); }
    return v;
  } catch(e) { return ''; }
})();

// Enviar evento ao CAPI server-side
window._capi = function(evName, evId, extra) {
  var fbc = window._ck('_fbc');
  // Fallback: reconstruir _fbc do fbclid na URL se cookie ausente
  if (!fbc) {
    try {
      var _fc = new URLSearchParams(window.location.search).get('fbclid');
      if (_fc) fbc = 'fb.1.' + Date.now() + '.' + _fc;
    } catch(e) {}
  }
  var body = { event_name: evName, event_id: evId, fbp: window._ck('_fbp') };
  if (fbc) body.fbc = fbc;
  if (window._extId) body.external_id = window._extId;
  // PII de retorno: ler do localStorage se visitante já converteu antes
  try {
    var _sp = JSON.parse(localStorage.getItem('_app_pii') || 'null');
    if (_sp) {
      if (_sp.em) body.email = _sp.em;
      if (_sp.ph) body.phone = _sp.ph;
      if (_sp.fn) body.name = _sp.fn;
    }
  } catch(e) {}
  if (extra) { for (var k in extra) if (extra.hasOwnProperty(k)) body[k] = extra[k]; }
  fetch('/api/capi', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body), keepalive: true }).catch(function(){});
};
```

**Após Lead com PII:** salvar no localStorage para elevar EMQ em eventos futuros do mesmo visitante:
```js
try { localStorage.setItem('_app_pii', JSON.stringify({ em: email, ph: phoneClean, fn: nome })); } catch(e) {}
```

#### 9g. Deduplicação obrigatória

Para cada evento rastreado: gerar `event_id` **antes** do par `fbq()` + `_capi()`. Sem `event_id` idêntico em ambos, o Meta conta o evento em dobro:

```js
var evId = window._cId();
fbq('track', 'Lead', { /* custom data */ }, { eventID: evId });
window._capi('Lead', evId, { email: email, phone: phone, name: nome, value: 0, currency: 'BRL' });
```

**Eventos que devem ter CAPI** (lista de exemplo para LP de vendas com VSL):
`PageView`, `ViewContent`, `VSLPlay`, `VSLProgress25`, `VSLProgress75`, `ScrollDepth70`, `FAQOpen`, `PrecheckoutOpen`, `PrecheckoutEmailDigitado`, `PrecheckoutAbandono`, `Lead`.

`InitiateCheckout` e `Purchase`: tipicamente disparados pela plataforma de pagamento (Hotmart, Kiwify) — verificar se a plataforma já tem CAPI antes de duplicar na LP.

#### 9h. Microsoft Clarity (opcional — mapas de calor e gravações)

Instalar via `loadTracking()` após consentimento. Custom tags para enriquecer gravações:

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

#### 9i. VSLProgress — padrão YouTube IFrame API

Adicionar `enablejsapi=1` no src do iframe. Criar `new YT.Player('id-do-iframe')` com `onReady` callback. Poll via `setInterval(5000)` verificando `getCurrentTime() / getDuration()`. Usar fila `onYouTubeIframeAPIReady` se API ainda não carregou.

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

- `modal-precheckout.html` — modal standalone com CSS/HTML/JS isolados (sem dependências externas)
- `checkout-config.md` — copy do checkout, config do timer, imagem do produto, URL de oferta, parâmetros de pré-preenchimento testados, tracking IDs

### 10. Confirmar e orientar

Informar ao usuário:
1. Caminhos dos arquivos gerados (Guia, DS, vercel.json, deploy.py, api/capi.js)
2. Lista de campos `⬜` que restaram
3. **Gerar preview da paleta** — sem esperar pedido: criar `preview-paleta.html` em `{pasta-base}/` com swatches de todas as cores do DS, exemplos de tipografia (H1, H2, H3, body) e variantes do botão CTA. Perguntar: "Essa paleta está certa?" — só avançar com aprovação.
4. Próximo passo após paleta aprovada: construir a copy da LP e depois o HTML com os eventos de tracking configurados neste skill.

---

## Regras

- **Nunca** usar valores de nenhum produto como placeholder — nem paleta, nem Pixel ID, nem URLs, nem copy. Cada produto começa do zero.
- O Guia e o DS são documentos vivos — atualizar conforme a LP evolui.
- **Tracking não é opcional em LPs de infoproduto.** Sem Pixel + CAPI, o Meta Ads Manager não consegue otimizar campanhas e o EMQ fica baixo. Verificar `api/capi.js` + `META_CAPI_KEY` antes de qualquer deploy que vá receber tráfego pago.
- **Pixel ID e Access Token ficam no `.env` da raiz do projeto.** O `.env` precisa estar no `.gitignore`. O `META_CAPI_KEY` é sensível e nunca deve ser commitado. Ao gravar, usar `CHAVE=VALOR` sem aspas e sem espaços ao redor do `=`. Se a chave já existir no `.env`, atualizar o valor (não duplicar a linha).
- **Nunca peça login ou senha do Facebook Business.** Só o Pixel ID e o Access Token, que o usuário cola no chat.
- Nunca inclua eventos sem que façam sentido para o tipo de página.
- **Self-hosting de assets, sem exceções:** toda imagem, fonte e ícone deve estar em `assets/` e subir no deploy. Google Fonts: self-hospedar subset latin WOFF2. Ícones: SVG inline.
- Quando boas práticas universais evoluírem (nova regra de performance, novo padrão de consent LGPD), atualizar este skill para que todos os produtos futuros se beneficiem.
