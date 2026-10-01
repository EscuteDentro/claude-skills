"""Dry-run: propõe preencher 'Status CRM' na aba Leads com o que este skill
descobriu de verdade no WhatsApp (data do contato real), só pra quem a célula
está vazia. Nunca sobrescreve valor humano, nunca escreve em COMPROU = Sim.

Telefone casado pela forma canônica (com/sem o 9 extra é a mesma pessoa).

Telefone com mais de uma linha na Leads (grupo de duplicata):
- grupo inteiro com Status CRM vazio: a linha `Duplicado = 1` (ou a mais
  antiga, se não houver) vira âncora e recebe o texto real; as demais recebem
  `Ver linha N`. Uma âncora por pessoa, mesma convenção do crm-lead.
- grupo com alguma linha já preenchida: pula. Já existe âncora ou valor
  humano; ligar o resto é trabalho do crm-lead (plan_status_crm.py).

Uso: python3 plan_sync_leads.py achados.json
Formato achados.json: lista de {"telefone": ..., "data_contato": "DD/MM"}
"""
import json
import sys

from sheets_client import get_all_rows
from identidade import canon_tel
import config



def plan(achados_path):
    headers, rows = get_all_rows(config.LEADS_TAB)
    idx = {h: i for i, h in enumerate(headers)}

    def cell(row_num, col):
        r = rows[row_num - 2]
        i = idx.get(col)  # coluna opcional (ex: Duplicado, COMPROU) pode não existir na sua aba
        return r[i].strip() if i is not None and len(r) > i else ""

    by_phone = {}
    for row_num, r in enumerate(rows, start=2):
        tel = r[idx["Telefone"]] if len(r) > idx["Telefone"] else ""
        if tel:
            by_phone.setdefault(canon_tel(tel), []).append(row_num)

    with open(achados_path) as f:
        achados = json.load(f)

    proposals, skipped_anchored, skipped_filled, skipped_comprou = [], [], [], []
    for a in achados:
        tel, data = a["telefone"], a["data_contato"]
        matches = by_phone.get(canon_tel(tel), [])
        if not matches:
            continue
        if any(cell(n, "COMPROU") == "Sim" for n in matches):
            skipped_comprou.append((tel, matches))
            continue
        texto = f"Contato via WhatsApp ({data})"
        if len(matches) == 1:
            row_num = matches[0]
            if cell(row_num, "Status CRM"):
                skipped_filled.append((row_num, cell(row_num, "Status CRM")))
                continue
            proposals.append((row_num, tel, texto))
            continue
        if any(cell(n, "Status CRM") for n in matches):
            skipped_anchored.append((tel, matches))
            continue
        ancora = next((n for n in matches if cell(n, "Duplicado").rstrip("*") == "1"), min(matches))
        proposals.append((ancora, tel, texto))
        for n in matches:
            if n != ancora:
                proposals.append((n, tel, f"Ver linha {ancora}"))

    print(f"{len(proposals)} célula(s) de Status CRM pra preencher:")
    for row_num, tel, texto in proposals:
        print(f"  linha {row_num} ({tel}): -> \"{texto}\"")
    print(f"\n{len(skipped_filled)} pulada(s) por já ter valor humano.")
    print(f"{len(skipped_anchored)} grupo(s) de duplicata pulado(s) por já ter linha preenchida (âncora existente).")
    print(f"{len(skipped_comprou)} pulada(s) por COMPROU = Sim (nunca escrever).")
    return proposals


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 plan_sync_leads.py achados.json")
        sys.exit(1)
    plan(sys.argv[1])
