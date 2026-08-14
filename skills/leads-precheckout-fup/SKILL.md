---
name: leads-precheckout-fup
description: Extensão OPCIONAL do modal pré-checkout — planilha de acompanhamento com CRM (status + semáforo), sinalização de duplicata, e-mail diário de leads novos, link wa.me pronto pra clicar e sincronização com Google Contatos. Cada ferramenta é independente; escolha só as que quiser.
user-invocable: true
---

> **Instalação:** copiar esta pasta para `.claude/skills/leads-precheckout-fup/` no projeto e criar o command apontando para o SKILL.md. Preencher `scripts/config.py` (copiar de `config.example.py`) e `apps_script_template.gs` antes de usar. Ver [README.md](./README.md) para o passo a passo completo.

---

# Leads Pré-checkout — Follow-up (FUP)

Extensão **opcional** do modal pré-checkout (ver seção "Modal pré-checkout" no Guia de Construção da Página). Sem este skill, os leads já são capturados e salvos normalmente na Sheet — estas ferramentas adicionam acompanhamento e facilitam o re-contato de quem não comprou.

## LGPD

Todo o desenho respeita a LGPD: consentimento explícito antes de qualquer contato (`Consentiu WA`), nenhum envio automático em massa, dado sensível fica só na Sheet do próprio usuário (nunca em serviço terceiro além do Google). **Se você quiser entender a lógica de compliance em detalhe — o que é coletado, com que base legal, como pedir exclusão — pergunte ao Claude durante a conversa; ele explica antes de configurar qualquer coisa.**

## Modular — leia e decida

**Você não precisa (nem deve) implementar tudo.** Cada ferramenta abaixo é independente, com seu próprio requisito de configuração. Leia a lista, decida quais quer, e **avise explicitamente quais NÃO quer** — o Claude pula a etapa de setup correspondente e a Sheet continua funcionando sem elas (só fica sem aquele recurso específico).

### Pré-requisito comum

Um projeto no Google Cloud (gratuito) com a **Sheets API** habilitada + uma **Service Account** (chave JSON) com acesso de leitura/escrita à Sheet. Isso é infraestrutura — passo que exige sua aprovação explícita antes de rodar, mesmo que pareça óbvio pelo contexto. Sem isso, nenhuma ferramenta abaixo funciona (mas o modal pré-checkout continua funcionando normalmente).

A ferramenta 6 (salvar contatos no Google) precisa de mais um setup, à parte: **People API + OAuth Client**, listado nela.

---

### 1. CRM — status + semáforo visual

Coluna "Status CRM" na Sheet + cor de linha automática: cinza (sem consentimento — nunca contatar), verde (já comprou), vermelho (precisa contatar). Script: `aplicar_formatacao.py`.

**Requer:** só o pré-requisito comum.
**Se não quiser:** avise — a Sheet fica com os dados crus, sem cor automática; você acompanha manualmente.

### 2. Sinalização de duplicação

A mesma pessoa pode se cadastrar mais de uma vez (curiosidade, esquecimento, dispositivo diferente). Esta ferramenta detecta isso (por e-mail OU telefone repetido), numera as entradas em ordem cronológica (`1`, `2`, `3*`...) e marca com `*` quando o telefone ou e-mail muda entre uma entrada e outra da mesma pessoa. Scripts: `verificar_duplicados.py` (pente-fino, só leitura), `plan_duplicado.py` (dry-run) → `execute_duplicado.py` (escreve, só após confirmação), `validar_logica_numeracao.py` (auditoria a qualquer momento).

**Requer:** só o pré-requisito comum.
**Se não quiser:** avise — cada novo cadastro vira uma linha nova sem checagem de duplicata; você mesmo identifica manualmente se quiser.

### 3. WhatsApp — link pronto pra clicar

Biblioteca pequena de templates de mensagem (aba "Banco de Mensagens" na mesma Sheet — nunca um log de tudo que foi enviado) + gerador de link `wa.me` com a mensagem já preenchida, escolhendo automaticamente o template "quente" (lead recente) ou "frio" (lead mais antigo) pela data de captura. Scripts: `criar_banco_mensagens.py` (cria a estrutura vazia — você preenche o texto com suas próprias mensagens, nunca use texto de exemplo como se fosse real), `gerar_link_whatsapp.py`.

**O link é só pra você clicar.** Este skill nunca abre WhatsApp Web, nunca envia mensagem, nunca automatiza envio em lote — isso é proibido em qualquer circunstância, mesmo se pedido explicitamente (risco de suspensão de conta pela política do WhatsApp/Meta contra automação).

**Requer:** pré-requisito comum + você escrever seus próprios templates na aba "Banco de Mensagens" antes de usar.
**Se não quiser:** avise — a ferramenta de e-mail diário (#5) ainda funciona, só sai sem o link pronto.

### 4. Correção de telefone (WhatsApp, específico do Brasil)

Números de celular brasileiros podem estar registrados no WhatsApp no formato antigo (8 dígitos, sem o 9 extra) mesmo quando a Sheet guarda o formato novo (9 dígitos) — buscar só uma forma dá falso negativo. Esta ferramenta salva as duas variantes no mesmo contato do Google. Script: `add_phone_variant.py` (chamado automaticamente por `execute_contacts_update.py` ao criar contato novo).

**Requer:** ferramenta 6 (salvar contatos) ativa — a variante é salva no próprio contato.
**Se não quiser, ou se seu público não é majoritariamente brasileiro:** avise — a busca manual no WhatsApp pode falhar silenciosamente pra parte dos leads com número antigo.

### 5. E-mail diário de leads novos

Um e-mail por dia (só se houver lead novo nas últimas 24h — nunca envia à toa) resumindo quem chegou, com o link `wa.me` da ferramenta 3 já pronto pra clicar em cada nome (se você não ativar a ferramenta 3, o e-mail sai só com nome + aviso pra usar e-mail). Implementado como função no Apps Script (`emailLeadsDiarios()`) + acionador por tempo (`criarAcionadorDiario()`, roda 1x pra registrar, dispara todo dia às 8h).

**Requer:** só o pré-requisito comum (Sheets API). Não depende de People API/Contatos.
**Se não quiser:** avise — você mesmo confere a Sheet manualmente pra ver quem chegou.

### 6. Salvar contatos no Google

Cria/atualiza um contato no Google Contatos pra cada lead elegível (nunca pra quem comprou ou não consentiu), com nome padronizado (`{Nome} {marcador} {mês.ano}`) — facilita reconhecer o lead quando ele te chama depois. Scripts: `oauth_setup.py` (rodar 1x), `contacts_client.py`, `plan_contacts_update.py` (dry-run) → `execute_contacts_update.py` (escreve, só após confirmação).

**Requer:** People API habilitada no mesmo projeto Google Cloud + OAuth Client (tipo "App para computador").

**Antes de configurar, pergunte ao usuário: qual conta Google deve receber esses contatos?** Pode ser diferente da conta pessoal dele — é comum usar um número de WhatsApp Business separado, ou um e-mail dedicado só a isso, justamente pra manter os contatos de lead separados dos contatos pessoais. O OAuth (`oauth_setup.py`) autoriza a conta que a pessoa escolher no navegador na hora — confirme qual é antes de gerar o token.

**Se não quiser:** avise — as ferramentas 1, 2, 3 e 5 funcionam normalmente sem isso; só perde o reconhecimento automático do lead nos seus contatos e a ferramenta 4 (correção de telefone) fica sem efeito.

---

## Fluxo ao rodar (depois de configurado)

1. `python3 verificar_duplicados.py` — pente-fino, sempre primeiro, só leitura. Se achar algo estranho (marcação órfã), pare e avise — não conserte sozinho sem contexto.
2. Se ativou a ferramenta 2: `python3 plan_duplicado.py` → mostrar pro usuário → só com confirmação, `python3 execute_duplicado.py`.
3. Se ativou a ferramenta 3: listar quem precisa de contato (`Status CRM` vazio + `COMPROU` ≠ Sim), gerando o link com `gerar_link_whatsapp.py` pra quem `Consentiu WA = Sim`; quem não consentiu, só o nome + aviso de usar e-mail. Nunca gerar link pra quem não consentiu, mesmo se pedido.
4. Se ativou a ferramenta 6: `python3 plan_contacts_update.py` → mostrar plano completo (renomear/criar) → só com confirmação, `python3 execute_contacts_update.py`.
5. Fechar com um resumo: quantas duplicatas achadas/marcadas, quantos leads sem contato (com link), quantos contatos renomeados/criados. Sem inventar número — só o que os scripts realmente reportaram.

## Regras absolutas — nunca violar, mesmo se pedido

- Nunca gerar link `wa.me` nem sugerir texto de mensagem pra quem tem `Consentiu WA = Não`. Nunca contar essa pessoa como alvo de contato.
- Link gerado é só pra o usuário clicar — o Claude nunca clica, nunca envia, nunca abre WhatsApp Web pra mandar nada.
- Nunca automatizar envio de mensagem em lote via WhatsApp Web, nem checar registro em volume, sem alertar antes — risco real de suspensão de conta.
- Nunca escrever numa linha de lead que já comprou (`COMPROU = Sim`) — essa pessoa saiu do escopo deste fluxo.

## Editar o Apps Script depois de implantado

Ver o aviso completo no topo de `apps_script_template.gs`. Resumo: salvar no editor do navegador **não** republica a URL `/exec` já em produção — é preciso ir em Implantar → Gerenciar implantações → Nova versão → Implantar. Depois de republicar, valide com um POST real contra a URL (mesmo formato que o modal usa), nunca só pela aparência do código salvo no editor.

Pra editar código diretamente no editor Monaco do navegador (script.google.com): usar a API do Monaco via ferramenta de JavaScript (`window.monaco.editor.getModels()[0].getLineContent(n)` pra inspecionar, `getEditors()[0].executeEdits(...)` pra editar) — nunca colar via clipboard do sistema operacional (pode ser sobrescrito silenciosamente por sync entre dispositivos) nem usar tecla de navegação com nome especial tipo "Page Down"/"End" (pode ser digitada como texto literal em vez de navegar).

## Se faltar credencial ou o fluxo quebrar

Não tente recriar Service Account/OAuth sozinho sem aprovação explícita — é infraestrutura (Google Cloud Console, tela de consentimento OAuth) que precisa confirmação antes de rodar. Avise o usuário e pare.
