"""Cria a aba Dores e Desejos (cabeçalho + 1 linha de exemplo fictícia) se
ela ainda não existir. Rodar 1x na instalação. A linha de exemplo existe só
pra você validar que as colunas fazem sentido pro seu negócio antes de
popular com conversa real -- apague-a antes da primeira rodada real.

Escopo do que entra aqui (ver SKILL.md): só dor/desejo REAL que motivou o
cliente a buscar seu produto, nunca objeção pura (preço, dúvida) isolada.
Campo "Converteu?" só recebe "Sim" com confirmação explícita -- nunca por
inferência de contexto (ver regra na SKILL.md).
"""
from sheets_client import get_service
import config

HEADERS = [
    "#", "Data", "Canal", "Dores e/ou Desejos", "Categoria", "Tema", "Nome",
    "Id", "Contexto", "Frase literal", "Converteu?", "Observação",
]

EXEMPLO = [
    "1", "2026-01-01", "zap", "Insônia / mente acelerada à noite",
    "{categoria 1}", "insônia; mente agitada", "EXEMPLO — apagar",
    "0000-EXEMPLO",
    "Preencheu form, contato de recuperação. Relatou a dor quando perguntado por que buscou o produto.",
    "Eu deito e a cabeça não para, fico revirando o dia inteiro até tarde",
    "Não", "Linha fictícia só pra validar as colunas — apagar antes de popular dado real.",
]


def ensure_tab(service):
    meta = service.spreadsheets().get(spreadsheetId=config.SHEET_ID).execute()
    titles = [s["properties"]["title"] for s in meta["sheets"]]
    if config.DORES_DESEJOS_TAB in titles:
        return False
    service.spreadsheets().batchUpdate(
        spreadsheetId=config.SHEET_ID,
        body={"requests": [{"addSheet": {"properties": {"title": config.DORES_DESEJOS_TAB}}}]},
    ).execute()
    return True


def write():
    service = get_service()
    criada = ensure_tab(service)
    service.spreadsheets().values().update(
        spreadsheetId=config.SHEET_ID, range=f"{config.DORES_DESEJOS_TAB}!A1",
        valueInputOption="RAW", body={"values": [HEADERS, EXEMPLO]},
    ).execute()
    print(f"Aba '{config.DORES_DESEJOS_TAB}' {'criada' if criada else 'já existia'} + linha de exemplo escrita.")


if __name__ == "__main__":
    write()
