"""Cliente autenticado (service account) compartilhado pelos scripts deste
skill -- fonte única, nunca reimplementar get_service()/credencial em
script novo. Duplicar essa lógica em vários arquivos é como um range ou
mapa de coluna hardcoded errado sobrevive despercebido em mais de um
lugar sem ninguém notar.

Credencial NUNCA fica neste repo: caminho lido de config.py, que aponta
pra fora de qualquer repositório git.
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


def get_all_rows(tab):
    """Retorna (headers, rows) -- rows é lista de listas, sem o cabeçalho.

    Range com folga (A1:AZ) pra não truncar silenciosamente se você
    adicionar coluna nova no futuro -- um range curto demais derruba
    qualquer lookup por nome de cabeçalho na coluna que ficou de fora,
    sem erro nenhum até o ponto de uso real.
    """
    service = get_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=config.SHEET_ID, range=f"{tab}!A1:AZ"
    ).execute()
    values = result.get("values", [])
    if not values:
        return [], []
    headers, rows = values[0], values[1:]
    return headers, rows


def col_letter(index0based):
    n = index0based + 1
    letters = ""
    while n:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def update_cell(tab, a1_range, value):
    """Escreve UM valor. Pra mais de ~20 células, usar batch_update_cells --
    update_cell em loop estoura a quota de 60 write requests/min da Sheets API."""
    service = get_service()
    service.spreadsheets().values().update(
        spreadsheetId=config.SHEET_ID, range=f"{tab}!{a1_range}",
        valueInputOption="RAW", body={"values": [[value]]}
    ).execute()


def batch_update_cells(updates, tab):
    """updates: lista de (a1_range, value). Uma única chamada de API."""
    if not updates:
        return
    service = get_service()
    data = [{"range": f"{tab}!{a1_range}", "values": [[value]]} for a1_range, value in updates]
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=config.SHEET_ID,
        body={"valueInputOption": "RAW", "data": data},
    ).execute()
