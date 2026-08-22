"""Aplica o plano de plan_sync_leads.py. Rodar só depois de revisar o dry-run."""
import sys

from sheets_client import get_service, get_all_rows, col_letter
from plan_sync_leads import plan
import config


def execute(achados_path):
    proposals = plan(achados_path)
    if not proposals:
        print("Nada pra escrever.")
        return
    service = get_service()
    headers, _ = get_all_rows(config.LEADS_TAB)
    idx = {h: i for i, h in enumerate(headers)}
    col = col_letter(idx["Status CRM"])
    updates = [{"range": f"{config.LEADS_TAB}!{col}{row_num}", "values": [[texto]]}
               for row_num, _, texto in proposals]
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=config.SHEET_ID, body={"valueInputOption": "RAW", "data": updates}
    ).execute()
    print(f"{len(updates)} célula(s) escrita(s) na aba Leads.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 execute_sync_leads.py achados.json")
        sys.exit(1)
    execute(sys.argv[1])
