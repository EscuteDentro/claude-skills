"""Compara o que JÁ ESTÁ gravado na planilha com a numeração esperada de
'Duplicado' (lógica em plan_duplicado.compute_expected_groups -- única
implementação, nunca reimplementar aqui). Só leitura -- serve pra pente-fino
de auditoria a qualquer momento, sem risco nenhum de escrita.
"""
from sheets_client import get_all_rows
from plan_duplicado import compute_expected_groups


def main():
    headers, rows = get_all_rows()
    idx = {h: i for i, h in enumerate(headers)}
    expected = compute_expected_groups(headers, rows)

    mismatches = 0
    for i, e in expected.items():
        if e["expected_dup"] != e["actual_dup"]:
            mismatches += 1
            nome = (rows[i] + [""] * (len(headers) - len(rows[i])))[idx["Nome"]]
            print(f"Linha {i+2} ({nome}): esperado='{e['expected_dup']}' atual='{e['actual_dup']}'")

    print(f"\nTotal de linhas em grupo de duplicata: {len(expected)}")
    print(f"Divergências lógica-vs-planilha: {mismatches}")


if __name__ == "__main__":
    main()
