---
name: avaliar-ideia
description: Avalia a utilidade real de uma ideia, ferramenta ou skill de terceiro (slide, post, Reddit/X, repositório de código) para qualquer ponto do processo/negócio ativo. Lê a fonte real (nunca marketing), extrai o mecanismo por trás mesmo se a fonte for hoax/clickbait, gera o leque de oportunidades cross-domain antes de filtrar por risco, mapeia sinergia/arquitetura com o que já existe, separa risco em eixos (segurança, jurídico, ToS de plataforma), avalia se vale publicar em repositório público, e dá veredito com esforço/custo. Oferece registrar em backlog se aprovada.
user-invocable: true
---

# Avaliar Ideia

Avalia se uma ideia, ferramenta ou skill que alguém compartilhou (slide, link de Reddit/X/GitHub, texto colado) vale a pena adotar em algum ponto do processo/negócio ativo. Não é brainstorm livre nem parecer técnico solto — é um processo de duas passadas em ordem fixa, porque inverter a ordem poda ideia boa antes dela aparecer.

## 0. Ler a fonte real, nunca o resumo ou o marketing

**Regra dura:** avaliar o objeto real, não a descrição dele.

- **Link de repositório/skill (GitHub etc.):** localizar e ler o código-fonte de verdade antes de opinar. Nunca julgar pelo README, pitch ou marketing — pode ter algo genial (ou um problema grave) que só aparece no código.
- **Link de Reddit/X/artigo:** abrir o link real (WebFetch/leitura de página), não confiar só no texto que a pessoa colou — thread e comentários podem mudar a leitura.
- **Slide/screenshot:** ler visualmente, extrair a ideia central. Ignorar o quão bem produzido o slide é — isso não é sinal de qualidade da ideia.
- **Texto colado direto:** usar como está, mas checar se há link embutido que vale abrir.

**Fonte difícil de acessar** (link quebrado, paywall, PDF protegido, imagem ilegível, repo privado): não tentar contornar às cegas nem avaliar pela metade. Pedir outra forma de acesso ao usuário, informando o trade-off do meio que ele passou (ex: "esse link exige login — dá pra eu tentar via busca do título, mas perco o texto exato dos comentários; prefere colar o conteúdo direto ou me passar de outro jeito?").

Se a fonte citar número, resultado ou case ("aumentou X%", "validado por Y"), tratar como alegação a verificar, não fato — buscar a fonte primária se for decisivo pro veredito.

**Hoax, clickbait ou promessa que não se sustenta:** não encerrar a avaliação aí. Separar duas perguntas — "isso funciona/existe de verdade como anunciado?" de "existe um princípio ou mecanismo aproveitável por trás, mesmo que por outro caminho?". Se a segunda resposta for sim, seguir pro leque de oportunidades sobre o mecanismo (não sobre a fonte fraudulenta), deixando claro no veredito que a via de implementação real seria outra, não a ferramenta/post original. Vale também para conceito bom com execução ruim (não precisa ser hoax): propor o caminho novo que realizaria o conceito direito.

**Antes de propor um caminho novo, pesar custo de reinventar a roda:** se já existe ferramenta/skill/serviço estabelecido que entrega o mesmo mecanismo, comparar o esforço de construir do zero contra adotar/adaptar o que já existe (ver "Sinergia e arquitetura" na passada 2) — caminho novo só se justifica quando resolve algo que a alternativa pronta não resolve, não por preferência.

## 1. Passada 1 — leque de oportunidades, sem filtro de risco ainda

Objetivo: não deixar risco/custo podar uma ideia genial antes de ela ser mapeada por inteiro. Ser criativo e pensar fora da caixa é o valor central desta passada, não um extra.

- **Inventário real antes da varredura:** listar o que já está em uso no projeto — `.claude/skills/`, `.claude/commands/`, agentes disponíveis (listagem do Skill tool) — antes de aplicar a lista de domínios abaixo. Isso separa as duas categorias de oportunidade, que pedem tratamento diferente no veredito: **reforço** (domínio já coberto por skill/ferramenta existente — a ideia melhora ou substitui algo que já roda) vs. **território novo** (domínio sem cobertura nenhuma — a ideia abre uma frente que não existia). Território novo tende a valer mais atenção: é o que ninguém pensaria de cara.
- **Mecanismo, não rótulo:** identificar o que a ideia faz de verdade por baixo do produto/categoria em que foi embalada (ex: uma skill de "animar site" é, no fundo, um motor de transição/timing — aplicável a animação de vídeo, não só a site). Avaliar o mecanismo abre mais oportunidade do que avaliar a categoria original.
- **Varredura cross-domain obrigatória, em duas camadas:** checar explicitamente contra cada frente abaixo, mesmo que a ideia pareça pertencer só a uma — não pular nenhuma sem justificar por que não se aplica. Adaptar a lista ao negócio ativo; a lista nunca é teto — se o mecanismo sugerir uma frente fora dela, criar a categoria na hora e nomear por quê, em vez de forçar encaixe numa das existentes.
  - **Camada operacional** (mede reforço — melhora o que já roda). Ponto de partida genérico:
    - Copy e anúncios (páginas, criativos, roteiro de vídeo)
    - Revisão e qualidade de texto
    - Concepção de produto do zero (pesquisa, oferta, posicionamento)
    - Produção e edição de vídeo/áudio (corte, legenda, animação, efeitos, voz)
    - Captação e conversão de clientes (tráfego pago, CRM, follow-up, vendas 1:1)
    - Páginas e infraestrutura (LP, tracking, deploy)
    - Conteúdo orgânico e distribuição (redes sociais, formatos)
  - **Camada estrutural/estratégica** (mede território novo — é onde mora o disruptivo, porque não tem skill/ferramenta cobrindo hoje). Ponto de partida genérico:
    - Retenção e comunidade pós-venda (cliente depois que compra — a camada operacional acima para na conversão)
    - Modelo de negócio e precificação (upsell, bundle, assinatura vs. pagamento único)
    - Parcerias e canais de distribuição (afiliados, colabs, canal que hoje não existe)
    - Alavancagem pessoal/operação interna (automatizar o próprio tempo de trabalho, não algo client-facing)
    - Diferenciação competitiva (o que torna difícil de copiar)
    - Produtos ou mercados adjacentes (fora do produto/negócio atual)
    - Dados e decisão (visibilidade que hoje só existe manualmente)
- **Teste de segunda ordem, pra separar reforço de disruptivo:** essa ideia melhora um passo dentro do que já existe, ou muda como o negócio opera como um todo — remove uma categoria inteira de trabalho manual, muda a economia unitária, abre um canal que hoje não existe? A segunda resposta é o sinal de oportunidade disruptiva; não deixar passar batido só porque não é o que a fonte original prometia.
- **Cenário ideal:** se essa ideia funcionar 100%, o que ela substitui ou resolve? Nomear a alternativa concreta que já estava cotada ou em uso, se houver (ex: "isso substituiria a ferramenta X que eu já pago" é mais forte que "isso parece útil").
- **Além do pedido original:** que outros usos, adjacentes ao que a pessoa que compartilhou tinha em mente, isso abre no negócio? Ser exaustivo — é aqui que se ganha ou perde a avaliação, não na parte de risco.
- **Pesquisar se necessário:** se faltar contexto de mercado, fluxo ou case real pra avaliar direito, ou pra enriquecer a lista de aplicações possíveis, buscar (WebSearch/WebFetch) em vez de chutar.

## 2. Passada 2 — filtro, aplicado por cima do leque da passada 1

Nunca fazer esta parte primeiro.

- **Sinergia e arquitetura, antes de propor qualquer integração:** para cada oportunidade que sobreviver até aqui, mapear contra o catálogo real de skills/agentes/commands já ativos no projeto (listar `.claude/skills/`, `.claude/commands/`, agentes disponíveis) — não propor "criar skill nova" ou "integrar em X" sem antes checar se algo equivalente já existe.
  - **Redundância:** é upgrade real, é redundante com algo que já cobre isso, ou preenche gap genuíno? Nomear a skill/ferramenta irmã se houver.
  - **Arquitetura e paths explícitos, sempre:** desenhar onde cada peça mora antes de propor qualquer coisa — arquivo/pasta exatos que seriam criados vs. tocados, e se envolve par privado/público (ver seção 3), path de cada lado separado e nomeado. Nunca falar em abstrato ("integraria com o sistema de X"); listar os paths como bloco visível (ex: lista com `caminho/arquivo.ext` — criado, `caminho/outro.ext` — modificado), delimitado do resto do texto, fácil de escanear.
  - **Reforço nos dois lados:** se a proposta é reforçar uma skill existente (não criar uma nova), garantir que a mudança fique registrada nela mesma (nota de manutenção, seção nova) e não só na conversa — mesma lógica do padrão de skills gêmeas (ver seção 3), pra não passar batido numa sessão futura.
- **Esforço e viabilidade:** tempo pra adotar/adaptar, dependência externa, custo de API (converter pra moeda local se relevante). Se a decisão for "essa ferramenta OU uma alternativa já cotada", usar os 4 critérios: qualidade, esforço, viabilidade, custo.
- **Qualquer custo, avisar antes de prosseguir:** custo de API, assinatura, ou uso elevado de tokens/agentes (ex: pipeline que dispara vários agents/forks, pesquisa longa, loop de refinamento) — mesmo sem dinheiro saindo do bolso diretamente, consumo desproporcional de tokens é custo real e precisa ser declarado, não só custo em API explícito.
- **Instalação ou uso de sistema de terceiro:** se adotar a ideia exige instalar pacote (`brew`/`npm`/`pip`/etc.) ou conectar a um serviço/API externa, fazer auditoria de segurança antes de instalar — idade do pacote/repo, número de mantenedores, atividade de commits, CVEs/advisories conhecidos, arquivos de alto risco alterados em releases recentes. Reportar os achados de forma concisa e pedir confirmação explícita antes de instalar; nunca instalar durante a própria avaliação.
- **Risco — três eixos separados, nunca um "risco" genérico misturado:**
  - **Segurança/dados:** exposição de credencial, PII, exfiltração.
  - **Jurídico/regulatório:** proteção de dados (LGPD/GDPR conforme jurisdição), direitos autorais, compliance específico do nicho.
  - **ToS de plataforma:** automação/scraping em redes sociais (Meta, etc.) e afins — risco de suspensão de conta é **eliminatório sozinho**, nunca entra como trade-off aceitável junto com os outros dois eixos.
- **Existe risco inadmissível?** Declarar explicitamente se algum dos três eixos acima, sozinho, já mata a ideia — não deixar implícito dentro de um parágrafo de trade-offs.
- **Corner cases:** situação em que a ideia parece boa mas quebra (volume, escala, dependência de terceiro instável, mudança de política da plataforma).

## 3. Publicar em repositório público — decisão separada, nunca automática

Só se aplica quando o veredito de uma oportunidade for **Adotar/Adaptar** e resultar em skill ou script novo, ou alteração de um já existente, e o projeto mantiver algum repositório público (skills, ferramentas, templates).

- **Critério pra considerar publicar:** o mecanismo central não depende de dado privado, credencial ou config específica do negócio — se depende, ou fica só privado, ou publica-se uma versão agnóstica separada (padrão de skill gêmea: mesma lógica, sem os dados reais).
- **Se a skill tocada já tem gêmeo público:** propagar a mudança nos dois lados, nunca só de um.
- **Se decidir publicar, a versão agnóstica não pode carregar NADA do negócio real:** nenhum nome de produto, ID de planilha/pixel, config privada, exemplo com dado real de cliente/lead. Placeholders tipo `SEU_`/`TODO_` no lugar de qualquer valor real, e caminhos de arquivo genéricos (não assumir a estrutura de pastas específica do seu projeto).
- **Publicar (commit + push num repositório público) é ação externa e irreversível: sempre confirmar explicitamente com o usuário antes de executar — nunca fazer sozinho, mesmo que o conteúdo pareça óbvio, agnóstico ou já discutido no chat.** Apresentar o conteúdo final e esperar aprovação explícita antes do push.

## 4. Veredito

Um veredito por oportunidade relevante que sobreviveu à passada 2 — não um veredito único genérico quando o leque revelou mais de um encaixe real.

**Adotar** / **Adaptar** (útil, mas precisa mudança antes de usar) / **Vigiar** (não agora — falta maturidade, preço vai cair, esperar validação) / **Descartar** — com justificativa em 1-2 linhas cada.

**Assimetria de erro:** dúvida real entre veredictos vizinhos resolve pra cima (Vigiar > Descartar, Adaptar > Vigiar) — perder oportunidade boa custa mais que investigar uma ruim. **Descartar** só com risco eliminatório concreto ou redundância comprovada, nunca por incerteza.

Resposta final **concisa por padrão**: entregar o veredito e o essencial de cada passada, não o raciocínio completo. Aprofundar qualquer seção só se pedido depois.

## 5. Registro se aprovada

Se o veredito for **Adotar** ou **Adaptar**, oferecer (não fazer sem confirmar) salvar uma entrada num arquivo de backlog do seu projeto, formato:

```markdown
- [ ] **{{nome da ideia}}** — {{veredito}}, encaixa em {{ponto do processo}}
  - Fonte: {{link ou origem}}
  - Por quê: {{1 linha, a partir da passada 1}}
  - Próximo passo: {{ação concreta pra implementar}}
```

Se **Vigiar** ou **Descartar**, não registrar — fica só na conversa, a menos que o usuário peça explicitamente pra guardar o motivo do descarte (ex: pra não reavaliar a mesma ideia depois).
