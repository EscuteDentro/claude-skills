"""Dry-run: propõe preencher 'Status CRM' na aba Leads com o que este skill
descobriu de verdade no WhatsApp (data do contato real), só pra quem a
célula está vazia. Nunca sobrescreve valor humano.

Se o telefone bate com mais de uma linha da Leads (duplicata não
resolvida), pula e avisa -- resolver duplicata é trabalho do skill
`crm-lead` (plan_status_crm.py), não deste script.

Uso: python3 plan_sync_leads.py achados.json
Formato achados.json: lista de {"telefone": ..., "data_contato": "DD/MM"}
"""
import json
import sys

from sheets_client import get_all_rows
import config


def plan(achados_path):
    headers, rows = get_all_rows(config.LEADS_TAB)
    idx = {h: i for i, h in enumerate(headers)}

    by_phone = {}
    for row_num, r in enumerate(rows, start=2):
        tel = r[idx["Telefone"]] if len(r) > idx["Telefone"] else ""
        if tel:
            by_phone.setdefault(tel, []).append(row_num)

    with open(achados_path) as f:
        achados = json.load(f)

    proposals, skipped_dup, skipped_filled = [], [], []
    for a in achados:
        tel, data = a["telefone"], a["data_contato"]
        matches = by_phone.get(tel, [])
        if len(matches) == 0:
            continue
        if len(matches) > 1:
            skipped_dup.append((tel, matches))
            continue
        row_num = matches[0]
        status_atual = rows[row_num - 2][idx["Status CRM"]] if len(rows[row_num - 2]) > idx["Status CRM"] else ""
        if status_atual.strip():
            skipped_filled.append((row_num, status_atual))
            continue
        proposals.append((row_num, tel, f"Contato via WhatsApp ({data})"))

    print(f"{len(proposals)} célula(s) de Status CRM pra preencher:")
    for row_num, tel, texto in proposals:
        print(f"  linha {row_num} ({tel}): -> \"{texto}\"")
    print(f"\n{len(skipped_filled)} pulada(s) por já ter valor humano.")
    print(f"{len(skipped_dup)} pulada(s) por telefone duplicado na Leads (rodar crm-lead antes).")
    return proposals


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 plan_sync_leads.py achados.json")
        sys.exit(1)
    plan(sys.argv[1])
