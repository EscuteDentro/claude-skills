# Guia de Construção da Página — Template Universal

> Documento permanente. Template universal com valores preenchidos para o **{Produto}**.
> Campos marcados com ⬜ são site-específicos — substituir ao usar este Guia em outro produto.
> O DS JSON é um componente deste guia — tokens visuais e decisões de design de componente.

---

## ⬜ Configuração do site

Todos os valores específicos do site em um único lugar. Ao clonar para outro produto, substituir estes.

| Campo | {Produto} |
|---|---|
| **Nome do produto** | {Produto} |
| **URL canônica** | `https://{dominio}.com.br` |
| **Idioma** | `pt-BR` (HTML `lang`) / `pt_BR` (og:locale) |
| **CNPJ** | {CNPJ} |
| **Email de contato** | {email} |
| **Meta Pixel ID** | `{PIXEL_ID}` |
| **Microsoft Clarity ID** | `{CLARITY_ID}` |
| **Checkout URL** | `https://pay.hotmart.com/{CHECKOUT_CODE}?checkoutMode=10&hotfeature=51` |
| **Plataforma de vendas** | Hotmart |
| **Preço** | R$ 483,00 (BRL) |
| **YouTube Video ID (VSL)** | `{VIDEO_ID}` |
| **Professor** | {Nome Sobrenome} |
| **Instagram** | `@{produto}` → `https://www.instagram.com/{produto}` |
| **YouTube canal** | `@{produto}` → `https://www.youtube.com/@{produto}` |
| **TikTok** | `@{produto}` → `https://www.tiktok.com/@{produto}` |
| **og:title** | Aula com prática gratuita para sentir na pele o que é meditar de verdade |
| **og:description** | Método que traduz a sabedoria ancestral para o ocidental moderno. Perceba resultados desde as primeiras sessões. |
| **og:image** | `assets/og-image.png` — logo centralizada com `scale(1.25)`, canvas 1200×630 `#E8FAFF`. Source: `og-image-preview.html`. Regenerar se logo mudar. |
| **Favicon** | `assets/favicon.png` — estrela âmbar `#E8A820` sobre `#E8FAFF`, 256×256. Source: `favicon-export.html`. |

---

## ⬜ Arquivos e caminhos

| Arquivo | Caminho | Conteúdo |
|---|---|---|
| **HTML de trabalho** | `~/{pasta}/escute-dentro/paginas/index.html` | LP completa (~1900 linhas) |
| **Design System (DS)** | `{Produto}/Marketing/Página de vendas/design-system.json` | Tokens + regras completas (ver domínios abaixo) |
| **Auxiliares (raiz do domínio)** | `~/{pasta}/escute-dentro/paginas/` | `robots.txt`, `llms.txt`, `sitemap.xml` |
| **Política de privacidade** | `~/{pasta}/escute-dentro/paginas/privacidade.html` | Deploy em `/privacidade` no Vercel |
| **Template A/B** | `{Produto}/Marketing/Testes A-B/template.md` | Template e naming convention de testes |
| **Log de testes A/B** | `{Produto}/Marketing/Testes A-B/` | Relatórios datados por teste |

**Snapshots de portabilidade:** antes de publicar, criar dois arquivos de referência para facilitar migração futura de plataforma:
- `modal-precheckout.html` — modal standalone com CSS/HTML/JS isolados, sem dependência da LP
- `checkout-config.md` — copy do checkout (headline, preço, garantia), config do timer (duração, cor, texto), imagem do produto, URL, parâmetros de pré-preenchimento, tracking

**Regra de assets:** tudo que a página exibe fica em `assets/` e sobe junto no deploy. Nenhuma imagem depende de CDN externo de terceiros (Hotmart, plataforma de e-mail, drives, etc.). Se o terceiro mudar a URL ou tirar o arquivo do ar, a página quebra sem aviso. Exceções aceitáveis: thumbnails do YouTube (CDN do próprio YouTube, estáveis enquanto o vídeo existir), Google Fonts e Font Awesome (CDNs usados por milhões de sites, com SLA implícito).

---

## Design System

Cada domínio tem seção própria no `design-system.json`. Consultar pelo nome da chave.

| Domínio | Chave no DS | O que cobre |
|---|---|---|
| **— Design Visual —** | | |
| Princípios visuais | `principios` | 12 princípios (legibilidade, mobile-first, CTA, contraste, tipografia, sistema) |
| Paleta de cores | `paleta` + `nota_contraste` | Tokens de cor + notas de contraste WCAG |
| Tipografia | `tipografia` | Escala mobile base 17px; desktop: H1 ×1.75 · H2 ×1.5 · H3 ×1.22 · body +1px; fórmula em `escala_desktop_formula` |
| Ícones | `icones` | Cor `brand_vivid`, 48px wrapper / 44px SVG, filled SVG sem stroke; exclusivo para ícones |
| Border-radius | `border_radius` | Escala xs(6px) → full(9999px); nenhum elemento com radius 0 |
| Espaçamento | `espacamento` | Base 8px; escala xs → 3xl; mobile: xl=48px, 2xl=64px, 3xl=80px |
| Sombras | `sombras` | Tokens `card`, `elevated`, `btn_cta` |
| Hero | `hero` | Fundo `#E8FAFF`, logo, margens H1/subtítulo/lista na seção hero |
| Componentes | `padroes_de_bloco`, `botao`, `cards`, `tabelas`, `listas` | Regras CSS e variantes de cada componente |
| Alternância de seções | `alternancia_secoes_8D` | Fundo/texto por bloco da estrutura 8D (16 blocos) |
| Divisores de seção | `divisores_de_secao` | 3 tipos permitidos; proibido: qualquer divisor que pareça botão |
| Tom visual | `mood` + `observacoes` | "calma-energizada"; origem das cores (logo → brand e glacial) |
| **— Produto · Comportamento —** | | |
| Performance | `performance` | Lazy loading, preload, WebP, Core Web Vitals, fetchpriority, defer |
| Responsividade | `responsividade` | Mobile-first, breakpoints sm/md/lg, touch targets ≥44px, safe-area; escala desktop via multiplicadores (ver `escala_desktop_formula`) |
| **— Operação —** | | |
| Tracking | `tracking` | Meta Pixel (eventos atualizados: Lead substitui InitiateCheckout), Clarity, scroll-markers, data-track, UTM, GTM |
| Modal pré-checkout | `precheckout_modal` | Campos, DDI input-addon, validação, fluxo de dados, arquitetura JS |
| A/B Testing | `ab_testing` | Estratégia, o que testar primeiro, significância estatística, log |
| LGPD | `lgpd` | Consentimento, ferramentas, status atual, base legal |
| Acessibilidade | `acessibilidade` | Foco visível, touch targets, aria em modais e SVGs, alt texts, reduced motion, contraste |
| **— SEO + AEO —** | | |
| SEO + AEO | ver seção abaixo | Princípios detalhados na seção dedicada deste Guia |

---

## Schemas JSON-LD ativos

`FAQPage` · `Course` · `Person` · `Organization` · `VideoObject`

Condicional: `AggregateRating` (requer avaliações verificáveis e visíveis na página — aguarda reviews no Hotmart ou Google Reviews)

---

## ⬜ Tracking — Mapa completo de eventos

Arquitetura dupla: **Pixel browser + CAPI server-side** em paralelo. Deduplicação por `event_id` (UUID via `crypto.randomUUID()` gerado antes de cada par `fbq()` + `_capi()`). Meta deduplica dentro de 48h.

Todos os eventos dentro ou protegidos por `loadTracking()` — função que só dispara após consentimento LGPD.

| Evento | Tipo | Gatilho | Parâmetros | Pixel | CAPI | Clarity tag | Fonte |
|---|---|---|---|---|---|---|---|
| `PageView` | Pixel padrão | Disparo de `loadTracking()` | — | ✓ | ✓ | — | Nossa LP |
| `ViewContent` | Pixel padrão | 3s após consentimento | `value: 483, currency: 'BRL'` | ✓ | ✓ | — | Nossa LP |
| `VSLPlay` | Custom | Clique no facade do VSL | — | ✓ | ✓ | `vsl_played: 'true'` | Nossa LP |
| `VSLProgress25` | Custom | 25% do vídeo assistido (poll 5s via YT IFrame API) | — | ✓ | ✓ | `vsl_progress: '25'` | Nossa LP |
| `VSLProgress75` | Custom | 75% do vídeo assistido | — | ✓ | ✓ | `vsl_progress: '75'` | Nossa LP |
| `ScrollDepth70` | Custom | Scroll até 70% da altura da página | — | ✓ | ✓ | `scroll_depth_70: 'true'` | Nossa LP |
| `FAQOpen` | Custom | Toggle de qualquer `<details>` do FAQ | `question: [texto]` | ✓ | ✓ | — | Nossa LP |
| `PrecheckoutOpen` | Custom | Clique em qualquer `.btn-cta` (abre modal) | `origin: cta-hero/cta-meio/cta-preco/cta-final` | ✓ | ✓ | `modal_opened: 'true'` | Nossa LP |
| `PrecheckoutEmailDigitado` | Custom | Blur no campo email (`length > 3`) | `origin: [btn]` | ✓ | ✓ | — | Nossa LP |
| `PrecheckoutAbandono` | Custom | Fechar modal sem submit (×, Escape, clique fora) | `origin`, `had_email` | ✓ | ✓ | — | Nossa LP |
| `Lead` | Pixel padrão | Submit do pré-checkout (campos válidos) | `content_name, value: 483, currency: 'BRL'` | ✓ | ✓ + PII | `lead_captured: 'true'` | Nossa LP |
| `InitiateCheckout` | Hotmart nativo | Carregar pg de pagamento na Hotmart | — | ✓ (HM) | ✓ (HM CAPI) | — | Hotmart |
| `Purchase` | Hotmart nativo | Compra confirmada | — | ✓ (HM) | ✓ (HM CAPI) | — | Hotmart |
| Exit intent | — | Mouse sai pelo topo (desktop, `clientY < 5`) | — | — | — | `exit_intent: 'true'` | Nossa LP |

**Nota InitiateCheckout (pendente especialista, 2026-07-08):** a coluna CAPI do IC mostra `✓ (HM CAPI)` mas não está confirmado em produção — observamos zero eventos CAPI para IC vindo da Hotmart. Purchase CAPI está confirmado. Aguardando especialista para definir se adicionamos IC na nossa LP (com inflação ~40-50% dos eventos) ou aceitamos 0% CAPI no IC.

**Clarity tags adicionais:** `traffic_source: utm_source` (capturado em `loadTracking()`).

**CAPI — arquitetura:**
- Endpoint: `api/capi.js` (Vercel serverless, incluso no deploy via `deploy_v2.py`)
- Token: `META_CAPI_KEY` (env var encrypted no Vercel — nunca em código)
- Pixel ID: `{PIXEL_ID}` (hardcoded no `api/capi.js`)
- PII no Lead: email + phone (E.164, DDI 55 prefixado) + nome — hasheados SHA-256 `toLowerCase().trim()`
- `_fbc` reconstruído de `fbclid` na chegada, dentro de `loadTracking()` — 90 dias, `SameSite=Lax`
- `country`: `sha256('br')` hardcoded — eleva EMQ em eventos sem PII
- `external_id`: UUID gerado pós-consent em `localStorage._app_eid`, sha256 antes do envio no CAPI — conecta sessões cross-visit. **Também enviado no `fbq('init')` como plain text** (`fbq('init', PIXEL_ID, { external_id: window._extId })`) — Meta normaliza internamente para SHA-256 e consegue cruzar com o valor do CAPI.
- `event_source_url`: dinâmico — `_capi()` envia `page_url: window.location.href` e `api/capi.js` usa esse valor (fallback: `'https://www.{dominio}.com.br'`). Corrige o hardcoded anterior sem `www`.
- **`_fbc` fallback de URL** (fix 4a, 2026-07-08): se cookie `_fbc` ausente, reconstruir de `fbclid` na URL (`fb.1.{timestamp}.{fbclid}`). Só incluir no body se não-vazio — não enviar string vazia.
- **IP do usuário** (fix 4b, 2026-07-08): `capi.js` usa `x-real-ip` antes de `x-forwarded-for` — captura IPv6 quando disponível. Verificado em produção: IP não-vazio, formato correto.
- **PII de retorno** (fix 4c, 2026-07-08): após Lead, salvar PII em `localStorage._app_pii` (`{em, ph, fn}`). `_capi()` lê automaticamente e inclui em todos os eventos futuros do visitante — eleva EMQ de PageView/ViewContent para quem já converteu.
- **Dedup rate esperada**: CAPI captura eventos de usuários com adblocker que o browser pixel não alcança. Esses eventos CAPI-only não geram deduplicação — é o comportamento correto. Taxa de dedup de 60–80% reflete 20–40% de cobertura incremental via CAPI, não um problema. Para diagnosticar: verificar no Events Manager se usuários *sem adblocker* têm dedup próximo de 100%.
- Pattern obrigatório para qualquer evento com CAPI:
  ```js
  var evId = window._cId();
  if (typeof fbq === 'function') fbq('track', 'EventName', {}, { eventID: evId });
  window._capi('EventName', evId, { /* extra fields */ });
  ```

**PRODUCT_VALUE:** lido dinamicamente de `document.querySelector('[data-price]').dataset.price`. Para atualizar preço: mudar `data-price` no elemento `.preco-alt` (e o texto visível). O fallback hardcoded na linha seguinte do JS também deve ser atualizado.

**VSLProgress — padrão YouTube IFrame API:** iframe com `enablejsapi=1` → `new YT.Player('vsl-iframe', ...)` → poll `setInterval(5000)` → `p.getCurrentTime() / p.getDuration()`. Fallback via `onYouTubeIframeAPIReady` se API ainda não carregou.

**Microsoft Clarity** (ID: `{CLARITY_ID}`): gravação de sessão e mapas de calor. Tags customizadas via `clarity('set', 'key', 'value')` — ver coluna "Clarity tag" acima. Acessar em clarity.microsoft.com → Recordings e Heatmaps.

**Consent gate**: `localStorage.getItem('edm_consent') === 'granted'` — em visitas recorrentes, `loadTracking()` dispara automaticamente no carregamento.

**UTM — estrutura padrão para Meta Ads (configurar em cada anúncio):**

| Parâmetro | Valor | Tipo |
|---|---|---|
| `utm_source` | `MetaAds` | fixo |
| `utm_medium` | `paid` | fixo |
| `utm_campaign` | `{{campaign.name}}` | dinâmico |
| `utm_content` | `{{ad.name}}` | dinâmico |
| `utm_term` | `{{placement}}` | dinâmico (parâmetro personalizado) |
| `utm_adset` | `{{adset.name}}` | dinâmico (parâmetro personalizado) |

Linktree (bio Instagram, TikTok, YouTube): `utm_source=linktree&utm_medium=social&utm_campaign=bio` — fixo, configurado nos links de destino dentro do Linktree.

Esses parâmetros são capturados por `captureUtms()` no modal e gravados na Sheet — colunas: UTM Source, UTM Medium, UTM Campaign, UTM Content, UTM Term, UTM Adset, Duplicado, Obs Duplicação. Ao criar campanha nova no Meta, replicar essa estrutura em "Parâmetros de URL" no adset ou anúncio.

---

## Modal pré-checkout

Intercepta todos os `.btn-cta`. Coleta nome + email + telefone antes de redirecionar ao Hotmart.

**Campos do formulário:**

| Campo | Tipo | Validação |
|---|---|---|
| Nome | `input[type=text]` | Obrigatório (não vazio) |
| E-mail | `input[type=email]` | Regex `/^[^\s@]+@[^\s@]+\.[^\s@]+$/` |
| DDI | input-addon (ver abaixo) | Não pode estar vazio no submit |
| Telefone | `input[type=tel]` | ≥ 7 dígitos internacionais |

**Campo DDI — input addon:**

Badge estático (`<span class="pc-ddi-badge" id="pc-ddi-badge">`) + input numérico (`<input class="pc-ddi-input" id="pc-ddi">`), agrupados em `.pc-ddi-group`.

- Badge mostra `🇧🇷 +` no carregamento (value="55"). Atualiza no blur: `flag + ' +'` se DDI reconhecido, `'+'` se desconhecido.
- DDI_MAP: ~120 países. Vive dentro do mesmo IIFE do modal para acessar `showError`/`clearError`.
- Validação blur: `showError('pc-ddi', 'DDI inválido')` se campo vazio.
- Validação submit: `clearError` em todos + `if (!ddi) showError(...)` — DDI vazio bloqueia submit.

**Fluxo de dados:**

1. Submit válido → gera `event_id` → dispara `Lead` no Pixel (com `event_id`) → POST para `/api/capi` com PII (email + phone + nome, hasheados no servidor) → POST para Apps Script → salva no Google Sheets
2. `phoneClean = ddi + phone.replace(/\D/g,'')` (DDI prefixado)
3. Redirect Hotmart: `?name=&email=` (sem `&phone=` — parâmetro não suportado pelo Hotmart)

**Arquitetura JS:** todo o código do modal (DDI_MAP, listeners, validação, submit) vive num único `<script>` com IIFE, imediatamente após o HTML do modal. `showError`/`clearError` são funções internas do IIFE — não expor como globais.

---

## Protocolo de trabalho

- **Editar CSS**: `grep -n ".classe" index.html` → Read com offset
- **Editar bloco HTML**: `grep -n "BLOCO 0X" index.html` → ler 30-40 linhas com offset
- **Não ler o HTML completo** — é ~1900 linhas; consultar via grep/offset
- **PREVIEW ONLY block**: remover antes do deploy (últimas ~50 linhas do `<style>`)

### Checklist de avaliação antes de qualquer mudança

Toda alteração na LP — de copy, CSS, HTML, schema ou arquivos auxiliares — deve ser avaliada conscientemente contra os seguintes critérios antes de implementar. Desvios são permitidos, mas devem ser explicitados.

| Critério           | O que verificar                                                                                                                              |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tipografia**     | Fonte (Montserrat), tamanho (base 17px mobile → desktop via multiplicadores DS), peso, cor por contexto; mudanças desktop só em `@media (min-width: 900px)` |
| **Cores**          | Usa tokens do DS (`--brand`, `--brand-vivid`, `--star`, `--ink` etc.) — nunca hex avulso                                                     |
| **Contraste**      | Texto corpo ≥4.5:1 WCAG AA; texto grande ≥3:1                                                                                                |
| **Copy**           | Sem travessão (—) em copy persuasiva, sem ponto de exclamação em copy persuasiva (permitido em momentos de conquista — submit, pós-compra), sem "guru", sem "jornada de 40 dias"; texto de alunos exato do site/copy file |
| **SEO+AEO**        | H1 único; H2 com keyword; FAQ: lead AEO + título ≤65 chars; alt text descritivo; schema sincronizado                                         |
| **Performance**    | Self-hosting de todo asset (sem exceções); fontes self-hosted com `font-display: optional`; ícones como SVG inline (nunca icon font); `fetchpriority="high"` + `srcset` no LCP; `width`/`height` + `img { height: auto }` em todas as imagens; Lighthouse mobile ≥ 90. Ver `## Performance` neste Guia. |
| **LGPD**           | Tracking só dentro de `loadTracking()` — nunca no `<head>` diretamente                                                                       |
| **Tracking**       | Novos elementos clicáveis relevantes precisam de `data-track` ou evento Pixel                                                                |
| **Responsividade** | Testar 390px mobile; touch targets ≥44px; nada que quebre em landscape; desktop em bloco único `@media (min-width: 900px)` — mobile base intocado |
| **llms.txt**       | Mudança de copy ou FAQ que afeta o resumo do site → atualizar `llms.txt` junto                                                               |
| **Tokens de componente** | Ícone usa `var(--brand-vivid)`, 48px wrapper / 44px SVG; border-radius e sombra via tokens do DS — nunca valores avulsos |
| **Schema sync** | Ao alterar FAQ, campo `text` do JSON-LD FAQPage muda junto; ao alterar VSL, `VideoObject` muda junto |
| **IDs de seção** | Novos `<section>` precisam de `id="secao-*"` — usados pelos scroll markers de tracking e por links internos de FAQ |
| **Acessibilidade** | `:focus-visible` visível em todos os interativos; `aria-modal` + `aria-labelledby` em modais; `aria-label` em SVGs e facades; `alt` correto em todas as imagens; `@media (prefers-reduced-motion)` desativa animações |

---

## Escala tipográfica mobile → desktop

**Fórmula generalizada** — aplicar em qualquer LP nova ao adicionar suporte desktop:

| Token | Mobile | Desktop | Multiplicador |
|---|---|---|---|
| `.t-hero` (H1) | 24px | 42px | ×1.75 |
| `.t-h2` | 20px | 30px | ×1.50 |
| `.t-h3` | 18px | 22px | ×1.22 |
| body / parágrafos | 16px | 17px | +1px |

**Razões desktop resultantes** — H2/body: 1.76× · H3/body: 1.29× (harmonia visual validada em 900px+)

**Princípio**: desktop amplifica, não redesenha. A hierarquia mobile é preservada com multiplicadores consistentes. Nunca escalar headings sem manter a proporção entre si.

**Implementação**: bloco único `@media (min-width: 900px)` — estilos base (mobile) intocados. Nenhuma regra mobile dentro do bloco desktop. Ver `escala_desktop_formula` no `design-system.json`.

---

## Padrões de composição desktop

Decisões de layout desktop validadas em sessões anteriores. Aplicar em páginas novas quando a situação se repetir.

### Grid de cards com alturas variadas (masonry)

Usar **JS masonry** (`position:absolute`) quando os cards tiverem alturas variadas e for necessário preencher gaps organicamente. CSS grid cria linhas de altura igual (gera espaço vazio); CSS columns encaixa top-to-bottom mas não é L→R; JS masonry coloca cada card na coluna mais curta (shortest-column-first).

**CSS base (mobile — intocado):**
```css
.grid { display: grid; grid-template-columns: 1fr; gap: 12px; }
```

**CSS desktop (dentro do bloco `@media (min-width: 900px)`):**
```css
.dep-grid   { display: block; position: relative; }
.dep-card   { box-shadow: var(--shadow-lift); }
.ciencia-grid  { display: block; position: relative; }
.ciencia-bloco { box-shadow: var(--shadow-lift); border: 1px solid var(--border); }
```

**Script (antes de `</body>`) — reutilizável para qualquer grid:**
```javascript
(function(){
  var BP = 900;
  function masonry(selector, cols, gap) {
    var grid = document.querySelector(selector);
    if (!grid) return;
    var cards = Array.from(grid.children);
    if (window.innerWidth < BP) {
      grid.style.cssText = '';
      cards.forEach(function(c){ c.style.cssText = ''; });
      return;
    }
    grid.style.position = 'relative';
    grid.style.display  = 'block';
    var colW = (grid.offsetWidth - gap * (cols - 1)) / cols;
    var tops = new Array(cols).fill(0);
    cards.forEach(function(card){
      var col = tops.indexOf(Math.min.apply(null, tops));
      card.style.position = 'absolute';
      card.style.width    = colW + 'px';
      card.style.left     = (col * (colW + gap)) + 'px';
      card.style.top      = tops[col] + 'px';
      tops[col] += card.offsetHeight + gap;
    });
    grid.style.height = Math.max.apply(null, tops) + 'px';
  }
  function run() {
    masonry('.dep-grid',    3, 8);
    masonry('.ciencia-grid', 2, 24);
  }
  function init() {
    run();
    document.querySelectorAll('.dep-grid img, .ciencia-grid img').forEach(function(img){
      if (!img.complete) img.addEventListener('load', run);
    });
    var t;
    window.addEventListener('resize', function(){ clearTimeout(t); t = setTimeout(run, 120); });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
```

**Atenção — lazy images**: `loading="lazy"` faz imagens terem height 0 no DOMContentLoaded. O listener por imagem (`if (!img.complete) img.addEventListener('load', run)`) é obrigatório.

**Trade-off**: ordem visual no desktop não é estritamente sequencial — cada card vai para a coluna mais curta, não para a próxima posição da esquerda. Aceitável em grids narrativos; verificar com o cliente se a ordem importa.

**Usar**: grids com conteúdo de alturas variadas (dep-visuais, pesquisas científicas)
**Não usar**: cards uniformes (ícone + título + desc fixo) → CSS grid convencional

### Layouts multi-coluna (1 → N colunas no desktop)

Para seções que vão de coluna única (mobile) para 2 ou mais colunas (desktop): **wrapper semântico + flex/grid no breakpoint**. Nunca `grid-row`/`grid-column` explícitos em filhos — frágil, quebra com qualquer mudança de conteúdo ou ordem.

**HTML — adicionar wrapper por coluna:**
```html
<section class="sec minha-sec">
  <div class="minha-inner">    <!-- wrapper: conteúdo principal / coluna 1 -->
    ...
  </div>
  <div class="minha-aside">   <!-- irmão: conteúdo secundário / coluna 2 -->
    ...
  </div>
</section>
```

**CSS — dentro do bloco `@media (min-width: 900px)`:**
```css
/* 2 colunas assimétricas (foto + texto, item + detalhe) */
.minha-sec   { display: flex; gap: 40px; align-items: center; }
.minha-inner { flex: 1; }
.minha-aside { flex-shrink: 0; width: 260px; }

/* 2 colunas simétricas */
.minha-sec   { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }

/* 3 colunas uniformes */
.minha-grid  { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }

/* N colunas uniformes */
.minha-grid  { display: grid; grid-template-columns: repeat(N, 1fr); gap: Xpx; }
```

**Instâncias EDm:**
- 2 col assimétricas: professor (foto `width: 260px; flex-shrink: 0` + bio `flex: 1`)
- 3 col simétricas: para quem é (`repeat(3, 1fr)`, gap 20px, padding ampliado com `50vw - 580px`)
- 3–4 col alturas variáveis: dep-visuais e ciência → JS masonry (ver seção acima)

**Regra de ouro:** o wrapper fica no HTML permanentemente. O `display: flex/grid` fica **só** dentro do `@media (min-width: 900px)`. O CSS base (mobile) não precisa de `display: block` explícito — já é o padrão. Mobile nunca é afetado.

### Watermark SVG com posicionamento viewport-relativo

Para alinhar um elemento decorativo de fundo com elemento específico do texto em qualquer viewport, usar `left: calc(50vw - Xpx)` em vez de `right: fixo`.

**Fórmula**: `Xpx = metade_viewport_alvo − posição_horizontal_desejada`

A seção pai precisa de `position: relative; overflow: hidden; isolation: isolate`. O SVG recebe `position: absolute; z-index: -1`.

### Seção com conteúdo mais largo

Para seções que se beneficiam de mais espaço horizontal (ex: grid de 3 cards com ícones grandes), ampliar o padding: `max(16px, calc(50vw - Xpx))` onde X > 480. A cada +100px em X, o conteúdo cresce +200px em viewports largos. Usar com moderação — quebra a grade uniforme de 960px.

### Footer com logo à esquerda e texto centralizado

No desktop, quando a logo fica alinhada à esquerda (`justify-content: flex-start`), o texto que deve parecer centralizado precisa de `flex: 1; text-align: center` — isso o centraliza no espaço restante, não no viewport inteiro. Fundo claro (`var(--brand-ice)`) com logo a `opacity: 1.0`.

### Logo com clipping de whitespace interno (mobile)

Quando o arquivo de logo tem margem/padding interno no topo, o elemento visual fica empurrado para baixo do frame visível. Técnica: `overflow: hidden` no wrapper com altura fixa + `margin-top` negativo na `<img>` para "pular" o whitespace.

```css
.footer-logo { overflow: hidden; height: 62px; } /* altura = quanto quero mostrar */
.footer-logo img { height: 72px; margin-top: -10px; } /* pula 10px de whitespace no topo */
```

A janela visível passa a ser pixels 10–72 do arquivo (62px de conteúdo útil). Ajustar os valores conforme o whitespace real do arquivo de logo.

### Bloco de preço — estrutura HTML

O "12x de" é um `<span class="preco-parcela">` dentro do `<p class="preco-main">`, não um elemento separado. Isso garante que o número de parcelas e o valor ficam na mesma linha tipográfica com tamanhos diferentes.

```html
<p class="preco-label">Por apenas</p>
<p class="preco-main"><span class="preco-parcela">12x de </span>R$49,95</p>
<p class="preco-alt">ou R$ 483,00 à vista</p>
<p class="preco-seguro">Pagamento <strong>100% seguro</strong> com acesso imediato</p>
```

Não separar `preco-parcela` em elemento próprio — quebra o alinhamento de linha.

### Bloco professor — foto desktop

Foto ao lado do texto com `align-items: center` no container flex (centro da foto alinhado ao centro do texto). Tamanho fixo: `width: 260px; max-width: none; flex-shrink: 0` no desktop. Mobile: `max-width: 180px; width: 100%`. Não usar `align-items: stretch` nem `object-fit: cover` — distorce a proporção original.

### Quebra de linha condicional (`br.br-desktop`)

Para controlar quebras de linha em headings longos sem criar HTML duplicado por viewport:

```html
O que você nunca teve é um método que te faça<br class="br-desktop">
sentir na pele o que é meditar de verdade
```

```css
/* base (mobile) */
br.br-desktop { display: none; }

/* desktop */
@media (min-width: 900px) {
  br.br-desktop { display: inline; }
}
```

Usar em subtítulos de hero e headings que precisam de quebra manual apenas em viewports largos.

---

## Status LGPD

**CONFORME** — Pixel e Clarity carregados via `loadTracking()` somente após consentimento. Cookie banner implementado com mecanismo completo de consent.

**Mecanismo de consentimento (junho 2026):**
- Qualquer scroll na LP → consent, exceto enquanto `_policyFocused = true`
- Qualquer clique fora do `#cookie-banner` → consent; cliques dentro do banner que não sejam o botão Continuar são suprimidos (texto, link de política, área vazia)
- Botão "Continuar" → fecha o banner + consent via event bubbling
- Link "Política de Privacidade" no banner → abre `<details id="politica-privacidade">` inline no footer (não abre nova página); banner permanece visível; `_policyFocused = true` ativado sincronamente antes do `scrollIntoView`
- Enquanto `_policyFocused = true`: scroll suprimido em toda a fase — a caminho da seção, dentro dela e no evento que a tira da viewport; clique dentro de `#politica-privacidade` também suprimido
- `_policyViewed = true` marcado quando a seção entra na viewport — distingue "ainda chegando" de "saindo"
- Quando a seção sai da viewport após ter sido vista: flags limpas; consent retoma na **próxima** interação (não no mesmo evento de scroll)
- Consentimento persistido em `localStorage('edm_consent'='granted')` — tracking não carrega novamente em visitas seguintes

**DPA Hotmart:** não aplicável — Hotmart BR não tem fluxo de DPA para produtores. Hotmart atua como operadora de dados no checkout pelos próprios termos. Política de privacidade já menciona a Hotmart. Nenhuma ação necessária.

---

## Performance

> **Princípio central — mobile-first.** Performance mobile não é otimização opcional — é a base da conversão de tráfego pago. Cada segundo a mais de carregamento reduz conversão diretamente. Toda avaliação (Lighthouse, LCP, CLS, TBT) é feita no modo **Mobile**, aba anônima, URL de produção. Meta: Lighthouse mobile ≥ 90. Score 95+ é factível e deve ser perseguido. Referência: LP {Produto} atingiu 97 com as práticas abaixo.

### Diagnóstico

- **Lighthouse Mobile**: DevTools → Lighthouse → **Mobile**, aba anônima, URL de produção. Nunca usar preview Vercel — `X-Robots-Tag: noindex` distorce métricas de SEO e pode afetar o score.
- **LCP breakdown**: expandir o elemento LCP no Lighthouse → decompor em TTFB + resource load delay + resource load duration + render delay. Cada componente tem causa específica e fix diferente.
- **Identificar o elemento LCP**: pode ser imagem (thumbnail) ou texto (H1 com fonte externa). A causa muda o fix.
- **TBT breakdown**: expandir "Minimize main-thread work" no Lighthouse — ver qual script está bloqueando e por quanto tempo.

### Regras ordenadas por impacto (mobile)

#### Impacto muito alto — eliminar antes de qualquer outra otimização

**1. Eliminar icon fonts**

Nunca usar Font Awesome ou qualquer icon font para < 10 ícones. Substituir por SVG inline:
- Elimina render-blocking (~1.370ms observado na LP {Produto})
- Remove ~73KB JS + ~18KB CSS não usados do thread principal
- Fonte de SVGs FA6 free: `raw.githubusercontent.com/FortAwesome/Font-Awesome/6.5.1/svgs/solid/[nome].svg`
- CSS: `.icone svg { width: Xpx; height: Xpx; fill: var(--brand-vivid); }`

**2. Self-hospedar fontes com `font-display: optional`**

Google Fonts CDN adiciona DNS+TLS externos que bloqueiam render. Solução:
- Baixar WOFF2 do subset latin (U+0000–00FF) — cobre pt-BR. Um arquivo para weight range 400–700 se for fonte variável.
- `@font-face` com **`font-display: optional`**, nunca `swap`. `optional` abandona a fonte se não carregou no primeiro ciclo de render (usa fallback do sistema); `swap` re-pinta ao carregar a fonte e dispara novo ciclo LCP.
- `<link rel="preload" as="font" href="assets/fonte.woff2" type="font/woff2" crossorigin>` no `<head>`
- Subsetting avançado: `pyftsubset fonte.ttf --unicodes="U+0000-00FF" --flavor=woff2` reduz de ~35KB para ~18–22KB (+2–3pts extras)
- **Trade-off:** `optional` pode exibir fonte do sistema na primeira visita se a fonte não carregou dentro do ciclo inicial de render. Em visitas seguintes está em cache e aparece. Mitigação: definir fallback visualmente próximo — `font-family: 'Montserrat', 'Arial', sans-serif` — para que o fallback seja aceitável.
- Impacto observado: FCP 2.4s → 1.2s

**3. Self-hospedar elemento LCP com `fetchpriority="high"` e preload com srcset**

O LCP element (thumbnail do VSL ou imagem hero) é o maior responsável pelo score mobile. Se vier de CDN externo, paga DNS+TLS de outro domínio antes de começar o download. Solução:
- Baixar e converter para WebP: `cwebp -q 70 thumb.jpg -o assets/vsl-thumb.webp` (~78KB para 1280×720)
- Versão mobile (obrigatória): `cwebp -q 72 thumb.jpg -resize 780 438 -o assets/vsl-thumb-mobile.webp` (~33KB)
- No `<img>`: `srcset="assets/vsl-thumb-mobile.webp 780w, assets/vsl-thumb.webp 1280w" sizes="(max-width: 900px) 100vw, 880px"` + `fetchpriority="high"` + **sem** `loading="lazy"`
- No `<head>` preload: `<link rel="preload" as="image" imagesrcset="assets/vsl-thumb-mobile.webp 780w, assets/vsl-thumb.webp 1280w" imagesizes="(max-width: 900px) 100vw, 880px" fetchpriority="high">` — sem `imagesrcset`, o preload ignora srcset e baixa sempre o maior arquivo
- Impacto observado: LCP 6.4s → 4.5s

**4. CSS reset de imagens + atributos dimensionais em todas as `<img>`**

No reset global:
```css
img { display: block; max-width: 100%; height: auto; }
```
Em cada `<img>`: `width="X" height="Y"` com dimensões reais (obtidas com `sips -g pixelWidth -g pixelHeight assets/img`).
- `height: auto` no CSS é obrigatório junto com o atributo `height` — sem ele, o atributo vira pixel fixo e distorce em containers responsivos
- Atributos `width`/`height` permitem que o browser reserve espaço antes do download (elimina CLS)
- Impacto observado: CLS 0.x → 0

#### Impacto alto — aplicar logo após os fundamentos

**5. `loading="lazy"` em tudo abaixo do fold; `fetchpriority="high"` no LCP**

Duas regras complementares para o carregamento de imagens:
- Toda `<img>` abaixo do fold: `loading="lazy"` — o browser não baixa durante o load inicial, libera banda para o LCP
- `<img>` acima do fold (logo, hero, LCP element): `fetchpriority="high"` — sobe na fila de prioridade. **Nunca combinar `loading="lazy"` com `fetchpriority="high"`**
- Auditoria: `grep -n '<img' index.html | grep -v 'loading='` — apenas logo do header e thumbnail LCP devem aparecer

**6. Converter todas as imagens para WebP e comprimir agressivamente**

PNG e JPG pesam 2–5× mais que WebP equivalente. Padrões de qualidade:
- Fotos/depoimentos: `cwebp -q 65 foto.png -o foto.webp` — limiar ideal qualidade/tamanho
- Logos e ícones raster: `cwebp -q 80 logo.png -o logo.webp` — preserva bordas nítidas
- Recomprimir WebP já existentes (quando recebidos de terceiros): `dwebp img.webp -o /tmp/tmp.png && cwebp -q 65 /tmp/tmp.png -o img.webp`
- Verificar dimensões: nunca servir imagem maior que o espaço de display (`sips -g pixelWidth img`)
- Impacto observado na LP EDm: −422KB total de payload (PNGs → WebP + 8 WebPs recomprimidos)

**7. Scripts externos com `defer` ou movidos para `</body>`**

Todo `<script src="...">` sem `defer` no `<head>` bloqueia o parse HTML — cada ms de bloqueio vira TBT:
- Scripts de analytics/tracking: `defer` ou dentro de `loadTracking()` (dispara só após consentimento — ideal para LGPD + performance)
- Scripts de componentes (masonry, modal): mover para antes de `</body>` ou usar `defer`
- Nunca usar `async` para scripts que dependem de outros — order não é garantida

**15. Facade para todos os iframes de vídeo (não só o LCP)**

Todo `<iframe>` do YouTube/Vimeo carrega ~500KB de JS no primeiro render. O VSL tem facade (thumbnail local + JS só ao clicar). O mesmo padrão deve ser aplicado a **todos os iframes de depoimento**:
- Substituir `<iframe src="https://www.youtube.com/embed/ID">` por `<div class="video-facade" data-vid="ID">` com thumbnail WebP local
- JS: ao clicar, substituir o `<div>` pelo `<iframe>` com `?autoplay=1&mute=1`
- Sem facade, cada iframe de depoimento visível na viewport dispara 1 request externo ao load

**VSL com VSLProgress (YT IFrame API):** o iframe do VSL pode estar no HTML inicial com `enablejsapi=1` (para `new YT.Player()` funcionar no load) ou pode ser injetado no clique com `enablejsapi=1` e `YT.Player` inicializado em seguida — ambos válidos. O iframe de depoimentos usa sempre injeção no clique (padrão simples). Nunca colocar `enablejsapi=1` em iframes de depoimento: aumenta payload desnecessariamente.

**16. Analytics e tracking só após consentimento (double-win LGPD + performance)**

Pixel e Clarity no `<head>` bloqueiam render e aumentam TBT, além de violar LGPD. Padrão correto:
- Todo tracking vai dentro de `loadTracking()`, chamado apenas quando usuário aceita o cookie banner
- Ganho: TBT reduzido no load inicial (~100–200ms); compliance LGPD automático
- Verificar: `grep -n "fbq\|clarity\|gtag" index.html` — nenhuma ocorrência deve aparecer fora da função de consent

**17. INP — modal com `opacity`/`visibility`, não `display:none` (padrão obrigatório para overlays)**

`display:none → display:flex` força full layout reflow no click handler, bloqueando o browser de pintar. Em mobile mid-range, esse reflow sozinho já ultrapassa o limiar de 200ms do INP.

Padrão correto para overlays/modais:
```css
/* Modal sempre em display:flex (fixed = sem impacto no layout do documento) */
.modal-overlay {
  display: flex; position: fixed; inset: 0;
  opacity: 0; visibility: hidden; pointer-events: none;
  transition: opacity 0.15s ease;
}
.modal-overlay.active {
  opacity: 1; visibility: visible; pointer-events: auto;
}
@media (prefers-reduced-motion: reduce) { .modal-overlay { transition: none; } }
```

```js
btn.addEventListener('click', function(e) {
  e.preventDefault();
  // Resposta visual imediata — apenas mutações DOM necessárias para pintar
  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';
  // ...outras mutações visuais...

  // Tracking + foco adiados com setTimeout(0): browser pinta antes de processar
  setTimeout(function() {
    loadTracking();
    document.getElementById('campo-inicial').focus();
    // fbq(), _capi(), clarity() aqui
  }, 0);
});
```

- `visibility: hidden` evita que elementos dentro do overlay sejam focáveis via Tab quando fechado (accessibility OK)
- `backdrop-filter: blur()` aplicado ao overlay não bloqueia INP com esta abordagem: a GPU já tem o layer compositor no load
- `setTimeout(0)` é suficiente para ceder ao browser; `scheduler.yield()` é mais preciso mas Chrome 115+ only

#### Impacto médio — ganhos incrementais garantidos

**8. Cache headers no Vercel**

`vercel.json` na raiz do projeto, incluído no payload de deploy:
```json
{
  "headers": [
    { "source": "/(.*)", "headers": [
        {"key": "X-Content-Type-Options", "value": "nosniff"},
        {"key": "X-Frame-Options",        "value": "SAMEORIGIN"},
        {"key": "X-XSS-Protection",       "value": "0"},
        {"key": "Referrer-Policy",        "value": "strict-origin-when-cross-origin"}
    ]},
    { "source": "/",            "headers": [{"key": "Cache-Control", "value": "public, max-age=0, s-maxage=86400, stale-while-revalidate=86400"}] },
    { "source": "/(.*)\\.html", "headers": [{"key": "Cache-Control", "value": "public, max-age=0, s-maxage=86400, stale-while-revalidate=86400"}] },
    { "source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, s-maxage=31536000, immutable"}] },
    { "source": "/robots.txt",  "headers": [{"key": "Cache-Control", "value": "public, max-age=86400"}] },
    { "source": "/sitemap.xml", "headers": [{"key": "Cache-Control", "value": "public, max-age=86400"}] }
  ]
}
```
- Security headers (bloco `/(.*)`): nosniff previne MIME-sniffing; SAMEORIGIN bloqueia embedding por domínio externo (anti-clickjacking); XSS=0 desativa auditor legado; Referrer-Policy mantém origem sem vazar URL completa em requests cross-origin.
- HTML (`/` e `/*.html`): `max-age=0` (browser revalida sempre) + `s-maxage=86400, stale-while-revalidate=86400` (CDN serve cache 24h sem travar usuário).
- Assets (`/assets/(.*)`): `max-age=31536000, s-maxage=31536000, immutable` — browser e CDN nunca re-verificam (assets com hash no nome).

**9. Preconnect para 3rd parties críticos + DNS-prefetch para secundários**

No `<head>`, antes de qualquer script externo:
```html
<link rel="preconnect" href="https://www.clarity.ms">
<link rel="preconnect" href="https://connect.facebook.net">
<link rel="preconnect" href="https://pay.hotmart.com">
<link rel="dns-prefetch" href="https://www.youtube.com">
<link rel="dns-prefetch" href="https://www.youtube-nocookie.com">
```
`preconnect` = DNS + TCP + TLS antecipados (usar para 3rd parties do critical path). `dns-prefetch` = só DNS (usar para domínios que carregam após interação do usuário).

**10. HTML minificado no deploy**

`html-minifier-terser` remove whitespace, comentários e atributos redundantes — reduz HTML de ~140KB para ~126KB sem risco. Integrar no script de deploy, não no HTML-fonte.
```bash
npx html-minifier-terser \
  --collapse-whitespace \
  --remove-comments \
  --remove-redundant-attributes \
  --collapse-boolean-attributes \
  index.html
```
**Nunca usar `--minify-js`**: renomeia funções entre blocos `<script>` separados — quebra chamadas cross-script.

**11. Override CSS mobile para containers com masonry JS**

Masonry JS usa `element.style.cssText` que sobrescreve CSS de componente. Em mobile, o reset de grid precisa de `!important`:
```css
@media (max-width: 899px) {
  .dep-grid { display: grid !important; grid-template-columns: 1fr !important; height: auto !important; position: static !important; }
  .dep-grid .dep-card { position: static !important; width: 100% !important; left: auto !important; top: auto !important; }
}
```
Race condition entre `img.load` events e o masonry JS torna `grid.style.cssText = ''` imprevisível — `!important` é a única garantia.

**17. Evitar redirect chains**

Cada redirect (www → apex, http → https) adiciona 100–300ms de round-trip antes do primeiro byte. Configurar o domínio canônico diretamente no DNS (A record para apex, CNAME para www → apex no Vercel). Verificar:
```bash
curl -I https://www.{dominio}.com.br/
# Location: deve apontar diretamente para apex, sem cascata de redirects
```
Dois redirects em cadeia (http → https → www → apex) = +600ms no mobile antes de qualquer byte de HTML.

**18. Payload total monitorado**

Meta mobile: payload total < 1.6MB (limite Lighthouse para sem aviso de recurso pesado). Auditar antes de cada deploy:
```bash
du -sh assets/* | sort -h   # listar assets por tamanho
du -sh assets/               # total da pasta
```
Suspects típicos: PNGs não convertidos (> 200KB), WebPs sem recompressão (> 150KB), fontes completas sem subsetting (> 80KB).

#### Impacto baixo/situacional — +1 a 3 pontos em contextos específicos

**12. AVIF além de WebP**

Suporte 96%+ em 2026. AVIF reduz imagens ~20% adicionais vs WebP na média (observado: 267KB de saving em 35 imagens da LP EDm, ~20% de redução). Usar `<picture>` com fallback — browser escolhe o melhor formato disponível:
```html
<picture>
  <source srcset="assets/img.avif" type="image/avif">
  <img src="assets/img.webp" alt="..." loading="lazy" width="X" height="Y">
</picture>
```
Converter: `avifenc -q 65 --speed 6 img.png img.avif` (`-q` = qualidade 0–100, 100=lossless; `--speed 6` = rápido; requer `brew install libavif`).

**Fluxo completo de conversão** (avifenc aceita apenas PNG/JPG como input):
```bash
dwebp foto.webp -o /tmp/tmp.png && avifenc -q 65 --speed 6 /tmp/tmp.png foto.avif
```
Para logos: usar `-q 75` (preserva bordas nítidas).

**ATENÇÃO:** AVIF não é sempre menor que WebP. Antes de servir o AVIF, comparar tamanhos:
- Se `avif >= webp`: deletar o AVIF e usar WebP puro (sem `<picture>`)
- Não adianta usar `<picture>` com AVIF maior — browser escolheria o maior

**Não converter para AVIF:**
- VSL thumbnail (LCP element + preload ativo) — complexidade de preload com AVIF não justifica o risco de regredir LCP
- Favicons e ícones (pouco impacto)
- Imagens para og:image/twitter:image (crawlers de social não suportam AVIF)

**13. CSS coverage audit**

DevTools → More tools → Coverage → recarregar a página → CSS não usado destacado em vermelho. Remover seletores de componentes que não existem na LP. Não automatizável via script — requer execução no browser real.

**14. Font subsetting avançado**

Reduzir WOFF2 com `pyftsubset` (já executado na LP EDm em jun/2026):
```bash
# pyftsubset já instalado via Homebrew
pyftsubset Montserrat.woff2 \
  --unicodes="U+0020-007E,U+00A9,U+00C0-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2013-2014,U+2000-206F,U+20AC,U+2122,U+FEFF,U+FFFD" \
  --output-file=montserrat.woff2 \
  --flavor=woff2
```
Resultado LP EDm: 35KB → 25KB (−28%, com layout features/kerning preservados). Antes de subsetar: extrair chars únicos do HTML com `python3 -c "import re,html; ..."` para garantir cobertura.

**19. Prefetch da página de checkout**

`<link rel="prefetch">` instrui o browser a baixar o URL em background durante tempo ocioso, antes do usuário clicar. Quando o CTA é clicado, a página de checkout já está (parcialmente) em cache:
```html
<link rel="prefetch" href="https://pay.hotmart.com/[OFFER_ID]?checkoutMode=10">
```
- Colocar no `<head>`, após os `<link rel="preconnect">` existentes
- Risco: zero. O browser baixa silenciosamente apenas se houver banda disponível
- Impacto: percepção de velocidade no momento de conversão (pós-clique no CTA)

### Diagnóstico por sintoma

| Sintoma | Causa mais provável | Fix |
|---|---|---|
| LCP > 4s + elemento é imagem | Thumbnail externo ou sem preload | Self-hospedar + `fetchpriority="high"` + preload com `imagesrcset` (regra 3) |
| LCP > 3s + elemento é texto (H1) | `font-display: swap` re-pintando | `font-display: optional` (regra 2) |
| FCP > 2s | Fonte via CDN externo | Self-hospedar + preload (regra 2) |
| CLS > 0 | `<img>` sem `width/height` ou sem `height: auto` | Reset CSS + atributos dimensionais (regra 4) |
| TBT alto | Scripts pesados no thread principal | `defer` / mover para `</body>` / lazy-load tracking (regra 7) |
| TBT alto + render-blocking JS/CSS | Icon font (Font Awesome, etc.) | SVG inline (regra 1) |
| Score cai em mobile vs desktop | Imagens sem versão mobile no srcset | srcset com variante mobile (regra 6) |
| Colunas não colapsam no mobile | Masonry JS inline style sobrescreve CSS | `!important` no `@media (max-width: BP-1px)` (regra 11) |
| Imagens abaixo do fold pesando no load | `loading` ausente | `loading="lazy"` em tudo abaixo do fold (regra 5) |

### Meta e benchmarks

> Toda avaliação: Lighthouse **Mobile**, aba anônima, URL de produção. Desktop é irrelevante para conversão de tráfego pago mobile.

| Métrica | Aceitável | Excelente | Meta |
|---|---|---|---|
| Lighthouse mobile | ≥ 80 | ≥ 90 | ≥ 90, perseguir 95+ |
| LCP | < 2.5s | < 1.5s | < 2.5s |
| FCP | < 1.8s | < 1.0s | < 1.5s |
| CLS | < 0.1 | 0 | 0 |
| TBT | < 200ms | < 50ms | < 150ms |
| Accessibility | ≥ 85 | ≥ 95 | ≥ 90 |

Referência real: LP {Produto} pós-sessões 30+31 → **97 Performance / 96 Accessibility / 100 Best Practices / 100 SEO** (Lighthouse Mobile, produção).

### Caminho típico de evolução do score

| Faixa | O que falta | Regras prioritárias |
|---|---|---|
| < 70 | Icon font, fonte CDN, thumbnail externo, CLS | 1, 2, 3, 4 |
| 70–85 | loading=lazy ausente, iframes sem facade, imagens PNG/JPG pesadas | 5, 6, 15 |
| 85–93 | Scripts não diferidos, tracking no head, sem cache headers, sem preconnect | 7, 16, 8, 9 |
| 93–97 | HTML não minificado, imagens ainda grandes, redirects, payload acima de 1.6MB | 10, 6 (recomprimir), 17, 18 |
| 97–100 | AVIF, CSS coverage, font subsetting | 12, 13, 14 |

---

## SEO + AEO — Princípios e Regras

> AEO (Answer Engine Optimization) = otimizar para Google AI Overviews, ChatGPT, Claude, DeepSeek, Perplexity e outros modelos que extraem respostas diretamente do conteúdo da página.

### 1. Meta e head técnico

- **`<title>`**: keyword primária nos primeiros 60 chars; versão longa (700+ chars) para AEO — modelos de linguagem leem o title completo; SERP exibe só os primeiros ~60 chars
- **`<meta description>`**: primeira frase = resposta direta AEO; SERP exibe os primeiros ~155 chars; total pode ser 800–1000 chars para cobertura de AEO
- **`<meta name="robots">`**: `content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"` — autoriza o Google a usar fragmentos completos, imagens em alta resolução e previews de vídeo para AI Overviews
- **`canonical`** e **`hreflang`**: obrigatórios mesmo em site de página única
- **Open Graph** (`og:*`):
  - `og:type`: `website` para LP; `article` para posts de blog
  - `og:locale`: `pt_BR` (underscore, não hífen) — ausente = Google assume locale padrão
  - `og:title` e `og:description`: versões distintas e conversacionais — são o que aparece no WhatsApp, Facebook e LinkedIn
  - `og:image`: 1200×630px obrigatório para rich preview; `og:image:width` e `og:image:height` explícitos; evitar logo pequena sobre fundo vazio (parece placeholder); logo em canvas full-width com identidade visual da marca é aceitável — o que importa é que a imagem comunique algo no preview social
- **Twitter/X Card** (`twitter:*`):
  - `twitter:card`: `summary_large_image` para imagem de destaque
  - `twitter:title` e `twitter:description`: podem ser iguais aos og:* ou adaptados para o tom do X
  - `twitter:image`: mesma imagem do og:image; atualizar junto ao og:image no deploy

### 2. Schemas JSON-LD

- Todo schema fica em `<script type="application/ld+json">` único com `@graph` — nunca inline em atributos HTML
- **FAQPage**: aumenta em 3× a probabilidade de aparecer em Google AI Overviews. Campo `text` em plain text (zero HTML). Schema deve ser idêntico ao texto visível na página; se o FAQ mudar, o schema muda junto
- **Course**: incluir `name`, `description`, `teaches`, `keywords` (40+ termos), `educationalLevel`, `provider`, `instructor`, `inLanguage`, `courseMode`, `hasCourseInstance` com `Offer`
- **VideoObject**: obrigatório se há VSL — incluir `name`, `description`, `uploadDate`, `duration` (formato ISO 8601: `PT51M48S`), `embedUrl`, `thumbnailUrl`, `contentUrl`
- **Person**: usar nome completo (`"{Nome Sobrenome}"`, não só `"Davi"`) — entidade nomeada completa melhora reconhecimento. Incluir `jobTitle`, `description`, `url`, `knowsAbout`, `sameAs`
- **Organization**: incluir `name`, `url`, `logo`, `contactPoint` e `sameAs` com todas as redes sociais — permite que o Google consolide a mesma entidade em múltiplas plataformas
- **`sameAs`** (Organization e Person): `["https://www.instagram.com/{produto}", "https://www.youtube.com/@{produto}", "https://www.tiktok.com/@{produto}"]` — ao adicionar nova rede social, atualizar em ambos os schemas
- **AggregateRating**: só implementar com avaliações verificáveis e visíveis na página (Hotmart ou Google Reviews) — Google pode penalizar markup sem evidência na página

### 3. Hierarquia de headings

- **Um único H1** no hero — pode ser emocional, mas deve conter ou remeter à keyword primária
- **H2 por seção principal** — cada H2 deve ser keyword-rich: descreve o tópico da seção, não apenas nomeia
  - Bom: "Perguntas Frequentes sobre Meditação"
  - Ruim: "Perguntas Frequentes - FAQ" (redundante, sem keyword adicional)
  - Bom: "Pesquisas científicas demonstram inúmeros benefícios de praticar meditação"
  - Bom: "{Nome Sobrenome} — yoga e meditação há 20 anos" (entidade nomeada + keyword)
  - Fraco: "Sobre o professor" (sem keyword, sem entidade nomeada)
- **H3 para sub-elementos** dentro de cada seção
- **Nunca pular níveis** (ex: H1 → H3 sem H2 intermediário)

### 4. FAQ — regras AEO específicas

- **Primeira frase = resposta direta**: crawlers de AI extraem a primeira frase como a resposta para a busca. Deve ser completa, com o dado mais específico e verificável logo no início — nunca uma frase introdutória
- **Títulos ≤65 chars**: Google trunca rich snippets a ~65 chars — título maior não aparece inteiro no SERP
- **Separar por intenção de busca**: personas distintas com estados emocionais diferentes merecem perguntas próprias com AEO leads próprios (ex: TDAH vs. "já tentou e não conseguiu" são clusters de busca separados)
- **Afirmações científicas**: citar fonte, ano e instituição na mesma frase (ex: Nature 2024, Johns Hopkins JAMA 2014) — aumenta credibilidade para extração por modelos e para o próprio leitor
- **Links externos de credibilidade**: afirmações com respaldo científico ganham links inline para a fonte primária (PubMed, Nature, Harvard Health, ScienceDaily etc.). Usar classe `ciencia-fonte` (font-size: 11px, color: var(--ink-3)) logo após o texto da afirmação. Quando há múltiplos links que quebrariam em meados do label, envolver em `<span class="ciencia-links">` com `display: block; margin-top: 3px` para forçar os links à linha abaixo. Benefício: sinal de E-E-A-T para Google + âncora de credibilidade para modelos de linguagem que extraem informações com fontes verificáveis
- **H2 da seção FAQ inclui keyword**: ex. "Perguntas Frequentes sobre Meditação", não "FAQ" isolado
- **Schema FAQPage sincronizado**: o campo `text` do JSON-LD deve ser idêntico ao texto visível na página (plain text, sem HTML)

### 5. Imagens

- **Self-hosting obrigatório, sem exceções**: toda imagem, fonte e ícone fica em `assets/` e sobe no deploy — nunca referenciar CDN de terceiros. Thumbnails YouTube: baixar e converter para WebP (`vsl-thumb.webp`). Fontes: self-hospedar subset latin em WOFF2. Ícones: substituir por SVG inline.
- **`fetchpriority="high"`** no LCP: logo e thumb do VSL hero (primeira dobra) — sem lazy loading nessas
- **`srcset` + `sizes` no LCP**: thumbnail com versão mobile (≤780px, ~33KB) e desktop (1280px, ~78KB) — browser baixa só o tamanho necessário. Preload também precisa de `imagesrcset` + `imagesizes` para respeitar a seleção responsiva.
- **`loading="lazy"`** em tudo abaixo da primeira dobra
- **`width` e `height` explícitos** em todas as imagens — obtidos com `sips -g pixelWidth -g pixelHeight assets/imagem`. Combinar sempre com `img { height: auto }` no CSS global; sem `height: auto`, o atributo height vira pixel fixo e distorce em containers responsivos.
- **WebP em tudo**: converter PNGs e JPGs com `cwebp -q 70`. Alvo: <100KB por imagem de conteúdo, <200KB para fotos grandes.
- **Alt text descritivo**: descreve o conteúdo + inclui keyword onde natural; formato sugerido: `[Pessoa/contexto] — [resultado/ação com keyword]`; máx 125 chars
- **Nunca `alt=""`** em imagem informativa — reservar só para imagens puramente decorativas (`aria-hidden="true"` nesses casos)

### 6. Semântica HTML

- **`<main>`** wrapping todo o conteúdo principal (entre a abertura do body/wrapper e o `<footer>`) — crawlers e screen readers usam para isolar conteúdo indexável
- **`<section>` com `id` descritivo** em cada bloco: `id="secao-faq"`, `id="secao-jornada"` etc. — usados pelos scroll markers de tracking e por links internos
- **`aria-label`** em elementos interativos sem texto visível (SVGs, botões de ícone, facades de vídeo)
- **`<footer>`** separado do `<main>` — conteúdo do footer não é considerado conteúdo principal pelo Google

### 7. Arquivos auxiliares (raiz do domínio)

- **`llms.txt`**: sintetiza o site para crawlers de modelos de linguagem (Perplexity, ChatGPT, Claude). Manter sincronizado com mudanças de copy e FAQ — se o FAQ muda, o `llms.txt` muda junto na mesma sessão
- **`robots.txt`**: diretivas para crawlers; `Sitemap:` apontando para `sitemap.xml`; `Disallow:` para versões de preview/staging que não devem ser indexadas antes do deploy
- **`sitemap.xml`**: submeter no Google Search Console após deploy; atualizar `<lastmod>` a cada mudança de conteúdo relevante

### 8. Performance como fator de SEO

Core Web Vitals afetam ranking diretamente: LCP < 2.5s, CLS < 0.1, INP < 200ms. Ver playbook completo na seção `## Performance` deste Guia — inclui regras ordenadas por impacto, diagnóstico e meta de score.

### 9. Schemas avaliados e descartados

Documentados para evitar reavaliação desnecessária em sessões futuras.

| Schema | Decisão | Razão |
|---|---|---|
| `Speakable` | Descartado | Google restringiu a publishers de notícias; sem benefício comprovado para LPs de curso em 2025–2026 |
| `HowTo` | Condicional | Adequado para "como meditar" apenas se a metodologia for reestruturada como série de passos numerados — exige mudança estrutural de conteúdo |
| `Clip` / `SeekToAction` | Condicional | Permite que o Google linke momentos específicos do VSL — requer timestamps exatos e vídeo chaptered no YouTube |
| `WebSite` + `SearchAction` | Baixa prioridade | Útil para site com múltiplas páginas e busca interna; pouco impacto para LP única |

### 10. Oportunidades condicionais abertas

| Oportunidade | Condição para implementar |
|---|---|
| `AggregateRating` schema | Avaliações verificáveis visíveis na página (Hotmart / Google Reviews) |
| ~~FAQ com links internos~~ | ✅ Implementado — Q1→`#secao-ciencia`, Q2→`#secao-o-que-e`, Q3→`#secao-o-que-e`+`#secao-jornada`, Q5→`#secao-depoimentos`, Q7→`#secao-dep-visuais`, Q9→`#secao-entregaveis` |
| ~~Milestone events VSL (25%, 50%, 75%)~~ | ✅ Implementado — `VSLProgress25` + `VSLProgress75` via YT IFrame API (`enablejsapi=1`, poll `setInterval(5000)`), Pixel + CAPI |
| `sameAs` com novas redes sociais | Ao ativar nova rede: adicionar URL em Organization e Person schemas |

---

## Validação e Testes

Rodar antes do deploy e periodicamente pós-publicação.

| O que testar | Ferramenta | O que verificar |
|---|---|---|
| Schemas JSON-LD | Google Rich Results Test | FAQPage, Course, VideoObject aparecem sem erros ou warnings |
| Core Web Vitals | PageSpeed Insights | LCP < 2.5s, CLS < 0.1, INP < 200ms — testar URL de produção |
| Open Graph | Meta Sharing Debugger | Preview de imagem (1200×630), título e descrição corretos |
| Twitter/X Card | X Card Validator | Preview exibe imagem grande (`summary_large_image`) |
| Meta Pixel | Meta Events Manager | Todos os 6 eventos disparando com parâmetros corretos |
| Microsoft Clarity | clarity.microsoft.com | Sessões sendo gravadas; mapa de calor do CTA visível |
| Análise de performance | Claude Code | O Claude consegue analisar: heatmap do Clarity (atenção por scroll), leads da planilha Apps Script (UTMs, criativos, funil) e Meta Ads (CPL, criativo, placement). |
| Hierarquia de headings | Extensão headingsMap (Chrome/Firefox) | Hierarquia H1 → H2 → H3 sem saltos; único H1 |
| LGPD / Consent | DevTools → Application → LocalStorage | `edm_consent: granted` só aparece após interação com o banner |

---

## Acessibilidade

Requisitos mínimos. Não bloqueantes para launch, mas implementar antes de tráfego pago significativo.

| Requisito | Implementação |
|---|---|
| **Foco visível** | `:focus-visible` em todos os interativos — `outline: 2px solid var(--brand-vivid); outline-offset: 2px`. Não usar `:focus` (afeta cliques de mouse) |
| **Touch targets** | Área clicável ≥44×44px (WCAG 2.5.5) — aplicar `padding` compensatório se o elemento visual for menor |
| **Aria modal** | Modal pré-checkout: `role="dialog"`, `aria-modal="true"`, `aria-labelledby=[id do título]`. Escape fecha. Foco preso dentro do modal (Tab não escapa) |
| **Aria interativos** | SVGs, botões icon-only, facades de vídeo: obrigatório `aria-label` descritivo |
| **Alt texts** | Informativas: `alt` com keyword front-loaded, máx 125 chars. Decorativas: `alt=""` + `aria-hidden="true"` |
| **Movimento reduzido** | `@media (prefers-reduced-motion: reduce)`: desativar transições, animações, scroll parallax |
| **Contraste** | Corpo ≥4.5:1 WCAG AA; texto grande ≥3:1. `brand_vivid` sobre branco = 3.5:1 — restrito a grifos |

---

## Anti-padrões

O que nunca fazer nesta LP, com razão documentada.

| Proibição | Razão |
|---|---|
| Fabricar ou modificar qualquer dado específico do produto — nomes de módulos, features, expressões da metodologia (ex: "guru", "Jornada de 40 dias"), contagem ou texto de depoimentos, avaliações agregadas | Se não existe no produto, não entra. Schema markup fabricado é penalizado pelo Google |
| Usar ponto de exclamação (!) em copy persuasiva | Hipótese em teste — evitar em headings, bullets e CTAs persuasivos. Permitido em momentos reais de conquista: submit de formulário, pós-compra, confirmação de acesso |
| Usar travessão (—) em copy persuasiva | Padrão de voz; exceções permitidas em headings informativos (ex: H2 com nome do professor) |
| Automação pós-lead | Com leads capturados na planilha, implementar fluxo de recuperação de vendas via ferramenta de automação. Condição: Sheet validada em produção |
| Tracking no `<head>` fora de `loadTracking()` | Viola LGPD — Pixel e Clarity devem disparar só após consentimento |
| `alt=""` em imagem informativa | Prejudica acessibilidade (screen readers) e SEO (crawler não lê o conteúdo) |
| `loading="lazy"` na imagem LCP (acima da dobra) | Atrasa LCP — usar `fetchpriority="high"` sem lazy nessas imagens |
| `loading="lazy"` sem `width`/`height` | Causa CLS (layout shift) — dimensões explícitas são obrigatórias |
| Font Awesome (ou qualquer icon font) | Adiciona ~73KB JS + ~18KB CSS não usados + request render-blocking (~1.3s). Substituir por SVG inline. |
| Google Fonts CDN (ou qualquer fonte via CDN externo) | Dois requests externos (fonts.googleapis.com + fonts.gstatic.com) que bloqueiam render. Self-hospedar subset WOFF2. |
| `font-display: swap` | Re-pinta o LCP quando a fonte carrega, disparando novo ciclo de LCP. Usar `font-display: optional`. |
| Thumbnail do VSL apontando para CDN externo (YouTube, etc.) | DNS+TLS externo no caminho crítico do LCP. Baixar, converter para WebP e self-hospedar. |
| `<img>` sem `height: auto` no CSS global quando tem atributo `height` | Atributo `height` vira pixel fixo e distorce a imagem em containers responsivos. Reset `img { height: auto }` é obrigatório. |
| `<link rel="preload" as="image">` sem `imagesrcset` para imagem com srcset | Preload baixa sempre o arquivo maior, ignorando a seleção responsiva do `srcset`. Usar `imagesrcset` + `imagesizes` no preload. |
| Deploy sem `vercel.json` com cache headers | Assets ficam com cache curto por padrão — Lighthouse penaliza e usuários re-baixam assets imutáveis a cada visita. |
