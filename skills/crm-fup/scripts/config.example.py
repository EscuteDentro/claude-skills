"""Copie este arquivo para `config.py` (já no .gitignore) e preencha com os
valores reais do seu projeto. `config.py` NUNCA deve ser commitado — nem
neste repo público, nem em nenhum outro lugar com histórico compartilhado.

Se você já tem o skill `crm-lead` instalado, reaproveite o `config.py` dele
como base: SHEET_ID e SERVICE_ACCOUNT_KEY_PATH são os mesmos (mesma Sheet,
mesma credencial), só adicione as variáveis novas desta lista que ele não
tem.
"""

# ID da planilha (no meio da URL: docs.google.com/spreadsheets/d/{ISSO}/edit)
SHEET_ID = "{SEU_SHEET_ID}"

# Nome da aba onde o crm-lead grava os leads (mesma origem)
LEADS_TAB = "Leads"

# Abas que este skill cria/mantém. Pode renomear à vontade -- só use o
# mesmo nome em todo lugar.
FUP_TAB = "FUP"
DORES_DESEJOS_TAB = "Dores e Desejos"
BANCO_COPIES_TAB = "Banco de Copies"

# Caminho da credencial de Service Account (Sheets API). Nunca commitar
# esse arquivo em lugar nenhum -- fica fora de qualquer repositório git.
SERVICE_ACCOUNT_KEY_PATH = "{caminho/fora/do/repo/service-account.json}"

# Termo de busca usado no WhatsApp Web pra achar os contatos deste fluxo.
# Precisa bater com o padrão de nome que você usa pra salvar lead no
# WhatsApp/Contatos -- se você usa o CONTATO_MARCADOR do crm-lead
# ("Lead PréCheckout {SeuProduto}"), uma palavra única dele (ex: "Lead")
# já filtra certo. Escolha algo que não colida com contato pessoal seu.
MARCADOR_BUSCA_WHATSAPP = "{palavra-marcador, ex: Lead}"

# Taxonomia de Categoria pra síntese (aba Dores e Desejos / Banco de Copies).
# Comece VAZIO ou com 1-2 categorias óbvias do seu negócio -- defina o
# resto a partir dos primeiros achados reais, nunca adivinhe categoria
# antes de ter conversa de verdade pra basear nela. Ex. de ponto de
# partida: motivo prático (preço, tempo), motivo emocional, dúvida sobre
# o produto -- mas troque pelas categorias que emergirem do seu público.
CATEGORIAS = ["{categoria 1}", "{categoria 2}", "Outro"]

# Guias de copy opcionais do seu projeto. Se não existirem, o skill
# simplesmente não os consulta -- não é obrigatório ter.
GUIA_COPY_PATH = None  # ex: ".claude/rules/copy/guia-de-copy.md"
MANUAL_HOOKS_PATH = None  # ex: ".claude/rules/copy/manual-hooks.md"

# Limites de segurança contra bloqueio de conta (ver SKILL.md, seção
# "Segurança contra bloqueio"). Valores conservadores por padrão -- só
# afrouxar com critério.
TETO_CONVERSAS_POR_RODADA = 20
LOTE_TAMANHO = 10
MIN_MINUTOS_ENTRE_RODADAS = 30
