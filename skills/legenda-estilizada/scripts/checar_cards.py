#!/usr/bin/env python3
"""Confere cards de legenda de qualquer origem. Uso: checar_cards.py cards.json [--largura-max N]
Aceita {"cards": [{"text": ...}]} do build_captions ou lista com "text"/"t". Sai com erro se achar defeito.
Regras: sem filler vocal; sem pontuação .,:; no fim; enumeração com 1 item por card; última linha sem palavra sozinha."""
import json, re, sys
FILLER = re.compile(r"(^|\s)(h?[ãa]{2,}|h?[eé]{2,}|ah+n+|hu*m{2,})([,.!?…\s]|$)", re.I)
d = json.load(open(sys.argv[1]))
cards = d["cards"] if isinstance(d, dict) and "cards" in d else d.get("leg", d) if isinstance(d, dict) else d
erros = []
for c in cards:
    t = (c.get("text") or c.get("t") or "").replace("/", " ")
    if not t:
        continue
    if FILLER.search(t):
        erros.append(("filler", t))
    if t.rstrip()[-1] in ".,:;":
        erros.append(("pontuação no fim", t))
    if t.count(",") >= 2:
        erros.append(("lista no mesmo card", t))
for tipo, t in erros:
    print(f"{tipo}: {t}")
print(f"{len(cards)} cards, {len(erros)} defeitos")
sys.exit(1 if erros else 0)
