"""Escreve de fato o que plan_status_crm.py propôs -- "Ver linha N" nas
linhas do grupo que não são a âncora de contato. Escreve TODAS as linhas do
plano, inclusive as com ⚠️ (intervalo grande) -- por padrão o contato
antigo continua valendo; a ⚠️ é só aviso pra decidir se vale reabordar,
nunca bloqueia a escrita. Rodar plan_status_crm.py e mostrar pro usuário
ANTES -- nunca escrever sem confirmação.
"""
from sheets_client import get_all_rows, batch_update_cells
from plan_status_crm import compute_plan


def col_letter(index0based):
    n = index0based + 1
    letters = ""
    while n:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def main():
    plan, anomalias = compute_plan()
    if not plan:
        print("Nada pra escrever.")
    else:
        headers, _ = get_all_rows()
        idx = {h: i for i, h in enumerate(headers)}
        col_status_crm = col_letter(idx["Status CRM"])
        updates = [(f"{col_status_crm}{item['row_num']}", item["esperado"]) for item in plan]
        batch_update_cells(updates)
        for item in plan:
            print(f"linha {item['row_num']} ({item['nome']}) atualizada -> '{item['esperado']}'")
        print(f"\nTotal: {len(plan)} linha(s) atualizadas.")

    if anomalias:
        print(f"\n=== ANOMALIAS não resolvidas automaticamente ({len(anomalias)}) ===")
        for a in anomalias:
            print(f"  {a}")


if __name__ == "__main__":
    main()
