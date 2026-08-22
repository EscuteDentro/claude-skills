"""Popula a aba Banco de Copies: síntese de Dores e Desejos agrupada por
Categoria, com fontes rastreáveis e hook sugerido.

Este arquivo é um TEMPLATE -- ROWS abaixo é só exemplo de formato, apague
e preencha com os padrões reais do seu Dores e Desejos. Síntese exige
leitura humana/IA pra agrupar por padrão (não dá pra automatizar por
contagem de string) -- rode de novo, reescrevendo ROWS, quando Dores e
Desejos tiver crescido o suficiente pra valer revisão dos agrupamentos.

Regras de agrupamento (ver SKILL.md e, se você tiver, seu manual de hooks):
- Respeitar a Categoria já atribuída em Dores e Desejos como eixo primário
  -- não juntar padrões de categorias diferentes num hook só, mesmo quando
  o tema parece próximo entre categorias.
- "Leads distintos" != número de linhas -- se o mesmo lead aparece em mais
  de uma linha, reportar quantas PESSOAS diferentes confirmam o padrão,
  não quantas linhas. Nunca deixar "3 linhas" parecer "3 pessoas".
- Relato indireto (sobre terceiro, não o próprio lead) entra como sinal de
  mercado, mas o campo "Hook sugerido" fica vazio e a Observação avisa --
  nunca virar citação direta de lead que não disse aquilo.
- Se você tiver um manual de hooks (config.MANUAL_HOOKS_PATH), aplicar a
  mecânica dele no "Hook sugerido": sensorial e específico, não abstrato;
  nunca frase que serviria pra qualquer pessoa em qualquer situação.
"""
from sheets_client import get_service
import config

HEADERS = [
    "Categoria", "Padrão", "Leads distintos",
    "Fontes (linhas D&D)", "Hook sugerido", "Frase(s) de referência", "Observação",
]

# EXEMPLO -- apague e substitua pelos padrões reais do seu Dores e Desejos.
ROWS = [
    [
        "{categoria 1}", "{descreva o padrão que se repete}",
        "1", "{linhas de origem, ex: 2, 5}",
        "{hook -- cena/confissão específica, não afirmação abstrata}",
        "{frase literal de origem, quase verbatim}",
        "",
    ],
]


def write():
    service = get_service()
    body = {"values": [HEADERS] + ROWS}
    service.spreadsheets().values().update(
        spreadsheetId=config.SHEET_ID, range=f"{config.BANCO_COPIES_TAB}!A1",
        valueInputOption="RAW", body=body,
    ).execute()


if __name__ == "__main__":
    write()
    print(f"Banco de Copies populado com {len(ROWS)} padrão(ões) -- edite ROWS neste arquivo com os seus achados reais.")
