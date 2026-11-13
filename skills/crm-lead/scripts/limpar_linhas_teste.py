"""Apaga linhas de teste de uma aba de leads (nome "teste"/"test" ou telefone de dígito repetido, ex. 11999999999).

Uso: python3 limpar_linhas_teste.py "<aba>"            (dry-run)
     python3 limpar_linhas_teste.py "<aba>" --executar

- Relê a linha logo antes de apagar e confere nome+telefone (nunca apaga pela posição de uma leitura velha)
- Apaga de baixo pra cima (índice das de cima não muda) e corrige todo "Ver linha N" que apontava pra baixo
  das linhas apagadas; "Ver linha N" que apontava PRA uma linha de teste vira vazio
"""
import re
import sys

import config
from sheets_client import get_service

SHEET_ID = config.SHEET_ID


def e_teste(nome, tel):
    d = re.sub(r"\D", "", tel or "")
    return (nome or "").strip().lower() in ("teste", "test") or bool(re.search(r"(\d)\1{6,}$", d[-8:] or "x"))


def main(aba, executar):
    svc = get_service()
    sid = next(s["properties"]["sheetId"] for s in svc.spreadsheets().get(
        spreadsheetId=SHEET_ID, fields="sheets.properties").execute()["sheets"] if s["properties"]["title"] == aba)
    vals = svc.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=f"'{aba}'!A1:AZ").execute()["values"]
    h = vals[0]
    iN, iT, iS = h.index("Nome"), h.index("Telefone"), h.index("Status CRM")
    g = lambda r, i: r[i] if i < len(r) else ""
    alvo = [n for n, r in enumerate(vals[1:], 2) if e_teste(g(r, iN), g(r, iT))]
    for n in alvo:
        print(f"APAGA linha {n}: {g(vals[n-1], iN)} {g(vals[n-1], iT)}")
    if not alvo:
        print("nenhuma linha de teste")
        return
    novos = []
    for n, r in enumerate(vals[1:], 2):
        m = re.fullmatch(r"Ver linha (\d+)", g(r, iS).strip())
        if not m or n in alvo:
            continue
        ref = int(m.group(1))
        novo = "" if ref in alvo else f"Ver linha {ref - sum(1 for a in alvo if a < ref)}"
        if novo != g(r, iS):
            novos.append((n - sum(1 for a in alvo if a < n), novo))
            print(f"AJUSTA Status CRM da linha {n}: '{g(r, iS)}' -> '{novo}'")
    if not executar:
        return
    for n in sorted(alvo, reverse=True):
        r = svc.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=f"'{aba}'!A{n}:AZ{n}").execute()["values"][0]
        if not e_teste(g(r, iN), g(r, iT)):
            sys.exit(f"linha {n} mudou desde a leitura, parei sem apagar")
        svc.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body={"requests": [{"deleteDimension": {
            "range": {"sheetId": sid, "dimension": "ROWS", "startIndex": n - 1, "endIndex": n}}}]}).execute()
    col = chr(ord("A") + iS)
    for n, novo in novos:
        svc.spreadsheets().values().update(spreadsheetId=SHEET_ID, range=f"'{aba}'!{col}{n}",
                                           valueInputOption="RAW", body={"values": [[novo]]}).execute()
    print(f"apagadas: {len(alvo)}, Status CRM ajustados: {len(novos)}")


if __name__ == "__main__":
    main(sys.argv[1], "--executar" in sys.argv)
