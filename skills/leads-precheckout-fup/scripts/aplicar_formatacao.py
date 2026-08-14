"""Ferramenta de CRM (status + semáforo visual).

Formatação condicional de linha inteira, 3 regras em ordem de prioridade
(Sheets aplica só a 1ª regra que bate, nunca soma -- por isso a ordem
importa):
1) Consentiu WA = "Não" -> linha inteira cinza claro (prioridade máxima:
   nunca sinaliza "precisa contatar" quem não pode ser contatado).
2) COMPROU = "Sim" -> linha inteira verde claro.
3) Status CRM vazio -> só a célula dessa coluna fica vermelha (sinal visual
   "precisa contatar"). Por estar em 3º lugar, só aparece quando as regras
   1-2 não capturaram a linha.

Requer as colunas "Status CRM", "COMPROU" e "Consentiu WA" na aba (nomes
exatos -- resolvidos por cabeçalho E consultados via metadata da própria
Sheet, nunca hardcoded, entao funciona em qualquer ordem/tamanho de coluna).
"""
from sheets_client import get_service, get_all_rows
import config


def col_letter(index0based):
    n = index0based + 1
    letters = ""
    while n:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def get_tab_gid(service, tab_name):
    meta = service.spreadsheets().get(spreadsheetId=config.SHEET_ID).execute()
    return next(s["properties"]["sheetId"] for s in meta["sheets"]
                if s["properties"]["title"] == tab_name)


def main():
    service = get_service()
    headers, _ = get_all_rows()
    idx = {h: i for i, h in enumerate(headers)}
    gid = get_tab_gid(service, config.SHEET_TAB)
    n_cols = len(headers)

    col_status_crm = col_letter(idx["Status CRM"])
    col_comprou = col_letter(idx["COMPROU"])
    col_consentiu = col_letter(idx["Consentiu WA"])

    gray = {"red": 0.93, "green": 0.93, "blue": 0.93}
    green = {"red": 0.85, "green": 0.91, "blue": 0.83}
    red = {"red": 0.92, "green": 0.60, "blue": 0.60}

    requests = [
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": gid, "startRowIndex": 1,
                        "startColumnIndex": 0, "endColumnIndex": n_cols,
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [{"userEnteredValue": f'=${col_consentiu}2="Não"'}],
                        },
                        "format": {"backgroundColor": gray},
                    },
                },
                "index": 0,
            }
        },
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": gid, "startRowIndex": 1,
                        "startColumnIndex": 0, "endColumnIndex": n_cols,
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [{"userEnteredValue": f'=${col_comprou}2="Sim"'}],
                        },
                        "format": {"backgroundColor": green},
                    },
                },
                "index": 1,
            }
        },
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": gid, "startRowIndex": 1,
                        "startColumnIndex": idx["Status CRM"],
                        "endColumnIndex": idx["Status CRM"] + 1,
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [{"userEnteredValue": f'={col_status_crm}2=""'}],
                        },
                        "format": {"backgroundColor": red},
                    },
                },
                "index": 2,
            }
        },
    ]

    service.spreadsheets().batchUpdate(
        spreadsheetId=config.SHEET_ID, body={"requests": requests}
    ).execute()
    print("Regras de formatação condicional aplicadas.")
    print("Atenção: se a aba já tiver regras de formatação condicional de uma "
          "tentativa anterior, apague-as manualmente antes (Formatar > "
          "Formatação condicional na UI do Sheets) -- este script só adiciona, "
          "nunca remove regra existente.")


if __name__ == "__main__":
    main()
