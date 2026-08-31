# crm-tudo

Orquestrador de ponta a ponta: aciona `crm-lead` e depois `crm-fup`, sempre nessa ordem, numa única chamada. Não reimplementa nada das duas — é só um atalho pra não precisar chamar as duas skills separadamente. Ver [SKILL.md](./SKILL.md) pro fluxo completo e o porquê da ordem fixa.

## Pré-requisitos

- `crm-lead` instalado e configurado (pelo menos as ferramentas que você quiser usar).
- `crm-fup` instalado e configurado (mesma Sheet e credencial do `crm-lead`).

Esta skill não tem `config.py` próprio — ela só chama as outras duas, que já têm a configuração delas.

## Instalação

Copiar esta pasta inteira pra `.claude/skills/crm-tudo/` no seu projeto. Não precisa de dependências novas nem de setup adicional além do que `crm-lead` e `crm-fup` já exigem.

## Uso

Peça ao Claude pra rodar o skill (`/crm-tudo` se você criou um command apontando pro SKILL.md, ou só descrevendo o pedido — "roda o CRM inteiro"). Ele executa `crm-lead` até o fim, depois `crm-fup` até o fim, e fecha com um resumo combinado.

## LGPD / privacidade

Herda integralmente as regras de `crm-lead` e `crm-fup` — nenhum dado novo, nenhum comportamento novo de coleta ou contato. Ver a seção "LGPD" em cada um dos dois SKILL.md.
