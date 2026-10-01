"""Leitura da captura da lista de conversas (captura_AAAA-MM-DD.json).

Item: {"nome", "data" (AAAA-MM-DD), "trecho"} + opcionais "canal" e "id"
(ver identidade.py). O trecho é sempre o texto literal que a lista exibe:
é contra ele que a próxima rodada compara, então trecho resumido ou
reescrito à mão vira falso "mudou".
"""
import json
import re

# Avisos do próprio aplicativo: aparecem como última linha da conversa sem
# ninguém ter escrito nada. Nunca contam como atividade.
SISTEMA_RE = re.compile(
    r"usa um serviço seguro da Meta"
    r"|mensagens temporárias"
    r"|duração padrão para mensagens"
    r"|criptografia de ponta a ponta"
    r"|código de segurança .* mudou",
    re.IGNORECASE,
)


def is_sistema(trecho):
    return bool(SISTEMA_RE.search(trecho or ""))


def load_captura(path):
    with open(path) as f:
        return json.load(f)


def trecho_por_nome(path):
    """{nome: trecho literal} só de quem tem trecho real (não vazio, não aviso)."""
    return {i["nome"]: i["trecho"] for i in load_captura(path)
            if i.get("trecho") and not is_sistema(i["trecho"])}
