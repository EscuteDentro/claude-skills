"""Ferramenta de CRM (status + semáforo visual).

Formatação condicional de linha inteira, 3 regras em ordem de prioridade
(Sheets aplica só a 1ª regra que bate, nunca soma -- por isso a ordem
importa):
1) COMPROU = "Sim" -> linha inteira verde claro (prioridade máxima: virou
   cliente, isso é mais relevante que qualquer outro sinal -- contato
   pós-compra costuma ter base legal própria, execução de contrato,
   independente do consentimento de WhatsApp pré-checkout. Confirme a
   base legal aplicável ao seu caso antes de assumir isso como regra).
2) Consentiu WA = "Não" -> linha inteira cinza claro (nunca contatar via
   WhatsApp quem não consentiu -- só perde pra COMPROU=Sim acima).
3) Status CRM vazio E Nome preenchido -> só a célula dessa coluna fica
   vermelha (sinal visual "precisa contatar"). O "E Nome preenchido" evita
   pintar linha vazia sem dado nenhum -- a condição sozinha "Status CRM
   vazio" também é verdadeira pra linha em branco, pintando de vermelho
   até o final do range sem necessidade.

Requer as colunas "Status CRM", "COMPROU", "Consentiu WA" e "Nome" na aba
(nomes exatos -- resolvidos por cabeçalho E consultados via metadata da
própria Sheet, nunca hardcoded, então funciona em qualquer ordem/tamanho
de coluna).

CRÍTICO -- locale da Sheet: fórmula CUSTOM_FORMULA com múltiplos argumentos
(AND, OR, SUM...) precisa usar o separador do LOCALE da planilha -- em
pt_BR é `;`, não `,`. A API rejeita com "Invalid ConditionValue.userEnteredValue"
se usar o separador errado pro locale. Verifique o locale da sua Sheet
(`spreadsheets().get().execute()['properties']['locale']`) antes de usar
fórmula com mais de 1 argumento. Comparação simples (`=A2="Sim"`) não tem
separador, então não é afetada.
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


def get_locale_separator(service):
    """AND()/OR() etc. usam ';' em locales que usam ',' como separador
    decimal (ex: pt_BR, de_DE), e ',' em locales que usam '.' (ex: en_US).
    Heurística simples: locales latinos/europeus usam ';'."""
    meta = service.spreadsheets().get(spreadsheetId=config.SHEET_ID, fields="properties.locale").execute()
    locale = meta.get("properties", {}).get("locale", "en_US")
    return ";" if locale.split("_")[0] in ("pt", "de", "es", "fr", "it", "nl", "pl", "ru") else ","


def main():
    service = get_service()
    headers, _ = get_all_rows()
    idx = {h: i for i, h in enumerate(headers)}
    gid = get_tab_gid(service, config.SHEET_TAB)
    n_cols = len(headers)
    sep = get_locale_separator(service)

    col_nome = col_letter(idx["Nome"])
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
                            "values": [{"userEnteredValue": f'=${col_comprou}2="Sim"'}],
                        },
                        "format": {"backgroundColor": green},
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
                            "values": [{"userEnteredValue": f'=${col_consentiu}2="Não"'}],
                        },
                        "format": {"backgroundColor": gray},
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
                            "values": [{"userEnteredValue": f'=AND(${col_status_crm}2=""{sep}${col_nome}2<>"")'}],
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
