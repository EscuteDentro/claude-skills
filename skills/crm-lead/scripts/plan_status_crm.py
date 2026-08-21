"""Ferramenta de sinalização de duplicação (extensão): dry-run que, pra
cada grupo de duplicata que já tem uma linha-âncora (Status CRM começando
com "Contato via WhatsApp" -- ajuste ANCORA_PREFIXO se seu texto de status
for diferente), propõe "Ver linha N" pras demais linhas do grupo que ainda
não apontam corretamente pra ela.

Princípio: só existe UMA âncora de contato por pessoa/grupo -- follow-up
não é contato novo, é parte da mesma conversa. A âncora é a linha onde o
contato de fato aconteceu; TODAS as outras linhas do grupo -- mais antigas
OU mais novas que ela -- apontam pra ela, nunca o contrário.

Alerta de intervalo: se a entrada mais nova do grupo estiver a mais de
JANELA_DIAS de distância da âncora (comparando Timestamp), o plano AINDA
propõe o "Ver linha N" por padrão (contato antigo continua valendo), mas
marca ⚠️ ATENÇÃO na saída pro usuário decidir se vale reabordar -- nunca
bloqueia a escrita sozinho.

Se aparecer mais de uma âncora no mesmo grupo (anomalia -- não deveria
acontecer), reporta e não resolve sozinho.

Nunca mexe em linha com COMPROU = Sim. Reusa o agrupamento de
plan_duplicado.build_duplicate_groups -- nunca reimplementar o union-find
aqui (já aconteceu 1x de escrever uma versão aproximada/inferior aqui por
engano; sempre importar, nunca reconstruir).
"""
from datetime import datetime, timezone

from sheets_client import get_all_rows
from plan_duplicado import build_duplicate_groups, pad

ANCORA_PREFIXO = "Contato via WhatsApp"
JANELA_DIAS = 7


def parse_timestamp(ts):
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


def compute_plan():
    headers, rows = get_all_rows()
    idx = {h: i for i, h in enumerate(headers)}
    rows = [pad(r, len(headers)) for r in rows]
    groups = build_duplicate_groups(headers, rows)

    plan = []
    anomalias = []
    for root, members in groups.items():
        members = sorted(members, key=lambda i: rows[i][idx["Timestamp"]])
        ancoras = [i for i in members if rows[i][idx["Status CRM"]].strip().startswith(ANCORA_PREFIXO)]

        if len(ancoras) == 0:
            continue
        if len(ancoras) > 1:
            nomes = [f"linha {i+2}" for i in ancoras]
            anomalias.append(f"Grupo com {len(ancoras)} linhas de contato real ({', '.join(nomes)}) -- não deveria acontecer, confira manualmente.")
            continue

        anchor_i = ancoras[0]
        anchor_row_num = anchor_i + 2
        anchor_ts = parse_timestamp(rows[anchor_i][idx["Timestamp"]])

        for i in members:
            if i == anchor_i:
                continue
            r = rows[i]
            if r[idx["COMPROU"]].strip() == "Sim":
                continue
            expected = f"Ver linha {anchor_row_num}"
            atual = r[idx["Status CRM"]].strip()
            if atual == expected:
                continue
            gap_dias = abs((parse_timestamp(r[idx["Timestamp"]]) - anchor_ts).days)
            plan.append({
                "row_num": i + 2,
                "nome": r[idx["Nome"]],
                "atual": atual,
                "esperado": expected,
                "gap_dias": gap_dias,
                "atencao": gap_dias > JANELA_DIAS,
            })
    return plan, anomalias


def main():
    plan, anomalias = compute_plan()
    print(f"Linhas com Status CRM pra apontar pra âncora: {len(plan)}")
    for item in plan:
        flag = f"  ⚠️  ATENÇÃO: {item['gap_dias']} dias de intervalo, confirme se ainda vale" if item["atencao"] else ""
        print(f"  linha {item['row_num']} ({item['nome']}): '{item['atual']}' -> '{item['esperado']}'{flag}")

    if anomalias:
        print(f"\n=== ANOMALIAS ({len(anomalias)}) ===")
        for a in anomalias:
            print(f"  {a}")


if __name__ == "__main__":
    main()
