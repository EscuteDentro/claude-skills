"""Ferramenta de salvar contatos no Google.

Cliente autenticado (OAuth) pra People API (Google Contatos). Token gerado
uma vez via oauth_setup.py; refresh automático depois disso.

IMPORTANTE -- pergunte ao usuário ANTES de configurar: qual conta Google
esses contatos devem ser salvos? Pode ser diferente da conta principal --
é comum usar um número de WhatsApp Business separado do pessoal, ou um
e-mail diferente do que a pessoa usa no dia a dia. O OAuth roda contra a
conta que autorizar no navegador quando oauth_setup.py for executado, e é
essa conta que vai receber os contatos -- confirme qual é antes de gerar
o token.
"""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

import config

SCOPES = ["https://www.googleapis.com/auth/contacts"]


def get_service():
    token_path = os.path.expanduser(config.OAUTH_TOKEN_PATH)
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "w") as f:
            f.write(creds.to_json())
        os.chmod(token_path, 0o600)
    return build("people", "v1", credentials=creds)


def list_lead_contacts():
    """Retorna lista de dicts {resourceName, name, phones, emails} de todos os
    contatos cujo nome contém config.CONTATO_MARCADOR."""
    service = get_service()
    results = []
    page_token = None
    while True:
        resp = service.people().connections().list(
            resourceName="people/me",
            pageSize=1000,
            personFields="names,phoneNumbers,emailAddresses",
            pageToken=page_token,
        ).execute()
        for person in resp.get("connections", []):
            names = person.get("names", [])
            display = names[0]["displayName"] if names else ""
            if config.CONTATO_MARCADOR in display:
                phones = [p.get("value", "") for p in person.get("phoneNumbers", [])]
                emails = [e.get("value", "") for e in person.get("emailAddresses", [])]
                results.append({
                    "resourceName": person["resourceName"],
                    "etag": person["etag"],
                    "name": display,
                    "phones": phones,
                    "emails": emails,
                })
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return results


if __name__ == "__main__":
    contacts = list_lead_contacts()
    print(f"Total de contatos '{config.CONTATO_MARCADOR}': {len(contacts)}")
    for c in contacts:
        print(f"  {c['name']} | tel={c['phones']} | email={c['emails']}")
