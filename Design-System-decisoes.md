# Design-System: Decisoes Fechadas

Data: 2026-05-11

## Botao CTA
- Variacao B aprovada: ambar #E8A820 + texto ink #1A2E3F + box-shadow outline 2.5px #1A2E3F
- Sem texto branco sobre ambar (contraste insuficiente)

## Fundo de secoes alternadas
- Glacial #E0F0F8 (nao creme). Motivo: azul tem mais energia que cinza, e mantem coerencia com a logo

## Logo
- Arquivo: `assets/logo.png` (substituir pelo caminho da sua logo)
- Hex estimados de exemplo: brand #2B5580, glacial #E0F0F8, ambar #E8A820, ripple #9CCAD8
- Logo pode ser colocada sobre qualquer secao brand-ice sem preocupacao de fundo

## Nome do sistema
- Design-System (adaptar nome ao projeto)

## Tipografia
- ~~H1/H2: Cormorant Garamond (serifa, ancora no ancestral)~~ — SUBSTITUÍDO
- ~~H3+, body, UI: Inter (maxima legibilidade)~~ — SUBSTITUÍDO
- **Atual:** Montserrat em todos os níveis (H1–H6, body, UI) — decisão mantém coerência com o site original
- Escala modular x1.25, base 17px (mantido)

## Bloco de preço — tipografia

- `preco-main`: 40px mobile / 48px desktop
- `preco-parcela` ("12x de", span dentro de preco-main): 32px mobile / 40px desktop; `letter-spacing: -0.03em`
- `preco-label` ("Por apenas"): 19px mobile / 21px desktop
- `preco-alt` ("ou R$ X à vista"): 21px mobile / desktop
- `preco-seguro` ("Pagamento 100% seguro..."): 14px, `white-space: nowrap` — manter em linha única; não aumentar sem testar no menor mobile

## Arquivo principal
- seuprojeto/design-system.json

## Tracking — Pixel + CAPI (decisão fechada 2026-07-01, atualizado 2026-07-02)

**Arquitetura aprovada:** Pixel browser + CAPI server-side em paralelo para 100% de cobertura.

- `META_CAPI_KEY` — token de acesso encrypted no Vercel (nunca em código ou `.env` commitado)
- Pixel ID: `0000000000000000` (hardcoded em `api/capi.js`)
- `event_id` via `crypto.randomUUID()` — gerado antes de cada `fbq()`, passado para Pixel e CAPI. Deduplicação garantida pelo Meta dentro de 48h.
- PII no Lead: email + phone (E.164 sem `+`, DDI 55 prefixado) + nome — todos hasheados SHA-256 com `toLowerCase().trim()` antes de enviar.
- `_fbc` reconstruído do `fbclid` da URL dentro de `loadTracking()` — 90 dias, `SameSite=Lax` (mitiga Safari ITP).
- `country`: `sha256('br')` hardcoded em todos os eventos — eleva EMQ sem PII adicional.
- `external_id`: UUID gerado pós-consent em `localStorage._app_eid`, sha256 antes do envio ao CAPI — conecta sessões cross-visit (produto raramente comprado no mesmo dia do primeiro acesso).
- EMQ baseline pré-CAPI: 7.2/10. Meta pós-CAPI com PII: ≥ 8.5.

**Eventos rastreados na LP (nossa camada):**
PageView · ViewContent · VSLPlay · VSLProgress25 · VSLProgress75 · ScrollDepth70 · FAQOpen · PrecheckoutOpen · PrecheckoutEmailDigitado · PrecheckoutAbandono · Lead

**Eventos rastreados pelo Hotmart (não duplicar):**
InitiateCheckout · Purchase

**Fixes CAPI (verificados em produção, 2026-07-08):**
- **4a — `_fbc` fallback:** se cookie ausente, reconstruir de `fbclid` na URL. Body só inclui `fbc` se não-vazio.
- **4b — IP do usuário:** `x-real-ip` antes de `x-forwarded-for` em `capi.js` — captura IPv6. Verificado: IP não-vazio, formato correto.
- **4c — PII de retorno:** PII salva em `localStorage._app_pii` após Lead; `_capi()` inclui automaticamente em eventos futuros do visitante.

**InitiateCheckout CAPI Hotmart (pendente especialista, 2026-07-08):** zero evidência de CAPI para IC em produção. Purchase CAPI confirmado. Aguardando especialista para decisão.

**Microsoft Clarity** (ID `clarityid0000`) — custom tags via `clarity('set', key, value)`:
`vsl_played` · `vsl_progress` (25/75) · `modal_opened` · `lead_captured` · `traffic_source` · `scroll_depth_70` · `exit_intent`

## Performance — decisões fechadas (2026-07-02)

- `decoding="async"` em todas as 56 imagens, incluindo LCP (safe com `fetchpriority="high"`)
- `dns-prefetch` como fallback nos mesmos domínios com `preconnect` (bug Safari)
- `og:image`: JPEG 65KB (era PNG 637KB, −90%)
- HTML: `max-age=0` (browser revalida sempre) + `s-maxage=86400, stale-while-revalidate=86400` (CDN serve cache 24h); raiz `/` tem regra separada idêntica
- Assets: `max-age=31536000, s-maxage=31536000, immutable` (browser + CDN, 1 ano)
- robots.txt e sitemap: `max-age=86400`
- Preload VSL thumbnail via `<link rel="preload" as="image" imagesrcset="...">` (sem picture/AVIF simultâneo — double download)
- Prefetch da URL Hotmart no `<head>` para acelerar redirect no submit
- Headers de segurança HTTP via `vercel.json` (bloco global `/(.*)`): `X-Content-Type-Options: nosniff` · `X-Frame-Options: SAMEORIGIN` · `X-XSS-Protection: 0` · `Referrer-Policy: strict-origin-when-cross-origin` — aplicados em produção desde 2026-07-03
