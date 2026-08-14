"""Dry-run da ferramenta "salvar contatos no Google": cruza a planilha
(grupos de duplicata, elegibilidade) com os contatos já existentes
(identificados por config.CONTATO_MARCADOR), e monta o plano de ações
(renomear existentes, criar novos) sem executar nada.
"""
import re
from collections import defaultdict
from datetime import datetime

from sheets_client import get_all_rows
from contacts_client import list_lead_contacts
import config

SUFFIX = config.CONTATO_MARCADOR


def pad(row, length):
    return row + [""] * (length - len(row))


def norm_phone(raw):
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("55") and len(digits) > 11:
        digits = digits[2:]
    return digits[-11:] if len(digits) >= 11 else digits


def month_year(ts):
    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ")
    return f"{dt.month:02d}.{dt.year % 100:02d}"


def first_name(nome):
    return nome.strip().split()[0] if nome.strip() else ""


STOPWORDS = {"da", "de", "do", "das", "dos", "e"}


def disambiguate(lead):
    """Nome + sobrenome se houver (pulando conectivos 'da/de/do'); senão
    infere um segundo nome a partir do e-mail (parte local, best-effort)."""
    parts = lead["nome"].strip().split()
    if len(parts) > 1:
        resto = [p for p in parts[1:] if p.lower() not in STOPWORDS]
        if resto:
            return f"{parts[0]} {resto[0]}"
    email_local = lead["email"].split("@")[0]
    cleaned = re.sub(r"[^a-zA-ZÀ-ÿ]", " ", email_local).split()
    guess = cleaned[1].capitalize() if len(cleaned) > 1 else ""
    return f"{parts[0]} {guess}".strip()


def build_groups():
    headers, rows = get_all_rows()
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

    leads = []
    for root, members in groups.items():
        members.sort(key=lambda i: rows[i][idx["Timestamp"]])
        canonical_i = members[-1]  # mais recente
        canonical = rows[canonical_i]
        comprou = canonical[idx["COMPROU"]].strip()
        consentiu = canonical[idx["Consentiu WA"]].strip()
        elegivel = comprou != "Sim" and consentiu != "Não"
        leads.append({
            "row_num": canonical_i + 2,
            "nome": canonical[idx["Nome"]].strip(),
            "telefone": canonical[idx["Telefone"]].strip(),
            "email": canonical[idx["E-mail"]].strip(),
            "duplicado": len(members) > 1,
            "mmaa": month_year(canonical[idx["Timestamp"]]),
            "elegivel": elegivel,
            "status_crm": canonical[idx["Status CRM"]].strip(),
        })
    return leads


def main():
    leads = build_groups()
    contacts = list_lead_contacts()
    contacts_by_phone = {norm_phone(p): c for c in contacts for p in c["phones"]}

    print(f"Leads elegíveis (canônicos): {sum(1 for l in leads if l['elegivel'])}")
    print(f"Contatos existentes '{SUFFIX}': {len(contacts)}")
    print()

    plan, not_eligible_but_has_contact = [], []

    for lead in leads:
        phone_key = norm_phone(lead["telefone"])
        contact = contacts_by_phone.get(phone_key)
        suffix = lead["mmaa"] + ("+" if lead["duplicado"] else "")

        if not lead["elegivel"]:
            if contact:
                not_eligible_but_has_contact.append((lead, contact))
            continue

        base_name = contact["name"].replace(f" {SUFFIX}", "").strip() if contact else first_name(lead["nome"])
        plan.append({"lead": lead, "contact": contact, "base_name": base_name, "suffix": suffix})

    # detecta colisão de base_name entre leads DIFERENTES (telefone diferente)
    by_base = defaultdict(list)
    for item in plan:
        by_base[item["base_name"]].append(item)
    for base_name, items in by_base.items():
        if len(items) > 1:
            for item in items:
                new_base = disambiguate(item["lead"])
                print(f"COLISÃO de nome '{base_name}' — linha {item['lead']['row_num']} ({item['lead']['nome']}) desambiguado para '{new_base}'")
                item["base_name"] = new_base

    to_rename, to_create, already_ok = [], [], []
    for item in plan:
        expected_name = f"{item['base_name']} {SUFFIX} {item['suffix']}"
        if item["contact"]:
            if item["contact"]["name"] != expected_name:
                to_rename.append((item["lead"], item["contact"], expected_name))
            else:
                already_ok.append((item["lead"], item["contact"]))
        else:
            to_create.append((item["lead"], expected_name))

    print(f"\n=== RENOMEAR ({len(to_rename)}) ===")
    for lead, contact, expected in to_rename:
        print(f"  linha {lead['row_num']}: '{contact['name']}' -> '{expected}'")

    print(f"\n=== CRIAR ({len(to_create)}) ===")
    for lead, expected in to_create:
        print(f"  linha {lead['row_num']}: {lead['nome']} | tel={lead['telefone']} | nome final: '{expected}' | status_crm atual={lead['status_crm']!r}")

    print(f"\n=== JÁ OK ({len(already_ok)}) ===")
    for lead, contact in already_ok:
        print(f"  {contact['name']}")

    if not_eligible_but_has_contact:
        print(f"\n=== ATENÇÃO: tem contato mas NÃO é elegível (Comprou=Sim ou Consentiu=Não) ({len(not_eligible_but_has_contact)}) ===")
        for lead, contact in not_eligible_but_has_contact:
            print(f"  linha {lead['row_num']}: {contact['name']}")


if __name__ == "__main__":
    main()
