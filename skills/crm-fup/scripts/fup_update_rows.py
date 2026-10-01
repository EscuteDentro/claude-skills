"""Escreve atualizações na aba FUP depois que o agente abriu as conversas
mudadas/novas e decidiu o novo Status. Sempre revisar em dry-run (print)
antes de chamar contra dados reais.

updates: lista de dicts, cada um pode ter (todas opcionais menos 'nome'):
  nome, telefone, data_primeira, data_ultima, quem_mandou, status, observacao, trecho
Linha existente: casada por Telefone na forma canônica (com e sem o 9 extra
  é a mesma linha) sempre que `telefone` vier no update; cai pra Nome só se
  não vier. Sempre passar `telefone`. `nome` é escrito também em linha
  existente: contato renomeado precisa refletir na FUP.
Linha nova (nenhuma linha bate por telefone nem nome): precisa nome, telefone,
  data_primeira, data_ultima, quem_mandou, status, trecho; observacao é opcional.

CRÍTICO -- toda coluna é resolvida por NOME de cabeçalho, lido ao vivo,
nunca hardcoded como letra fixa. Se você reordenar coluna na aba FUP depois
de instalar este skill, um mapa de letra fixa (tipo `{"nome": "A", ...}`)
fica errado silenciosamente -- escreve valor na coluna errada sem erro
nenhum até alguém notar o dado torto. Resolver por nome elimina essa
classe inteira de bug.
"""
import json
import sys

from sheets_client import get_service, get_all_rows, col_letter
from captura import trecho_por_nome
from identidade import canon_tel
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


def get_row_index(service, idx, header):
    col = col_letter(idx[header])
    result = service.spreadsheets().values().get(
        spreadsheetId=config.SHEET_ID, range=f"{config.FUP_TAB}!{col}1:{col}"
    ).execute()
    values = result.get("values", [])
    return {row[0]: i + 1 for i, row in enumerate(values) if row}


def apply_updates(updates, captura_path=None):
    """`captura_path` (captura_AAAA-MM-DD.json da rodada): o trecho gravado
    passa a ser o texto literal que a lista de conversas exibiu, por cima do
    que veio no update. É contra esse texto que o próximo diff compara; trecho
    resumido ou com reticências à mão vira falso "mudou" pra sempre. Passar
    sempre que a rodada tiver captura."""
    service = get_service()
    headers, _ = get_all_rows(config.FUP_TAB)
    idx = {h: i for i, h in enumerate(headers)}
    n_cols = len(headers)
    # Telefone casado pela forma canônica: a mesma pessoa com e sem o 9 extra
    # é uma linha só (casar pela string crua duplica linha na FUP).
    by_tel = {canon_tel(t): n for t, n in get_row_index(service, idx, "Telefone").items()}
    by_nome = get_row_index(service, idx, "Nome")
    batch, appends = [], []
    literal = trecho_por_nome(captura_path) if captura_path else {}

    for u in updates:
        if u.get("nome") in literal and u.get("trecho") != literal[u["nome"]]:
            u = {**u, "trecho": literal[u["nome"]]}
        tel = u.get("telefone")
        row_num = by_tel.get(canon_tel(tel)) if tel else None
        if row_num is None:
            row_num = by_nome.get(u["nome"])
        if row_num is not None:
            for field, value in u.items():
                if field == "telefone":
                    continue  # chave de casamento: a forma já gravada na linha fica
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


def alinhar_nomes(diff_path):
    """Grava na FUP o nome que a conversa exibe, pras linhas que o fup_diff
    casou pela chave mas com Nome diferente (`nomes_divergentes`)."""
    with open(diff_path) as f:
        divergentes = json.load(f).get("nomes_divergentes", [])
    ups = [{"nome": d["nome_captura"], "telefone": d["telefone"]} for d in divergentes if d.get("telefone")]
    if not ups:
        print("Nenhum nome pra alinhar.")
        return
    for u in ups:
        print(f"  {u['telefone']}: -> {u['nome']}")
    apply_updates(ups)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--alinhar-nomes":
        alinhar_nomes(sys.argv[2])
    else:
        print("Uso: python3 fup_update_rows.py --alinhar-nomes diff_resultado.json")
