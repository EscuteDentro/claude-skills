"""Ferramenta de correção de telefone (WhatsApp).

Acrescenta a variante de telefone sem o 9º dígito extra (formato antigo do
WhatsApp) como segundo número de cada contato marcado por
config.CONTATO_MARCADOR, sem remover o original. Cobre números salvos com
DDI 55 (13 dígitos) e sem DDI (11 dígitos, só DDD+local).

**Específico do Brasil**: números brasileiros de celular podem estar
registrados no WhatsApp no formato antigo (8 dígitos locais, sem o 9 extra)
mesmo quando a Sheet guarda o formato novo (9 dígitos). Buscar só a forma
da Sheet dá falso negativo -- o WhatsApp Web não faz essa equivalência
sozinho. Se seu público não é majoritariamente brasileiro, esta ferramenta
provavelmente não se aplica -- avise que não quer usá-la.

Idempotente: contato que já tem as 2 variantes não duplica nada (roda de
novo sem problema).
"""
from contacts_client import get_service, list_lead_contacts


def alt_format(raw):
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) == 13 and digits[4] == "9":
        return digits[:4] + digits[5:]          # 55+DDD+9local -> 55+DDD+8local
    if len(digits) == 11 and digits[2] == "9":
        return digits[:2] + digits[3:]           # DDD+9local -> DDD+8local
    return None


def main():
    contacts = list_lead_contacts()
    updated, skipped = 0, 0
    service = get_service()

    for c in contacts:
        if len(c["phones"]) != 1:
            skipped += 1
            continue
        original = c["phones"][0]
        alt = alt_format(original)
        if not alt:
            print(f"PULADO (formato inesperado): {c['name']} | {original!r}")
            skipped += 1
            continue
        body = {
            "etag": c["etag"],
            "phoneNumbers": [{"value": original}, {"value": alt}],
        }
        service.people().updateContact(
            resourceName=c["resourceName"],
            updatePersonFields="phoneNumbers",
            body=body,
        ).execute()
        print(f"OK: {c['name']} -> {original!r} / {alt!r}")
        updated += 1

    print(f"\nTotal: {updated} atualizados, {skipped} pulados (formato inesperado)")


if __name__ == "__main__":
    main()
