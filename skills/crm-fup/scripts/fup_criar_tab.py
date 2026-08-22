"""Cria a aba FUP (só cabeçalho) se ela ainda não existir. Rodar 1x na
instalação, antes da primeira rodada do skill.

Status possíveis (ver SKILL.md pra critério completo de cada um): Ghost 1,
Ghost 2, Esperar, FUP, Responder, Convertida, Novo, Verificar.
"""
from sheets_client import get_service
import config

HEADERS = [
    "Nome", "Telefone", "Data 1ª mensagem", "Data última mensagem",
    "Quem mandou por último", "Status", "Observação", "Trecho última mensagem",
]


def ensure_tab(service):
    meta = service.spreadsheets().get(spreadsheetId=config.SHEET_ID).execute()
    titles = [s["properties"]["title"] for s in meta["sheets"]]
    if config.FUP_TAB in titles:
        return False
    service.spreadsheets().batchUpdate(
        spreadsheetId=config.SHEET_ID,
        body={"requests": [{"addSheet": {"properties": {"title": config.FUP_TAB}}}]},
    ).execute()
    return True


def write():
    service = get_service()
    criada = ensure_tab(service)
    service.spreadsheets().values().update(
        spreadsheetId=config.SHEET_ID, range=f"{config.FUP_TAB}!A1",
        valueInputOption="RAW", body={"values": [HEADERS]},
    ).execute()
    print(f"Aba '{config.FUP_TAB}' {'criada' if criada else 'já existia'}, cabeçalho garantido.")


if __name__ == "__main__":
    write()
