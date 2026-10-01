"""Chave estável de contato: par (canal, id).

Nome exibido muda (rename, sufixo de mês, sobrenome); o id do canal não. Todo
casamento entre a captura da conversa e a aba FUP passa por aqui.

Canal `zap`: id é o telefone canônico (só dígitos; número BR sem o 9 extra).
A lista do WhatsApp só mostra nome, então a ponte nome -> telefone vem do
Google Contatos (o nome do contato é exatamente o que o WhatsApp exibe).
Ponte opcional: sem `config.OAUTH_TOKEN_PATH`, o diff casa só por Nome.

Canal novo (Instagram, TikTok...): acrescentar a coluna de id na aba FUP,
registrar em ID_HEADER_POR_CANAL e gravar `canal` + `id` (ex: @usuario) em
cada item da captura. Sem telefone, a ponte via Contatos não se aplica; o id
precisa vir da própria captura.
"""
import os
import re

import config

CANAL_PADRAO = "zap"
ID_HEADER_POR_CANAL = {"zap": "Telefone"}


def canon_tel(raw):
    """Telefone comparável entre Sheet, Contatos e captura: só dígitos. Regra
    do 9 extra é específica do Brasil (DDI 55): as duas formas do mesmo
    número colapsam numa só. Outros países passam só pela limpeza."""
    d = re.sub(r"\D", "", raw or "")
    if len(d) in (10, 11) and not d.startswith("55"):
        d = "55" + d
    if d.startswith("55") and len(d) == 13 and d[4] == "9":
        d = d[:4] + d[5:]
    return d


def canon_id(canal, raw):
    if canal == "zap":
        return canon_tel(raw)
    return (raw or "").strip().lower().lstrip("@")


def nome_para_ids_zap():
    """{nome do contato: {telefones canônicos}} de todo contato Google cujo
    nome contém config.MARCADOR_BUSCA_WHATSAPP. Sem token configurado ou com
    Contatos indisponível devolve {} (o diff cai pro casamento por Nome)."""
    token_path = getattr(config, "OAUTH_TOKEN_PATH", None)
    if not token_path:
        return {}
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials.from_authorized_user_file(
            os.path.expanduser(token_path), ["https://www.googleapis.com/auth/contacts"])
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        service = build("people", "v1", credentials=creds)
        marcador = config.MARCADOR_BUSCA_WHATSAPP.lower()
        mapa, page_token = {}, None
        while True:
            resp = service.people().connections().list(
                resourceName="people/me", pageSize=1000,
                personFields="names,phoneNumbers", pageToken=page_token,
            ).execute()
            for person in resp.get("connections", []):
                names = person.get("names", [])
                nome = names[0]["displayName"] if names else ""
                if marcador not in nome.lower():
                    continue
                tels = {canon_tel(p.get("value", "")) for p in person.get("phoneNumbers", [])}
                mapa.setdefault(nome, set()).update(t for t in tels if t)
            page_token = resp.get("nextPageToken")
            if not page_token:
                return mapa
    except Exception as e:
        print(f"AVISO: Google Contatos indisponível ({e}); casando só por nome nesta rodada.")
        return {}
