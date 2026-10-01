"""Compara uma captura fresca do WhatsApp (lida e parseada pelo agente,
não por regex aqui -- texto de busca do WhatsApp é irregular demais pra
parser determinístico: nomes com badge de avatar, tags de arquivada/não
lida intercaladas etc.) contra o estado gravado na aba FUP.

Uso: python3 fup_diff.py captura.json
Formato de captura.json: lista de {"nome": ..., "data": "YYYY-MM-DD", "trecho": ...}
(+ opcionais "canal" e "id", ver identidade.py). `data` já vem absoluta (o
agente resolve "Ontem"/"quarta-feira" antes de escrever o arquivo).

Casamento captura <-> linha da FUP pela chave estável (canal, id) de
identidade.py -- no zap, o telefone. Nome só entra como fallback: ele muda
(rename, sufixo de mês, sobrenome) e casar por ele gera falso "contato novo".

Diff de 2 parâmetros: muda se DATA OU TRECHO mudou -- mensagem nova no
mesmo dia também conta, porque o trecho muda mesmo sem a data mudar.

Comparação de trecho é por PREFIXO comum (primeiros TRECHO_CMP_LEN chars),
sem aspas, nunca igualdade exata -- capturas de sessões diferentes truncam o
trecho em tamanhos diferentes. Trecho vazio (mídia, mensagem apagada) não
compara; aviso do aplicativo como última linha não conta como atividade.

Comparação de data normaliza DD/MM/AAAA (como a Sheet devolve célula DATE)
pra ISO antes de comparar.
"""
import json
import re
import sys
from pathlib import Path

from sheets_client import get_all_rows
import config
from captura import is_sistema, load_captura
from identidade import CANAL_PADRAO, ID_HEADER_POR_CANAL, canon_id, nome_para_ids_zap

TRECHO_CMP_LEN = 40  # comparar só o prefixo -- robusto a truncamento diferente entre capturas


def norm_trecho(t):
    """Remove aspas retas/curvas -- o WhatsApp varia se cita o texto reagido
    entre aspas ou não conforme a sessão de captura."""
    return re.sub(r'["“”]', "", t)


def to_iso(data_str):
    """DD/MM/AAAA -> AAAA-MM-DD. Deixa como está se já for ISO ou vazio."""
    m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", data_str)
    if m:
        d, mo, y = m.groups()
        return f"{y}-{mo}-{d}"
    return data_str


def get_fup_state():
    """Linhas da FUP indexadas pela chave estável (canal, id) e, como
    fallback, pelo Nome."""
    headers, rows = get_all_rows(config.FUP_TAB)
    idx = {h: i for i, h in enumerate(headers)}
    por_chave, por_nome, duplicadas = {}, {}, []
    for row_num, r in enumerate(rows, start=2):
        def cell(col):
            i = idx.get(col)
            return r[i] if i is not None and len(r) > i else ""
        nome = cell("Nome")
        if not nome:
            continue
        linha = {
            "row": row_num,
            "nome": nome,
            "data": cell("Data última mensagem"),
            "trecho": cell("Trecho última mensagem"),
            "ids": {},
        }
        for canal, header in ID_HEADER_POR_CANAL.items():
            bruto = cell(header)
            if bruto:
                linha["ids"][canal] = bruto
                chave = (canal, canon_id(canal, bruto))
                if chave in por_chave:
                    duplicadas.append((por_chave[chave], linha))
                else:
                    por_chave[chave] = linha
        por_nome[nome] = linha
    if duplicadas:
        print(f"ATENÇÃO: {len(duplicadas)} pessoa(s) com 2 linhas na FUP (mesma chave). Fundir antes de confiar no diff:")
        for a, b in duplicadas:
            print(f"  linha {a['row']} ({a['nome']}) e linha {b['row']} ({b['nome']})")
        print()
    return por_chave, por_nome


def achar_linha(item, por_chave, por_nome, ids_zap_por_nome):
    """Chave estável primeiro (id que veio na captura; no zap, telefone do
    Google Contatos pelo nome exibido), Nome só quando não há chave."""
    canal = item.get("canal", CANAL_PADRAO)
    if item.get("id"):
        ids = {canon_id(canal, item["id"])}
    elif canal == "zap":
        ids = ids_zap_por_nome.get(item["nome"], set())
    else:
        ids = set()
    for i in ids:
        linha = por_chave.get((canal, i))
        if linha:
            return linha
    return por_nome.get(item["nome"])


def diff(captura_path):
    por_chave, por_nome = get_fup_state()
    captura = load_captura(captura_path)
    ids_zap_por_nome = nome_para_ids_zap()

    novos, mudados, sem_mudanca, nomes_divergentes, avisos_sistema = [], [], [], [], []
    for item in captura:
        nome, data, trecho = item["nome"], item["data"], item["trecho"]
        linha = achar_linha(item, por_chave, por_nome, ids_zap_por_nome)
        sistema = is_sistema(trecho)
        if linha is None:
            novos.append({**item, "so_aviso_de_sistema": sistema})
            continue
        if linha["nome"] != nome:
            nomes_divergentes.append({
                "row": linha["row"], "nome_fup": linha["nome"], "nome_captura": nome,
                "telefone": linha["ids"].get("zap", ""),
            })
        if sistema:
            avisos_sistema.append(nome)  # aviso do aplicativo não é mensagem de ninguém
            continue
        # trecho vazio na lista (mídia, mensagem apagada) não é comparável: decide só a data
        trecho_mudou = bool(trecho) and (
            norm_trecho(linha["trecho"])[:TRECHO_CMP_LEN] != norm_trecho(trecho)[:TRECHO_CMP_LEN]
        )
        data_mudou = to_iso(linha["data"]) != to_iso(data)
        if data_mudou or trecho_mudou:
            mudados.append({**item, "row": linha["row"], "data_anterior": linha["data"],
                            "telefone": linha["ids"].get("zap", "")})
        else:
            sem_mudanca.append(nome)

    print(f"{len(novos)} contato(s) novo(s) (sem linha na FUP):")
    for n in novos:
        marca = " [só aviso de sistema, sem mensagem real]" if n["so_aviso_de_sistema"] else ""
        print(f"  + {n['nome']} | {n['data']} | {n['trecho'][:60]}{marca}")

    print(f"\n{len(mudados)} contato(s) com atividade nova desde a última rodada:")
    for m in mudados:
        print(f"  ~ {m['nome']} (linha {m['row']}) | era {m['data_anterior']}, agora {m['data']} | {m['trecho'][:60]}")

    print(f"\n{len(sem_mudanca)} sem mudança (não precisa abrir).")
    if avisos_sistema:
        print(f"{len(avisos_sistema)} com aviso de sistema como última linha (ignorado): {', '.join(avisos_sistema)}")
    if nomes_divergentes:
        print(f"\n{len(nomes_divergentes)} nome(s) na FUP diferente(s) do exibido na conversa (mesma pessoa, casada pela chave):")
        for d in nomes_divergentes:
            print(f"  linha {d['row']}: '{d['nome_fup']}' -> '{d['nome_captura']}'")
        print("  Alinhar: python3 fup_update_rows.py --alinhar-nomes diff_resultado.json")

    out = {"novos": novos, "mudados": mudados, "nomes_divergentes": nomes_divergentes}
    Path("diff_resultado.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print("\nLista de quem precisa ser aberto salva em diff_resultado.json")
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 fup_diff.py captura.json")
        sys.exit(1)
    diff(sys.argv[1])
