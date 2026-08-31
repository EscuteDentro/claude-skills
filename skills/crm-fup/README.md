# crm-fup

CRM efetivo de recuperação de venda por WhatsApp: verifica status de conversa de cada lead marcado (Ghost/Esperar/FUP/Responder/Convertida), captura dor/desejo real ("Dores e Desejos") e objeção real ("Objeções") do cliente em abas vivas, e sincroniza com a aba de leads original. Skill irmã do `crm-lead` — reaproveita a mesma Sheet e credencial. Ver [SKILL.md](./SKILL.md) pra fluxo completo e regras de segurança.

## Pré-requisitos

- Python 3.9+
- Skill `crm-lead` instalado e configurado (mesma Sheet, mesma Service Account) — não é estritamente obrigatório, mas o sync de volta pra aba de leads (passo 5 do fluxo) depende dele existir.
- Contatos de lead salvos no WhatsApp/Contatos com um marcador de nome consistente (ex: "Lead", ou qualquer palavra que você use pra identificar esse grupo) — é esse marcador que o skill busca.

## Instalação

1. Copiar esta pasta inteira pra `.claude/skills/crm-fup/` no seu projeto.
2. Instalar as dependências Python:
   ```bash
   pip install -r scripts/requirements.txt
   ```
3. Copiar `scripts/config.example.py` pra `scripts/config.py`. Se já tem `crm-lead` instalado, reaproveite `SHEET_ID` e `SERVICE_ACCOUNT_KEY_PATH` do config dele — são os mesmos. Preencha as variáveis novas (nomes de aba, marcador de busca do WhatsApp, categorias).
4. Rodar uma vez, na instalação:
   ```bash
   python3 scripts/fup_criar_tab.py
   python3 scripts/dores_desejos_criar_tab.py
   python3 scripts/objecoes_criar_tab.py
   ```
5. Ferramentas de síntese opcionais, só se for usá-las: "Banco de Copies" (crie a aba manualmente, o script `banco_copies_popular.py` escreve nela mas não a cria sozinho) e "Banco de Objeções" (`python3 scripts/banco_objecoes_criar_tab.py` cria a aba vazia).

## Uso

Ver a seção "Fluxo ao rodar" no [SKILL.md](./SKILL.md). Peça ao Claude pra rodar o skill (`/crm-fup` se você criou um command apontando pro SKILL.md, ou só descrevendo o pedido na conversa). Todo script de escrita tem um passo de dry-run antes — nada escreve na Sheet sem você revisar primeiro.

**Este skill nunca envia mensagem.** Só lê o WhatsApp Web pra classificar status de conversa e capturar o que o cliente já disse. Ver "Regra absoluta" no SKILL.md.

## LGPD / privacidade

As abas "Dores e Desejos" e "Objeções" guardam fala real de cliente extraída de conversa de recuperação de venda — trate como dado sensível. Nome completo não é necessário pra rastreabilidade (telefone/Id bastam); considere anonimizar ainda mais se for compartilhar a Sheet com terceiros. Nunca automatiza contato em lote — todo re-contato continua manual, pelo próprio usuário.
