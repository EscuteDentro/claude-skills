"""Ferramenta de WhatsApp: gera o link wa.me pronto pra um lead, usando o
template certo (quente/frio) do Banco de Mensagens -- nunca reinventa copy.

Trava de consentimento embutida na própria função (defesa em profundidade,
não só documentação): `gerar_link()` exige o valor de "Consentiu WA" como
argumento e recusa gerar qualquer link se não for exatamente "Sim" --
mesmo que quem chamar esqueça de filtrar antes. O link é só pra você
clicar; este script nunca abre nem envia nada sozinho.
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


class SemConsentimentoError(Exception):
    """Levantado quando gerar_link() é chamado pra um lead sem consentimento
    explícito de WhatsApp -- nunca capturar essa exceção pra tentar gerar o
    link de outro jeito; é um bloqueio proposital, não um erro técnico."""


def gerar_link(nome, telefone, timestamp_iso, consentiu_wa):
    if str(consentiu_wa).strip() != "Sim":
        raise SemConsentimentoError(
            f"Lead '{nome}' tem Consentiu WA={consentiu_wa!r} -- link NUNCA gerado "
            "sem consentimento explícito ('Sim'). Use o template de e-mail pra esse lead."
        )
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
    if len(sys.argv) != 5:
        print("Uso: python3 gerar_link_whatsapp.py '<nome>' '<telefone>' '<timestamp ISO>' '<Consentiu WA: Sim|Não>'")
        sys.exit(1)
    link, segmento = gerar_link(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print(f"Segmento: {segmento}")
    print(f"Link: {link}")
