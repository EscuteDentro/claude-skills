"""Roda o fluxo OAuth (installed app) uma única vez pra gerar o refresh
token de acesso ao Google Contatos (People API). Abre o navegador padrão
pro consentimento; salva o token fora do repo (caminho em config.py).

Antes de rodar: confirme com o usuário qual CONTA GOOGLE ele quer autorizar
aqui -- é a conta que vai receber os contatos desta ferramenta, e pode não
ser a conta principal dele (ex: uma conta dedicada a WhatsApp Business).
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow

import config

SCOPES = ["https://www.googleapis.com/auth/contacts"]


def main():
    client_secret_path = os.path.expanduser(config.OAUTH_CLIENT_SECRET_PATH)
    token_path = os.path.expanduser(config.OAUTH_TOKEN_PATH)
    flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
    creds = flow.run_local_server(port=0, open_browser=False)
    with open(token_path, "w") as f:
        f.write(creds.to_json())
    os.chmod(token_path, 0o600)
    print(f"OK — token salvo em {token_path}")


if __name__ == "__main__":
    main()
