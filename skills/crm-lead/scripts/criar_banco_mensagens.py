"""Cria a aba "Banco de Mensagens" -- biblioteca pequena e reutilizável de
templates, NUNCA um log de tudo que foi enviado. Fonte única de verdade:
tanto este skill (Python) quanto o Apps Script (e-mail diário) leem essa
aba em tempo real -- nunca hardcode o texto real em nenhum dos dois lados,
sempre edite só aqui.

Este script cria a ESTRUTURA com 3 linhas de exemplo vazias -- preencha o
texto de "Texto" com suas próprias mensagens reais (nunca use texto de
outro produto/marca como placeholder). "Canal" precisa ser exatamente
"WhatsApp" ou "E-mail" -- é isso que gerar_link_whatsapp.py usa pra
escolher o template certo.
"""
from sheets_client import get_service
import config

TEMPLATES_EXEMPLO = [
    ["WhatsApp - lead quente (<5 dias)", "WhatsApp", "",
     "[Escreva aqui a mensagem pra quem se cadastrou há menos de 5 dias. Use [Nome] "
     "onde o primeiro nome do lead deve entrar.]",
     "Substituir [Nome] pelo primeiro nome, só 1ª letra maiúscula."],
    ["WhatsApp - lead frio (>=5 dias)", "WhatsApp", "",
     "[Escreva aqui a mensagem pra quem se cadastrou há 5 dias ou mais -- geralmente "
     "reconhecendo que já faz um tempo, sem soar como cobrança.]",
     "Substituir [Nome]. Lead capturado há 5 dias ou mais."],
    ["E-mail - lead sem WhatsApp", "E-mail", "[Assunto do e-mail]",
     "[Escreva aqui o e-mail pra quem não tem WhatsApp confirmado -- geralmente mais "
     "longo que a mensagem de WhatsApp, já que é o único canal disponível.]",
     "Substituir [Nome]. Usado quando o número não está registrado no WhatsApp."],
]


def main():
    service = get_service()

    meta = service.spreadsheets().get(
        spreadsheetId=config.SHEET_ID, fields="sheets(properties(sheetId,title))"
    ).execute()
    existing = {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta["sheets"]}

    if config.BANCO_MENSAGENS_TAB in existing:
        sheet_id = existing[config.BANCO_MENSAGENS_TAB]
        print(f'Aba "{config.BANCO_MENSAGENS_TAB}" já existe (sheetId={sheet_id}) -- '
              "nada será sobrescrito. Edite direto na Sheet se quiser mudar os templates.")
        return
    else:
        add_resp = service.spreadsheets().batchUpdate(spreadsheetId=config.SHEET_ID, body={"requests": [{
            "addSheet": {"properties": {"title": config.BANCO_MENSAGENS_TAB,
                                         "gridProperties": {"rowCount": 50, "columnCount": 5}}}
        }]}).execute()
        sheet_id = add_resp["replies"][0]["addSheet"]["properties"]["sheetId"]

    headers = ["Nome do template", "Canal", "Assunto (e-mail)", "Texto", "Observação"]

    service.spreadsheets().values().update(
        spreadsheetId=config.SHEET_ID,
        range=f"{config.BANCO_MENSAGENS_TAB}!A1",
        valueInputOption="RAW",
        body={"values": [headers] + TEMPLATES_EXEMPLO},
    ).execute()

    format_body = {
        "requests": [
            {
                "repeatCell": {
                    "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
                    "cell": {"userEnteredFormat": {
                        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}, "fontSize": 10},
                        "backgroundColor": {"red": 0.169, "green": 0.169, "blue": 0.169},
                    }},
                    "fields": "userEnteredFormat(textFormat,backgroundColor)",
                }
            },
            {"updateSheetProperties": {"properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}}, "fields": "gridProperties.frozenRowCount"}},
            {
                "repeatCell": {
                    "range": {"sheetId": sheet_id, "startRowIndex": 1, "endColumnIndex": 5},
                    "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP", "verticalAlignment": "TOP", "textFormat": {"fontSize": 10}}},
                    "fields": "userEnteredFormat(wrapStrategy,verticalAlignment,textFormat)",
                }
            },
            {"updateDimensionProperties": {"range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1}, "properties": {"pixelSize": 220}, "fields": "pixelSize"}},
            {"updateDimensionProperties": {"range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 90}, "fields": "pixelSize"}},
            {"updateDimensionProperties": {"range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 2, "endIndex": 3}, "properties": {"pixelSize": 220}, "fields": "pixelSize"}},
            {"updateDimensionProperties": {"range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 3, "endIndex": 4}, "properties": {"pixelSize": 420}, "fields": "pixelSize"}},
            {"updateDimensionProperties": {"range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 4, "endIndex": 5}, "properties": {"pixelSize": 280}, "fields": "pixelSize"}},
        ]
    }
    service.spreadsheets().batchUpdate(spreadsheetId=config.SHEET_ID, body=format_body).execute()
    print(f'Aba "{config.BANCO_MENSAGENS_TAB}" criada (sheetId={sheet_id}) com 3 templates '
          "de EXEMPLO vazios. Preencha a coluna Texto com suas mensagens reais antes de usar.")


if __name__ == "__main__":
    main()
