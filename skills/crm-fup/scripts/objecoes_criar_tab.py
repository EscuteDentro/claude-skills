"""Cria a aba Objeções (cabeçalho + 1 linha de exemplo fictícia) se ela
ainda não existir. Rodar 1x na instalação. A linha de exemplo existe só
pra você validar que as colunas fazem sentido pro seu negócio antes de
popular com conversa real -- apague-a antes da primeira rodada real.

Diferença estrutural pra "Dores e Desejos": objeção é captura da MESMA
forma (quem, quando, canal, categoria, tema, frase literal, contexto),
mas ganha 2 colunas que D&D não precisa -- "Resposta dada" (o que foi
dito de volta) e "Superada?" (resultado local daquela objeção, não
confundir com "Converteu?" de D&D, que é resultado geral do lead).
Objeção normalmente aparece mais adiante no diálogo, depois que D&D já
foi levantado.

Escopo do que entra aqui: resistência real do lead (preço, tempo,
ceticismo, "já tentei outra coisa", etc.), nunca dor/desejo disfarçado de
objeção -- isso é D&D. Campo "Superada?" só recebe "Sim" com confirmação
explícita (mesma regra de "Converteu?" em Dores e Desejos: nunca por
inferência de contexto).
"""
from sheets_client import get_service
import config

HEADERS = [
    "#", "Data", "Canal", "Objeção", "Categoria", "Tema", "Nome",
    "Id", "Contexto", "Frase literal", "Resposta dada", "Superada?", "Observação",
]

EXEMPLO = [
    "1", "2026-01-01", "zap", "{objeção real, ex: preço alto pro momento financeiro}",
    "{categoria 1}", "parcelamento; timing financeiro", "EXEMPLO — apagar",
    "0000-EXEMPLO",
    "Já demonstrou desejo real de fazer o produto, mas hesitou na hora de decidir.",
    "Eu queria muito, mas agora tá contando centavo aqui",
    "Ofereci parcelamento e falei do valor por dia comparado a outros gastos",
    "Não sei",
    "Linha fictícia só pra validar as colunas — apagar antes de popular dado real.",
]


def ensure_tab(service):
    meta = service.spreadsheets().get(spreadsheetId=config.SHEET_ID).execute()
    titles = [s["properties"]["title"] for s in meta["sheets"]]
    if config.OBJECOES_TAB in titles:
        return False
    service.spreadsheets().batchUpdate(
        spreadsheetId=config.SHEET_ID,
        body={"requests": [{"addSheet": {"properties": {"title": config.OBJECOES_TAB}}}]},
    ).execute()
    return True


def write():
    service = get_service()
    criada = ensure_tab(service)
    service.spreadsheets().values().update(
        spreadsheetId=config.SHEET_ID, range=f"{config.OBJECOES_TAB}!A1",
        valueInputOption="RAW", body={"values": [HEADERS, EXEMPLO]},
    ).execute()
    print(f"Aba '{config.OBJECOES_TAB}' {'criada' if criada else 'já existia'} + linha de exemplo escrita.")


if __name__ == "__main__":
    write()
