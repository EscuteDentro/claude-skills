"""Dropdown Sim/Não com rejeição de valor inválido, nas colunas COMPROU e
Consentiu WA. Célula vazia não é bloqueada -- só valor não-vazio fora da
lista. Antes de aplicar, confirme que o Apps Script (doPost) só grava
'Sim'/'Não' exatos nessas colunas (nunca outro valor), senão a validação
passa a rejeitar gravações legítimas.
"""
from sheets_client import get_service, get_all_rows
import config

TETO_LINHAS = 10000  # folga generosa -- ajuste se sua base crescer além disso


def get_tab_gid(service, tab_name):
    meta = service.spreadsheets().get(spreadsheetId=config.SHEET_ID).execute()
    return next(s["properties"]["sheetId"] for s in meta["sheets"]
                if s["properties"]["title"] == tab_name)


def col_validation_request(gid, col_index_0based):
    return {
        "setDataValidation": {
            "range": {
                "sheetId": gid,
                "startRowIndex": 1,
                "endRowIndex": TETO_LINHAS,
                "startColumnIndex": col_index_0based,
                "endColumnIndex": col_index_0based + 1,
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": "Sim"}, {"userEnteredValue": "Não"}],
                },
                "strict": True,
                "showCustomUi": True,
            },
        }
    }


def main():
    service = get_service()
    headers, _ = get_all_rows()
    idx = {h: i for i, h in enumerate(headers)}
    gid = get_tab_gid(service, config.SHEET_TAB)

    requests = [
        col_validation_request(gid, idx["COMPROU"]),
        col_validation_request(gid, idx["Consentiu WA"]),
    ]
    service.spreadsheets().batchUpdate(
        spreadsheetId=config.SHEET_ID, body={"requests": requests}
    ).execute()
    print("Validação aplicada em COMPROU e Consentiu WA.")


if __name__ == "__main__":
    main()
