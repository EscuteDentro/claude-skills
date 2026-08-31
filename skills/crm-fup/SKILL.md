---
name: crm-fup
description: CRM efetivo de recuperação de venda — verifica no WhatsApp todos os contatos marcados como lead, classifica status de follow-up (Ghost 1/2, Esperar, FUP, Responder, Convertida), captura dor/desejo real e objeção real do cliente em abas vivas, e sincroniza com a aba de leads original. Só leitura, nunca envia nada.
user-invocable: true
---

> **Instalação:** copiar esta pasta para `.claude/skills/crm-fup/` no projeto. Preencher `scripts/config.py` (copiar de `config.example.py` — reaproveite os valores de `crm-lead` se já tiver esse skill instalado) antes de usar. Rodar `python3 scripts/fup_criar_tab.py`, `python3 scripts/dores_desejos_criar_tab.py` e `python3 scripts/objecoes_criar_tab.py` uma vez, na instalação. Ver [README.md](./README.md) para o passo a passo completo.

---

# CRM FUP — Status de conversa e follow-up

Skill irmã do `crm-lead`. Enquanto `crm-lead` cuida do primeiro contato (aba de leads original, só quem chegou pelo seu funil de captura), este skill é o **CRM efetivo**: lê o WhatsApp de verdade pra saber em que pé está CADA contato marcado como lead (do funil original ou não — inclui lead que chegou por outro canal e nunca passou pela aba original), mantém a aba FUP atualizada, e alimenta uma aba viva de "Dores e Desejos" com o que for achado nas conversas.

> **Nota de manutenção:** este skill tem uma implementação privada gêmea (mesma lógica, dados reais) mantida fora deste repo. Ao corrigir bug ou reforçar segurança num script aqui, checar se o mesmo problema existe na versão privada equivalente, e vice-versa — nunca corrigir só de um lado.

**Regra absoluta — nunca violar, mesmo se pedido: NUNCA ENVIAR NADA. Só leitura.** Não clicar em enviar, não reagir a mensagem, não marcar como lida por engano e deixar assim. Automação de leitura em volume já é risco de suspensão de conta no WhatsApp/Meta, sem falar em envio.

**Sempre sob demanda, nunca agendado.** Não usar loop, cron ou qualquer disparo automático pra este skill. Rodar só quando o usuário chamar `/crm-fup` explicitamente na conversa.

## LGPD / privacidade

Mesmo desenho do `crm-lead`: nunca contata quem não deu consentimento, nunca envia mensagem automaticamente, dado sensível (conversa de cliente, telefone) fica só na Sheet do próprio usuário. A aba Dores e Desejos guarda fala real de cliente — trate como dado sensível: nome completo não é necessário, `Id`/telefone bastam pra rastreabilidade sem inflar exposição.

## Pré-requisito

`crm-lead` instalado e configurado (mesma Sheet, mesma credencial de Service Account) — este skill assume que já existe uma aba de leads com coluna `Telefone` e `Status CRM`. Sem isso, o sync de volta (passo 5 do fluxo) não tem onde escrever, mas o resto funciona igual.

## Segurança contra bloqueio (aplicar em toda rodada)

- **Teste de sanidade antes de tudo**: 1 screenshot do WhatsApp Web já logado e responsivo antes de abrir qualquer busca. Se aparecer QR code, tela de erro, ou qualquer diálogo de verificação/atividade incomum, **parar imediatamente e avisar o usuário** — nunca tentar contornar.
- **Teto por rodada** (`config.TETO_CONVERSAS_POR_RODADA`, padrão 20): se o diff achar mais conversas que isso, processa até o teto, reporta quanto falta, e para — continua numa próxima chamada, nunca tudo de uma vez.
- **Lote com pausa** (`config.LOTE_TAMANHO`, padrão 10) e check-in com o usuário entre lotes.
- **Pausa variável entre ações** (1-3s, não sempre o mesmo valor) ao navegar entre conversas — menos robótico que timing fixo.
- **Nunca duas rodadas muito próximas** (`config.MIN_MINUTOS_ENTRE_RODADAS`, padrão 30): se a aba FUP foi atualizada há menos que isso, avisar e perguntar se realmente quer rodar de novo agora.
- Navegação só visual (ferramenta de computador/leitura de página), nunca requisição de rede direta pro domínio do WhatsApp.

## Fluxo ao rodar `/crm-fup`

### 1. Captura barata da lista (1 busca, sem abrir nada)

Abrir WhatsApp Web, buscar `config.MARCADOR_BUSCA_WHATSAPP` na busca, rolar até o fim, e ler o texto da página. Parsear manualmente (o texto de busca do WhatsApp é irregular demais pra regex confiável — nomes com badge de avatar, tags de arquivada/não lida intercaladas) em uma lista de `{nome, data, trecho}` por contato, resolvendo datas relativas ("Ontem", "quarta-feira") pra data absoluta usando a data de hoje. Salvar como JSON (ex: `captura_YYYY-MM-DD.json` — já no `.gitignore` desta pasta, nunca commitar captura real).

Ignorar contatos que claramente não são leads reais (ex: nome de comércio que só coincide ter o marcador de busca numa palavra do nome — checar contexto antes de tratar como lead).

### 2. Diff contra o estado gravado

```bash
cd scripts && python3 fup_diff.py captura_YYYY-MM-DD.json
```

Gera `diff_resultado.json` com quem é novo e quem mudou (data OU trecho diferente do gravado — mensagem nova no mesmo dia já muda o trecho, então entra no diff mesmo sem mudar a data). Reporte os números pro usuário antes de continuar.

### 3. Processar em lote (abrir só quem mudou ou é novo)

Pra cada contato do lote:

1. **Checar se está "Não lida" antes de abrir** (indicador visual na lista).
2. Abrir a conversa, ler o texto da página. Se for contato novo (nunca visto), rolar até o início da conversa pra achar a data da 1ª mensagem real — não confiar só na mensagem mais recente, ela pode não representar o motivo real de contato (relação longa pode ter deriva pra assunto totalmente diferente com o tempo, a raiz da conversa é onde a dor/desejo real costuma estar).
3. Classificar o novo Status:
   - **Ghost 1**: nunca respondeu, só 1 dia de tentativa sua.
   - **Ghost 2**: nunca respondeu, 2+ dias distintos de tentativa.
   - **Esperar**: já respondeu antes (diálogo real existiu), última mensagem foi sua há ≤48h.
   - **FUP**: já respondeu antes, última mensagem foi sua há >48h.
   - **Responder**: última mensagem é DELE, ainda sem sua resposta (o inverso de Esperar/FUP — o ponto não é ele estar quieto, é você estar devendo resposta).
   - **Convertida**: virou cliente (confirmado na aba de leads, ou evidência textual explícita na própria conversa — nunca por inferência, ver regra abaixo).
   - **Novo**: contato criado pelo sync do `crm-lead`, ainda não verificado no WhatsApp.
   - **Verificar**: dado insuficiente pra classificar com confiança (ex: só reação/figurinha, sem abrir o resto).
4. **Capturar Dores e Desejos**: só entra motivação REAL que levou o cliente a buscar o produto, nunca objeção pura (preço, dúvida) isolada — objeção vai pra aba Objeções (item 5 abaixo), não aqui. Se a fala citar sintoma/detalhe junto, incluir na frase literal, não resumir — frase literal é sempre a fala quase exata, nunca parafraseada. Preencher também **Categoria** (`config.CATEGORIAS`) — se a fala não couber bem em nenhuma categoria existente, marcar "Outro" e sinalizar pro usuário, pode virar categoria nova.
5. **Capturar Objeção**: resistência real do lead a avançar (preço, tempo, "já tentei outra coisa", ceticismo, timing pessoal) costuma aparecer mais adiante no diálogo, depois do D&D. Quando aparecer, registrar em Objeções: frase literal da objeção + a resposta que você de fato deu (não a resposta ideal, a real) + **Superada?** (mesma regra de nunca inferir do campo `Converteu?`: "Sim" só com confirmação explícita de que o lead seguiu em frente; "Não" só com confirmação explícita de que não seguiu; "Não sei" na ausência de sinal claro). Objeção nunca entra em Dores e Desejos, mesmo se envolver um sintoma junto (ex: "não tenho tempo com a ansiedade que eu tenho" é objeção de tempo com pista de dor — a dor, se ainda não capturada, também vira linha em D&D; a objeção em si vira linha separada em Objeções).
6. **Campo `Converteu?` — regra crítica**: só marcar "Sim" com confirmação explícita (a pessoa dizendo que comprou/pagou, ou o campo já confirmado na aba de leads). Sinal indireto forte (parcelamento discutido, relação longa, uso contínuo) NUNCA vira "Sim" — um campo binário não carrega nuance, e uma ressalva na Observação não corrige um "Sim" errado lido isoladamente por quem for analisar os dados depois. Na dúvida, "Não", e pergunte ao usuário antes de registrar qualquer suspeita de conversão.
7. **Restaurar "Não lida" IMEDIATAMENTE se estava assim antes de abrir** — fazer logo depois de ler cada conversa, nunca deixar pro fim do lote (se a rodada for interrompida no meio, o que já foi restaurado fica certo).

### 4. Dry-run antes de escrever

Mostrar pro usuário: linhas novas/atualizadas propostas pra FUP, linhas novas propostas pra Dores e Desejos, linhas novas propostas pra Objeções, e o que vai sincronizar de volta pra aba de leads. Só escrever após confirmação.

```python
from fup_update_rows import apply_updates
apply_updates([...])
```

```python
from dores_desejos_add_rows import add_rows
add_rows([...])
```

```python
from objecoes_add_rows import add_rows
add_rows([...])
```

### 5. Sync de volta pra aba de leads (mesmo padrão dry-run → confirmar → escrever)

```bash
python3 plan_sync_leads.py achados.json
python3 execute_sync_leads.py achados.json
```

Só preenche `Status CRM` pra quem está vazio (nunca sobrescreve valor humano), só quando o telefone bate com exatamente 1 linha na aba de leads (telefone duplicado = pula e avisa, resolver duplicata é trabalho do `crm-lead`).

### 6. Fechar com resumo

Quantos novos, quantos mudaram, distribuição de Status, quantas linhas novas em Dores e Desejos, quantas células sincronizadas de volta pra aba de leads. Confirmar que toda conversa aberta nesta rodada teve o "Não lida" original restaurado. Sem inventar número — só o que os scripts realmente reportaram.

## Banco de Copies — síntese pra uso direto em copy (opcional)

Aba separada, não populada automaticamente pelo fluxo principal — síntese exige leitura humana/IA pra agrupar por padrão, não só contagem de string. Editar `scripts/banco_copies_popular.py` (é um template, ROWS é exemplo) e rodar manualmente quando Dores e Desejos tiver crescido o suficiente pra valer revisão dos agrupamentos. Ver o docstring do arquivo pras regras de agrupamento (Categoria como eixo primário, "leads distintos" separado de "linhas", relato indireto nunca vira citação direta). Se você tiver um manual de hooks (`config.MANUAL_HOOKS_PATH`), aplicar a mecânica dele no campo "Hook sugerido" — hook forte é sensorial e específico, nunca frase que serviria pra qualquer pessoa em qualquer situação.

## Banco de Objeções — síntese pra estudo de argumentação de venda (opcional)

Aba separada, papel distinto de Banco de Copies: aquele existe pra gerar ideia de anúncio/conteúdo (hook), este existe pra estudar e melhorar a argumentação de venda 1:1. Mesma disciplina de Banco de Copies — não populada automaticamente, síntese exige leitura humana/IA. Rodar `scripts/banco_objecoes_criar_tab.py` uma vez pra criar a aba (só cabeçalho), depois popular manualmente (mesmo espírito de `banco_copies_popular.py` — adapte um script parecido) quando Objeções tiver massa real o suficiente pra generalizar um padrão.

**Schema**: `Categoria | Objeção padrão | Leads distintos | Fontes (linhas Objeções) | Caminho eficaz | Frase(s) de referência | Observação`.

**Regras de agrupamento:**
- "Caminho eficaz" só entra com base numa "Resposta dada" real registrada em Objeções que teve "Superada?" confirmado como Sim — nunca inventar o que "deveria" funcionar. Se o padrão se repete mas nenhuma resposta registrada teve confirmação de sucesso, deixar "Caminho eficaz" vazio e sinalizar na Observação (é lacuna real, não preencher por plausibilidade).
- "Leads distintos" é sempre o número de pessoas reais por trás do padrão, não de linhas — mesma regra de Banco de Copies.
- Se você mantém uma identidade de consumidor/framework de objeções documentado à parte (ex: objeções pré-mapeadas com argumentos prontos), este banco é o dado empírico que confirma ou corrige esse documento — comparar quando houver massa suficiente, sinalizar divergência ao usuário, nunca editar o documento original sozinho.

## Corner cases conhecidos

- **WhatsApp Web só sincroniza histórico recente.** Contato antigo pode ter 1ª mensagem inacessível — marcar `Verificar` com nota, nunca inventar data.
- **Contato renomeado** (ex: perdeu o marcador de busca do nome ao virar cliente): some da busca e a linha da FUP fica congelada no último estado conhecido. Sem detecção automática disso — se o usuário perceber, avisar e resolver manualmente.
- **Reação/figurinha sem texto**: conta como sinal de vida (não é Ghost), mas não dá dado suficiente pra Status completo sem abrir — cai em `Verificar` até alguém abrir de fato.
- **Contato de relacionamento/comunidade, não comercial** (gente próxima que tem o marcador de busca no nome por engano de convenção antiga): incluir na FUP igual, mas com nota clara na Observação pra não confundir com funil de vendas.

## Se faltar credencial ou o fluxo quebrar

Não tente recriar Service Account sozinho sem aprovação explícita — é infraestrutura que precisa confirmação antes de rodar. Avise o usuário e pare.
