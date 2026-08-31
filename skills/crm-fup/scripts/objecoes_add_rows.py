"""Adiciona linhas reais à aba Objeções. Sempre revisar em dry-run (print)
antes de chamar contra dado real -- ver SKILL.md, passo "Dry-run antes de
escrever".

rows: lista de dicts, cada um com as chaves (todas nomeadas, "numero" e
"data" obrigatórios):
  numero, data, canal, objecao, categoria, tema, nome, id, contexto,
  frase_literal, resposta_dada, superada, observacao
"Superada" default vazio/"Não sei" -- só usar "Sim" com confirmação
explícita de que o lead seguiu em frente depois da resposta dada (texto
da pessoa, ou campo já confirmado noutra fonte). "Não" só quando há
confirmação explícita de que ela NÃO seguiu em frente (ex: disse "não é
o momento"), nunca por ausência de resposta -- nesse caso "Não sei" é o
valor correto.
"""
from sheets_client import get_service
import config

FIELD_TO_HEADER = {
    "numero": "#",
    "data": "Data",
    "canal": "Canal",
    "objecao": "Objeção",
    "categoria": "Categoria",
    "tema": "Tema",
    "nome": "Nome",
    "id": "Id",
    "contexto": "Contexto",
    "frase_literal": "Frase literal",
    "resposta_dada": "Resposta dada",
    "superada": "Superada?",
    "observacao": "Observação",
}


def add_rows(rows):
    service = get_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=config.SHEET_ID, range=f"{config.OBJECOES_TAB}!A1:AZ1"
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
        spreadsheetId=config.SHEET_ID, range=f"{config.OBJECOES_TAB}!A1",
        valueInputOption="RAW", insertDataOption="INSERT_ROWS",
        body={"values": sheet_rows},
    ).execute()
    print(f"{len(sheet_rows)} linha(s) adicionada(s) em '{config.OBJECOES_TAB}'.")
