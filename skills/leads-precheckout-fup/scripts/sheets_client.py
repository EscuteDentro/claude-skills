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
    """Escreve UM valor. Sempre revisar em dry-run antes de chamar contra dados reais.
    Pra mais de ~20 células, usar batch_update_cells -- update_cell em loop
    estoura a quota de 60 write requests/min da Sheets API rapidinho."""
    service = get_service()
    service.spreadsheets().values().update(
        spreadsheetId=config.SHEET_ID, range=f"{tab or config.SHEET_TAB}!{a1_range}",
        valueInputOption="RAW", body={"values": [[value]]}
    ).execute()


def batch_update_cells(updates, tab=None):
    """Escreve várias células numa ÚNICA chamada de API (values.batchUpdate).
    `updates`: lista de (a1_range, value). Sempre revisar em dry-run antes de
    chamar contra dados reais.
    """
    if not updates:
        return
    service = get_service()
    tab_name = tab or config.SHEET_TAB
    data = [
        {"range": f"{tab_name}!{a1_range}", "values": [[value]]}
        for a1_range, value in updates
    ]
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=config.SHEET_ID,
        body={"valueInputOption": "RAW", "data": data},
    ).execute()
