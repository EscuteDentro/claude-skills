"""Escreve de fato o que plan_duplicado.py reportou. So mexe em celulas que
estao vazias ou com valor invalido -- nunca sobrescreve valor ja numerado
corretamente (1/2*/3...). Rodar plan_duplicado.py e mostrar o plano pro
usuário ANTES de rodar isto -- nunca escrever sem confirmação explícita.

Coluna resolvida por NOME de cabeçalho (nunca posição fixa tipo "F"/"R") --
reordenar colunas na Sheet nunca quebra isto.
"""
from sheets_client import get_all_rows, update_cell
from plan_duplicado import compute_plan


def col_letter(index0based):
    """0 -> A, 1 -> B, ..., 25 -> Z, 26 -> AA..."""
    n = index0based + 1
    letters = ""
    while n:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def main():
    headers, _ = get_all_rows()
    idx = {h: i for i, h in enumerate(headers)}
    col_dup = col_letter(idx["Duplicado"])
    col_obs = col_letter(idx["Obs Duplicação"])

    plan = compute_plan()
    if not plan:
        print("Nada pra escrever.")
        return
    for item in plan:
        update_cell(f"{col_dup}{item['row_num']}", item["expected_dup"])
        if item["expected_obs"]:
            update_cell(f"{col_obs}{item['row_num']}", item["expected_obs"])
        print(f"linha {item['row_num']} ({item['nome']}) atualizada.")
    print(f"\nTotal: {len(plan)} linha(s) atualizadas.")


if __name__ == "__main__":
    main()
