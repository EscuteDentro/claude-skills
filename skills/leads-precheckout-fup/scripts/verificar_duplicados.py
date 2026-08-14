"""Pente-fino de integridade: encontra linhas que compartilham e-mail ou telefone
com outra linha mas NÃO têm número na coluna Duplicado (indicaria duplicata
não marcada). Também detecta o caso inverso: célula "Duplicado" preenchida
sem par correspondente (marcação órfã). Somente leitura, não escreve nada --
rode sempre antes de plan_duplicado.py/execute_duplicado.py.
"""
from collections import defaultdict
from sheets_client import get_all_rows


def pad(row, length):
    return row + [""] * (length - len(row))


def main():
    headers, rows = get_all_rows()
    idx = {h: i for i, h in enumerate(headers)}
    rows = [pad(r, len(headers)) for r in rows]

    by_email = defaultdict(list)
    by_phone = defaultdict(list)
    for i, r in enumerate(rows, start=2):
        email = r[idx["E-mail"]].strip().lower()
        phone = r[idx["Telefone"]].strip()
        if email:
            by_email[email].append(i)
        if phone:
            by_phone[phone].append(i)

    problem_rows = set()
    for email, line_nums in by_email.items():
        if len(line_nums) > 1:
            problem_rows.update(line_nums)
    for phone, line_nums in by_phone.items():
        if len(line_nums) > 1:
            problem_rows.update(line_nums)

    missing_flag = []
    for line_num in sorted(problem_rows):
        r = rows[line_num - 2]
        dup_col = r[idx["Duplicado"]].strip()
        if not dup_col:
            missing_flag.append((line_num, r[idx["Nome"]], r[idx["E-mail"]], r[idx["Telefone"]]))

    print(f"Linhas com e-mail/telefone repetido: {len(problem_rows)}")
    print(f"Linhas SEM número em 'Duplicado' apesar de repetidas: {len(missing_flag)}")
    for line_num, nome, email, phone in missing_flag:
        print(f"  Linha {line_num}: {nome} | {email} | {phone}")

    # checagem reversa: linha tem número em Duplicado mas não achou par (grupo órfão)
    orphans = []
    for i, r in enumerate(rows, start=2):
        dup_col = r[idx["Duplicado"]].strip()
        if dup_col and i not in problem_rows:
            orphans.append((i, r[idx["Nome"]], r[idx["E-mail"]], r[idx["Telefone"]]))
    print(f"Linhas com 'Duplicado' preenchido mas sem par correspondente: {len(orphans)}")
    for line_num, nome, email, phone in orphans:
        print(f"  Linha {line_num}: {nome} | {email} | {phone}")


if __name__ == "__main__":
    main()
