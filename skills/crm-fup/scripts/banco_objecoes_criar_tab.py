"""Cria a aba Banco de Objeções (só cabeçalho -- sem exemplo fictício,
diferente de objecoes_criar_tab.py). Síntese de "Objeções" agrupada por
Categoria, com fontes rastreáveis e o caminho que de fato funcionou pra
superar cada padrão.

Papel distinto de Banco de Copies: Banco de Copies existe pra gerar ideia
de anúncio/conteúdo (hook a partir de dor/desejo real). Banco de Objeções
existe pra estudar e melhorar argumentação de venda 1:1 -- alimenta
roteiro comercial/SPIN, não copy.

Só popular linha aqui quando "Objeções" tiver massa real o suficiente pra
generalizar um padrão (mesma lógica de banco_copies_popular.py -- síntese
exige leitura humana/IA, não é automático, e não inventar "caminho
eficaz" sem ter uma resposta real que funcionou registrada em Objeções).
"""
from sheets_client import get_service
import config

HEADERS = [
    "Categoria", "Objeção padrão", "Leads distintos",
    "Fontes (linhas Objeções)", "Caminho eficaz", "Frase(s) de referência", "Observação",
]


def ensure_tab(service):
    meta = service.spreadsheets().get(spreadsheetId=config.SHEET_ID).execute()
    titles = [s["properties"]["title"] for s in meta["sheets"]]
    if config.BANCO_OBJECOES_TAB in titles:
        return False
    service.spreadsheets().batchUpdate(
        spreadsheetId=config.SHEET_ID,
        body={"requests": [{"addSheet": {"properties": {"title": config.BANCO_OBJECOES_TAB}}}]},
    ).execute()
    return True


def write():
    service = get_service()
    criada = ensure_tab(service)
    service.spreadsheets().values().update(
        spreadsheetId=config.SHEET_ID, range=f"{config.BANCO_OBJECOES_TAB}!A1",
        valueInputOption="RAW", body={"values": [HEADERS]},
    ).execute()
    print(f"Aba '{config.BANCO_OBJECOES_TAB}' {'criada' if criada else 'já existia'} + cabeçalho escrito.")


if __name__ == "__main__":
    write()
