"""Escreve atualizações na aba FUP depois que o agente abriu as conversas
mudadas/novas e decidiu o novo Status. Sempre revisar em dry-run (print)
antes de chamar contra dados reais.

updates: lista de dicts, cada um pode ter (todas opcionais menos 'nome'):
  nome, telefone, data_primeira, data_ultima, quem_mandou, status, observacao, trecho
Linha existente (casada por Nome): só sobrescreve os campos passados.
Linha nova (Nome não existe ainda): precisa nome, telefone, data_primeira,
  data_ultima, quem_mandou, status, trecho; observacao é opcional.

CRÍTICO -- toda coluna é resolvida por NOME de cabeçalho, lido ao vivo,
nunca hardcoded como letra fixa. Se você reordenar coluna na aba FUP depois
de instalar este skill, um mapa de letra fixa (tipo `{"nome": "A", ...}`)
fica errado silenciosamente -- escreve valor na coluna errada sem erro
nenhum até alguém notar o dado torto. Resolver por nome elimina essa
classe inteira de bug.
"""
from sheets_client import get_service, get_all_rows, col_letter
import config

# nome-de-campo (usado pelo chamador) -> nome REAL do cabeçalho na Sheet.
FIELD_TO_HEADER = {
    "nome": "Nome",
    "telefone": "Telefone",
    "data_primeira": "Data 1ª mensagem",
    "data_ultima": "Data última mensagem",
    "quem_mandou": "Quem mandou por último",
    "status": "Status",
    "observacao": "Observação",
    "trecho": "Trecho última mensagem",
}


def get_row_by_nome(service, idx):
    col_nome = col_letter(idx["Nome"])
    result = service.spreadsheets().values().get(
        spreadsheetId=config.SHEET_ID, range=f"{config.FUP_TAB}!{col_nome}1:{col_nome}"
    ).execute()
    values = result.get("values", [])
    return {row[0]: i + 1 for i, row in enumerate(values) if row}


def apply_updates(updates):
    service = get_service()
    headers, _ = get_all_rows(config.FUP_TAB)
    idx = {h: i for i, h in enumerate(headers)}
    n_cols = len(headers)
    by_nome = get_row_by_nome(service, idx)
    batch, appends = [], []

    for u in updates:
        nome = u["nome"]
        if nome in by_nome:
            row_num = by_nome[nome]
            for field, value in u.items():
                if field == "nome":
                    continue
                header = FIELD_TO_HEADER[field]
                col = col_letter(idx[header])
                batch.append({"range": f"{config.FUP_TAB}!{col}{row_num}", "values": [[value]]})
        else:
            row = [""] * n_cols
            for field, header in FIELD_TO_HEADER.items():
                row[idx[header]] = u.get(field, "")
            appends.append(row)

    if batch:
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=config.SHEET_ID, body={"valueInputOption": "RAW", "data": batch}
        ).execute()
    if appends:
        service.spreadsheets().values().append(
            spreadsheetId=config.SHEET_ID, range=f"{config.FUP_TAB}!A1",
            valueInputOption="RAW", insertDataOption="INSERT_ROWS",
            body={"values": appends},
        ).execute()

    print(f"{len(batch)} célula(s) atualizada(s) em linha existente, {len(appends)} linha(s) nova(s) criada(s).")
