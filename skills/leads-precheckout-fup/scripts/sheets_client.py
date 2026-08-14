"""Cliente autenticado (service account) para a Sheet de leads pré-checkout.

Credencial NUNCA fica neste repo nem em nenhum outro com histórico
compartilhado -- caminho lido de config.py, que aponta pra fora de qualquer
repositório git.
"""
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

import config

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_service():
    key_path = os.path.expanduser(config.SERVICE_ACCOUNT_KEY_PATH)
    creds = service_account.Credentials.from_service_account_file(key_path, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def get_all_rows(tab=None):
    """Retorna (headers, rows) -- rows é lista de listas, sem o cabeçalho.

    Range com folga (A1:AZ) pra nao truncar silenciosamente se voce
    adicionar coluna nova no futuro.
    """
    service = get_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=config.SHEET_ID, range=f"{tab or config.SHEET_TAB}!A1:AZ"
    ).execute()
    values = result.get("values", [])
    headers, rows = values[0], values[1:]
    return headers, rows


def update_cell(a1_range, value, tab=None):
    """Escreve UM valor. Sempre revisar em dry-run antes de chamar contra dados reais."""
    service = get_service()
    service.spreadsheets().values().update(
        spreadsheetId=config.SHEET_ID, range=f"{tab or config.SHEET_TAB}!{a1_range}",
        valueInputOption="RAW", body={"values": [[value]]}
    ).execute()
