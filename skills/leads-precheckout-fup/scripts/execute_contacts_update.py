"""Executa de fato o plano gerado por plan_contacts_update.py: renomeia os
contatos existentes e cria os que faltam. Roda a mesma lógica de plano
(idêntica, sem duplicar) e só então grava via People API. Rode
plan_contacts_update.py e mostre o plano pro usuário ANTES -- nunca escrever
sem confirmação explícita.
"""
from contacts_client import get_service
from plan_contacts_update import build_groups, disambiguate, first_name, norm_phone, SUFFIX
from contacts_client import list_lead_contacts
from add_phone_variant import alt_format
from collections import defaultdict


def build_plan():
    leads = build_groups()
    contacts = list_lead_contacts()
    contacts_by_phone = {norm_phone(p): c for c in contacts for p in c["phones"]}

    plan = []
    for lead in leads:
        if not lead["elegivel"]:
            continue
        phone_key = norm_phone(lead["telefone"])
        contact = contacts_by_phone.get(phone_key)
        suffix = lead["mmaa"] + ("+" if lead["duplicado"] else "")
        base_name = contact["name"].split(f" {SUFFIX}")[0].strip() if contact else first_name(lead["nome"])
        plan.append({"lead": lead, "contact": contact, "base_name": base_name, "suffix": suffix})

    by_base = defaultdict(list)
    for item in plan:
        by_base[item["base_name"]].append(item)
    for items in by_base.values():
        if len(items) > 1:
            for item in items:
                item["base_name"] = disambiguate(item["lead"])

    return plan


def main():
    plan = build_plan()
    service = get_service()

    renamed, created, skipped = 0, 0, 0
    for item in plan:
        expected_name = f"{item['base_name']} {SUFFIX} {item['suffix']}"
        lead, contact = item["lead"], item["contact"]

        if contact:
            if contact["name"] == expected_name:
                skipped += 1
                continue
            body = {
                "etag": contact["etag"],
                "names": [{"givenName": expected_name}],
            }
            service.people().updateContact(
                resourceName=contact["resourceName"],
                updatePersonFields="names",
                body=body,
            ).execute()
            print(f"RENOMEADO: '{contact['name']}' -> '{expected_name}'")
            renamed += 1
        else:
            # Ferramenta de correção de telefone já entra aqui na criação:
            # salva as 2 variantes do número (com/sem o 9º dígito) desde o
            # início, não só como backfill depois.
            phones = [{"value": lead["telefone"]}]
            alt = alt_format(lead["telefone"])
            if alt:
                phones.append({"value": alt})
            body = {
                "names": [{"givenName": expected_name}],
                "phoneNumbers": phones,
            }
            if lead["email"]:
                body["emailAddresses"] = [{"value": lead["email"]}]
            service.people().createContact(body=body).execute()
            print(f"CRIADO: '{expected_name}' (linha {lead['row_num']})")
            created += 1

    print(f"\nTotal: {renamed} renomeados, {created} criados, {skipped} já corretos.")


if __name__ == "__main__":
    main()
