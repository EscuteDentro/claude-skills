"""Ferramenta de WhatsApp: gera o link wa.me pronto pra um lead, usando o
template certo (quente/frio) do Banco de Mensagens -- nunca reinventa copy.

NUNCA chamar pra lead com Consentiu WA != 'Sim' (checar antes de usar) --
essa checagem é responsabilidade de quem chama esta função, não é feita
aqui. O link é só pra você clicar; este script nunca abre nem envia nada
sozinho.
"""
import re
import urllib.parse
from datetime import datetime, timezone

from sheets_client import get_service
import config


def get_template(segmento):
    service = get_service()
    r = service.spreadsheets().values().get(
        spreadsheetId=config.SHEET_ID, range=f"{config.BANCO_MENSAGENS_TAB}!A1:E10"
    ).execute()
    values = r.get("values", [])
    headers = values[0]
    idx = {h: i for i, h in enumerate(headers)}
    for row in values[1:]:
        nome = row[idx["Nome do template"]].lower()
        canal = row[idx["Canal"]]
        if canal == "WhatsApp" and segmento in nome:
            return row[idx["Texto"]]
    return None


def primeiro_nome(nome_completo):
    primeiro = (nome_completo or "").strip().split()[0] if nome_completo.strip() else ""
    return primeiro[:1].upper() + primeiro[1:].lower() if primeiro else ""


def dias_desde(timestamp_iso):
    ts = datetime.strptime(timestamp_iso, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - ts).days


def gerar_link(nome, telefone, timestamp_iso):
    segmento = "quente" if dias_desde(timestamp_iso) < config.DIAS_CORTE_QUENTE_FRIO else "frio"
    template = get_template(segmento)
    if not template:
        return None, segmento
    texto = template.replace("[Nome]", primeiro_nome(nome))
    numero = re.sub(r"\D", "", telefone)
    link = f"https://wa.me/{numero}?text={urllib.parse.quote(texto)}"
    return link, segmento


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Uso: python3 gerar_link_whatsapp.py '<nome>' '<telefone>' '<timestamp ISO>'")
        sys.exit(1)
    link, segmento = gerar_link(sys.argv[1], sys.argv[2], sys.argv[3])
    print(f"Segmento: {segmento}")
    print(f"Link: {link}")
