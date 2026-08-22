"""Compara uma captura fresca do WhatsApp (lida e parseada pelo agente,
não por regex aqui -- texto de busca do WhatsApp é irregular demais pra
parser determinístico: nomes com badge de avatar, tags de arquivada/não
lida intercaladas etc.) contra o estado gravado na aba FUP.

Uso: python3 fup_diff.py captura.json
Formato de captura.json: lista de {"nome": ..., "data": "YYYY-MM-DD", "trecho": ...}
`data` já deve vir como data absoluta (o agente resolve "Ontem"/"quarta-feira"
antes de escrever o arquivo, usando a data de hoje conhecida no momento da rodada).

Diff de 2 parâmetros: muda se DATA OU TRECHO mudou -- mensagem nova no
mesmo dia também conta, porque o trecho muda mesmo sem a data mudar.

Comparação de trecho é por PREFIXO comum (primeiros TRECHO_CMP_LEN chars),
nunca igualdade exata -- capturas de sessões diferentes podem truncar o
trecho em tamanhos diferentes, e comparação exata dá falso positivo de
"mudou" pra contato que na verdade está igual.
"""
import json
import sys
from pathlib import Path

from sheets_client import get_all_rows
import config

TRECHO_CMP_LEN = 40  # comparar só o prefixo -- robusto a truncamento diferente entre capturas


def get_fup_state():
    headers, rows = get_all_rows(config.FUP_TAB)
    idx = {h: i for i, h in enumerate(headers)}
    state = {}
    for row_num, r in enumerate(rows, start=2):
        def cell(col):
            i = idx.get(col)
            return r[i] if i is not None and len(r) > i else ""
        nome = cell("Nome")
        if nome:
            state[nome] = {
                "row": row_num,
                "data": cell("Data última mensagem"),
                "trecho": cell("Trecho última mensagem"),
            }
    return state


def diff(captura_path):
    state = get_fup_state()
    with open(captura_path) as f:
        captura = json.load(f)

    novos, mudados, sem_mudanca = [], [], []
    for item in captura:
        nome, data, trecho = item["nome"], item["data"], item["trecho"]
        if nome not in state:
            novos.append(item)
        else:
            atual = state[nome]
            trecho_mudou = atual["trecho"][:TRECHO_CMP_LEN] != trecho[:TRECHO_CMP_LEN]
            if atual["data"] != data or trecho_mudou:
                mudados.append({**item, "row": atual["row"], "data_anterior": atual["data"]})
            else:
                sem_mudanca.append(nome)

    print(f"{len(novos)} contato(s) novo(s) (nunca visto antes):")
    for n in novos:
        print(f"  + {n['nome']} | {n['data']} | {n['trecho'][:60]}")

    print(f"\n{len(mudados)} contato(s) com atividade nova desde a última rodada:")
    for m in mudados:
        print(f"  ~ {m['nome']} (linha {m['row']}) | era {m['data_anterior']}, agora {m['data']} | {m['trecho'][:60]}")

    print(f"\n{len(sem_mudanca)} sem mudança (não precisa abrir).")

    out = {"novos": novos, "mudados": mudados}
    Path("diff_resultado.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print("\nLista de quem precisa ser aberto salva em diff_resultado.json")
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 fup_diff.py captura.json")
        sys.exit(1)
    diff(sys.argv[1])
