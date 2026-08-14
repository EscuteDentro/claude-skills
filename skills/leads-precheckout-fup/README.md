# leads-precheckout-fup

Extensão opcional do modal pré-checkout: planilha de acompanhamento com CRM (status + semáforo), sinalização de duplicata, e-mail diário de leads novos, link `wa.me` pronto pra clicar e sincronização com Google Contatos. Ver [SKILL.md](./SKILL.md) pra descrição completa de cada ferramenta e o que cada uma exige.

## Pré-requisitos

- Python 3.9+
- Um produto já usando o **modal pré-checkout** do Guia (ver "Modal pré-checkout" no `Guia de Construção da Página.md`) — este skill assume que os leads já estão caindo numa aba da Sheet com as colunas Timestamp/Nome/E-mail/Telefone/Consentiu WA/COMPROU no mínimo.
- Projeto no [Google Cloud Console](https://console.cloud.google.com) (gratuito) com a **Sheets API** habilitada.
- Só se for usar a ferramenta "salvar contatos no Google": **People API** habilitada no mesmo projeto.

## Instalação

1. Copiar esta pasta inteira pra `.claude/skills/leads-precheckout-fup/` no seu projeto.
2. Instalar as dependências Python:
   ```bash
   pip install -r scripts/requirements.txt
   ```
3. Copiar `scripts/config.example.py` pra `scripts/config.py` e preencher com seus valores reais (Sheet ID, e-mail, caminhos de credencial). **`config.py` nunca deve ser commitado** — já está no `.gitignore` desta pasta, mas confira se o seu projeto principal também ignora esse arquivo.
4. Criar uma Service Account no Google Cloud (IAM & Admin → Contas de serviço → Criar), gerar uma chave JSON, salvar **fora de qualquer repositório git** (ex: `~/.credentials/`), e compartilhar a Sheet com o e-mail da Service Account como Editor.
5. Copiar `apps_script_template.gs` pro editor do Apps Script (script.google.com → Novo projeto), substituir `TODO_SHEET_ID` e `TODO_EMAIL_AVISO`, e seguir as instruções de deploy no topo do arquivo.
6. Só se for usar "salvar contatos": criar um OAuth Client (tipo "App para computador") no mesmo projeto Google Cloud, salvar o client secret fora do repo, e rodar `python3 scripts/oauth_setup.py` uma vez pra gerar o token — confirme antes qual conta Google deve receber esses contatos (pode ser diferente da conta pessoal).
7. Se for usar a ferramenta de WhatsApp: rodar `python3 scripts/criar_banco_mensagens.py` pra criar a estrutura da aba "Banco de Mensagens", depois preencher o texto de cada template com suas próprias mensagens (nunca deixe o texto de exemplo como se fosse real).

## Uso

Ver a seção "Fluxo ao rodar" no [SKILL.md](./SKILL.md). Todos os scripts de escrita (`execute_*.py`) têm um par de dry-run (`plan_*.py`/`verificar_*.py`) que deve ser mostrado ao usuário antes — nenhum script escreve na primeira chamada.

## LGPD

Este skill respeita a LGPD por desenho: nunca contata quem não deu consentimento explícito, nunca envia mensagem automaticamente (todo link é só pra clique manual), e todo dado fica só na sua própria Sheet/Contatos (nenhum serviço terceiro além do Google). Peça ao Claude mais detalhes sobre a lógica de compliance a qualquer momento.
