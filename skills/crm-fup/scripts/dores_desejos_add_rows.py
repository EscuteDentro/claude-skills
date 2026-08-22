"""Adiciona linhas reais à aba Dores e Desejos. Sempre revisar em dry-run
(print) antes de chamar contra dado real -- ver SKILL.md, passo "Dry-run
antes de escrever".

rows: lista de dicts, cada um com as chaves (todas nomeadas, "#" e "data"
obrigatórios):
  numero, data, canal, dores_desejos, categoria, tema, nome, id, contexto,
  frase_literal, converteu, observacao
"Converteu" default vazio/"Não" -- só usar "Sim" com confirmação explícita
de compra (texto da pessoa, ou campo já confirmado noutra fonte). Nunca
inferir de contexto indireto (parcelamento discutido, uso contínuo etc.) --
um campo binário não carrega nuance, e "Sim" errado contamina qualquer
análise que agregar essa coluna depois.
"""
from sheets_client import get_service
import config

FIELD_TO_HEADER = {
    "numero": "#",
    "data": "Data",
    "canal": "Canal",
    "dores_desejos": "Dores e/ou Desejos",
    "categoria": "Categoria",
    "tema": "Tema",
    "nome": "Nome",
    "id": "Id",
    "contexto": "Contexto",
    "frase_literal": "Frase literal",
    "converteu": "Converteu?",
    "observacao": "Observação",
}


def add_rows(rows):
    service = get_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=config.SHEET_ID, range=f"{config.DORES_DESEJOS_TAB}!A1:AZ1"
    ).execute()
    headers = result.get("values", [[]])[0]
    idx = {h: i for i, h in enumerate(headers)}
    n_cols = len(headers)

    sheet_rows = []
    for r in rows:
        row = [""] * n_cols
        for field, header in FIELD_TO_HEADER.items():
            if header in idx and field in r:
                row[idx[header]] = r[field]
        sheet_rows.append(row)

    service.spreadsheets().values().append(
        spreadsheetId=config.SHEET_ID, range=f"{config.DORES_DESEJOS_TAB}!A1",
        valueInputOption="RAW", insertDataOption="INSERT_ROWS",
        body={"values": sheet_rows},
    ).execute()
    print(f"{len(sheet_rows)} linha(s) adicionada(s) em '{config.DORES_DESEJOS_TAB}'.")
