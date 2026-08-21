"""Copie este arquivo para `config.py` (já no .gitignore) e preencha com os
valores reais do seu projeto. `config.py` NUNCA deve ser commitado — nem
neste repo público, nem em nenhum outro lugar com histórico compartilhado.
"""

# ID da planilha (no meio da URL: docs.google.com/spreadsheets/d/{ISSO}/edit)
SHEET_ID = "{SEU_SHEET_ID}"

# Nome da aba onde o modal pré-checkout grava os leads
SHEET_TAB = "Leads"

# Nome da aba com os templates de mensagem (ferramenta de WhatsApp).
# Só precisa existir se você for usar essa ferramenta.
BANCO_MENSAGENS_TAB = "Banco de Mensagens"

# E-mail que recebe o aviso diário de leads novos (ferramenta de e-mail).
EMAIL_AVISO = "{seu-email@exemplo.com}"

# Caminho da credencial de Service Account (Sheets API). Nunca commitar
# esse arquivo em lugar nenhum -- fica fora de qualquer repositório git.
SERVICE_ACCOUNT_KEY_PATH = "{caminho/fora/do/repo/service-account.json}"

# Caminhos da credencial OAuth (People API / Google Contatos) -- só
# necessários se for usar a ferramenta "salvar contatos no Google".
OAUTH_CLIENT_SECRET_PATH = "{caminho/fora/do/repo/oauth-client.json}"
OAUTH_TOKEN_PATH = "{caminho/fora/do/repo/oauth-token.json}"

# Corte em dias entre template "quente" e "frio" na ferramenta de WhatsApp/
# e-mail diário. 5 é só um ponto de partida razoável -- ajuste pro seu ciclo
# de vendas (produto de decisão rápida pode querer 2-3; ciclo longo, 7+).
DIAS_CORTE_QUENTE_FRIO = 5

# Trecho fixo que identifica um contato criado por este skill (usado tanto
# pra buscar os contatos existentes quanto pra montar o nome novo). Escolha
# algo que não colida com contatos pessoais reais seus -- ex: o nome do seu
# produto/marca + "Lead". Nunca deixe genérico demais (tipo só "Lead"), ou
# risco de mexer em contato que não é deste fluxo.
CONTATO_MARCADOR = "Lead PréCheckout {SeuProduto}"

# Padrão de nome completo pros contatos criados/atualizados. {mes_ano} vira
# o mês/ano do lead mais recente (ex: 08.26). {sufixo_multiplo} vira "+"
# quando a pessoa tem mais de 1 entrada na Sheet.
NOME_CONTATO_TEMPLATE = "{{primeiro_nome}} " + CONTATO_MARCADOR + " {{mes_ano}}{{sufixo_multiplo}}"
