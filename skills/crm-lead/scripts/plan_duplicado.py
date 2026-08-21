"""Ferramenta de sinalização de duplicação.

Fonte única da lógica de agrupamento/numeração (union-find por e-mail OU
telefone, ordem cronológica pelo Timestamp, "*" quando telefone OU e-mail
diverge da 1ª entrada do grupo) -- importada por validar_logica_numeracao.py
(leitura) pra nunca ter 2 implementações divergindo.

Uso como dry-run (`python3 plan_duplicado.py`): recomputa Duplicado + Obs
Duplicacao pra TODAS as linhas e mostra as que tem a coluna Duplicado vazia
(duplicata nova ainda nao marcada) OU um valor que nao bate com a convencao
numerada 1/2*/3... Nunca mexe em valor ja numerado corretamente. Nunca
escreve nada -- e execute_duplicado.py quem escreve, e so depois de
confirmacao explicita.

Requer as colunas "Timestamp", "Nome", "E-mail", "Telefone", "Duplicado" e
"Obs Duplicação" na aba (nomes exatos -- resolvidos por cabeçalho, nunca por
posição, entao reordenar colunas na Sheet nunca quebra isso).
"""
import re
from collections import defaultdict
from sheets_client import get_all_rows

DUP_PATTERN = re.compile(r"^\d+\*?$")


def pad(row, length):
    return row + [""] * (length - len(row))


def build_duplicate_groups(headers, rows):
    """Union-find por e-mail OU telefone. Retorna {root_index: [member_indices]}
    só pra grupos com >=2 membros (linhas padded, mesmo índice 0-based que
    `rows`). Fonte única do agrupamento -- plan_status_crm.py importa isto
    diretamente em vez de reimplementar, nunca duplicar essa lógica.
    """
    idx = {h: i for i, h in enumerate(headers)}
    rows = [pad(r, len(headers)) for r in rows]
    n = len(rows)

    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    by_email, by_phone = defaultdict(list), defaultdict(list)
    for i, r in enumerate(rows):
        email = r[idx["E-mail"]].strip().lower()
        phone = r[idx["Telefone"]].strip()
        if email:
            by_email[email].append(i)
        if phone:
            by_phone[phone].append(i)
    for group in list(by_email.values()) + list(by_phone.values()):
        for j in group[1:]:
            union(group[0], j)

    groups = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(i)

    return {root: members for root, members in groups.items() if len(members) >= 2}


def compute_expected_groups(headers, rows):
    """Retorna {row_index_0based: {"expected_dup", "expected_obs", "actual_dup"}}
    só pra linhas que pertencem a um grupo de duplicata (>=2 membros).
    """
    idx = {h: i for i, h in enumerate(headers)}
    rows = [pad(r, len(headers)) for r in rows]
    groups = build_duplicate_groups(headers, rows)

    result = {}
    for root, members in groups.items():
        members = list(members)
        members.sort(key=lambda i: rows[i][idx["Timestamp"]])
        first_phone = rows[members[0]][idx["Telefone"]].strip()
        first_email = rows[members[0]][idx["E-mail"]].strip().lower()
        for order, i in enumerate(members, start=1):
            r = rows[i]
            phone = r[idx["Telefone"]].strip()
            email = r[idx["E-mail"]].strip().lower()
            phone_diverge = phone != first_phone and order > 1
            email_diverge = email != first_email and order > 1
            diverge = phone_diverge or email_diverge
            expected_dup = str(order) + ("*" if diverge else "")
            obs_parts = []
            if phone_diverge:
                obs_parts.append(f"Telefone diverge da 1ª entrada ({first_phone})")
            if email_diverge:
                obs_parts.append(f"E-mail diverge da 1ª entrada ({first_email})")
            result[i] = {
                "expected_dup": expected_dup,
                "expected_obs": " | ".join(obs_parts),
                "actual_dup": r[idx["Duplicado"]].strip(),
            }
    return result


def compute_plan():
    headers, rows = get_all_rows()
    idx = {h: i for i, h in enumerate(headers)}
    expected = compute_expected_groups(headers, rows)

    plan = []
    for i, r in enumerate(rows):
        r = pad(r, len(headers))
        if i not in expected:
            continue
        e = expected[i]
        actual_dup = e["actual_dup"]
        if not actual_dup or not DUP_PATTERN.match(actual_dup):
            plan.append({
                "row_num": i + 2,
                "nome": r[idx["Nome"]],
                "expected_dup": e["expected_dup"],
                "expected_obs": e["expected_obs"],
                "motivo": "vazia" if not actual_dup else f"valor inválido ('{actual_dup}')",
            })
    return plan


def main():
    plan = compute_plan()
    print(f"Linhas de duplicata sem marcação correta: {len(plan)}")
    for item in plan:
        print(f"  linha {item['row_num']} ({item['nome']}) [{item['motivo']}]: Duplicado='{item['expected_dup']}'"
              + (f" | Obs Duplicação='{item['expected_obs']}'" if item['expected_obs'] else ""))


if __name__ == "__main__":
    main()
