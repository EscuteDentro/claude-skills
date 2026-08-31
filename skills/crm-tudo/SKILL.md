---
name: crm-tudo
description: Roda o CRM completo de ponta a ponta numa única chamada — aciona `crm-lead` (primeiro contato + ferramentas que você configurou) e depois `crm-fup` (status real de conversa via WhatsApp, Dores e Desejos, Objeções) sempre nessa ordem, e fecha com um resumo único combinando os dois. Use quando quiser rodar tudo de uma vez sem chamar as duas skills separadamente.
user-invocable: true
---

> **Instalação:** copiar esta pasta para `.claude/skills/crm-tudo/` no projeto. Só faz sentido com `crm-lead` e `crm-fup` já instalados e configurados — esta skill não tem `config.py` próprio, ela só orquestra as outras duas.

---

# CRM Tudo — orquestrador de ponta a ponta

Esta skill não reimplementa nada. Ela só aciona `crm-lead` e depois `crm-fup`, nessa ordem, cada uma até o fim do próprio fluxo (SKILL.md correspondente), e fecha com um resumo combinado. Qualquer mudança de comportamento das duas skills individuais vive nos SKILL.md delas, nunca aqui — isso evita duas fontes divergindo.

> **Nota de manutenção:** este skill tem uma implementação privada gêmea (mesma lógica, dados reais) mantida fora deste repo. Ao corrigir bug ou reforçar segurança aqui, checar se o mesmo problema existe na versão privada, e vice-versa — nunca corrigir só de um lado.

## Ordem fixa: `crm-lead` sempre primeiro, `crm-fup` sempre depois

Não inverter nem pular, mesmo que pareça que "não tem lead novo". Motivo real, achado em produção: rodar `crm-fup` sozinho várias vezes numa sessão sem `crm-lead` ter rodado de novo antes deixa lead novo (formulário respondido nesse intervalo) parado — sem duplicata verificada, sem contato salvo, sem link gerado, e sem entrar na aba FUP. Só aparece se alguém notar a aba de leads original desatualizada. `crm-lead` processa essa aba original (onde formulário novo chega primeiro); `crm-fup` só sabe de um contato se ele já estiver na FUP. Rodar `crm-lead` sempre antes fecha esse gap de forma estrutural, não por lembrete.

## Fluxo

1. **Acionar a skill `crm-lead`** e completar o fluxo dela inteiro (as ferramentas modulares que você configurou — ver o SKILL.md dela pra lista completa).
2. **Acionar a skill `crm-fup`** e completar o fluxo dela inteiro, do passo 1 (captura da lista) até o passo 6 (resumo).
3. **Fechar com resumo único**, combinando os dois: duplicatas resolvidas, leads sem contato (com link), contatos salvos/renomeados, distribuição de Status na FUP, linhas novas em Dores e Desejos e em Objeções, células sincronizadas de volta pra aba de leads. Sem inventar número — só o que os scripts de cada skill realmente reportaram.

## Regras herdadas (não duplicar aqui, só reforçar)

- **Nunca enviar mensagem** — herdado do `crm-fup`, vale pro fluxo inteiro.
- **Comando de execução ponta a ponta autoriza os gates internos das duas skills**: se o usuário pediu pra rodar este orquestrador, isso já é a aprovação pros passos que cada SKILL.md individual descreve como "dry-run → mostrar → confirmar" — não parar em cada um pra perguntar de novo, só se achar algo genuinamente anômalo (dado inconsistente, risco de privacidade, ambiguidade real que a própria skill já lista como "pare e avise").
- **Sync de volta sempre derivado do que foi de fato processado na rodada, nunca de uma lista escolhida a dedo**: ao montar o payload do passo 5 do `crm-fup` (sync pra aba de leads), incluir TODOS os contatos abertos/atualizados nessa rodada — não só os que tiveram D&D ou Objeção capturada. Ver corner case correspondente no SKILL.md do `crm-fup`.

## Se um dos dois falhar

Se `crm-lead` travar (ex: credencial faltando ou expirada), reportar o bloqueio primeiro. Perguntar se quer prosseguir só com `crm-fup` mesmo assim — funcionam de forma majoritariamente independente, mas pular `crm-lead` reintroduz o risco de lead novo ficar de fora (ver seção "Ordem fixa" acima). Nunca tentar recriar credencial sozinho sem aprovação explícita.

Se `crm-fup` identificar no teste de sanidade que o WhatsApp Web não está logado/responsivo, parar e avisar — não prosseguir tratando "só a parte do crm-lead que já rodou" como se fosse rodada completa.
