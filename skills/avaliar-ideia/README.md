# Skill: /avaliar-ideia

Avaliador de ideias, ferramentas e skills de terceiros para o Claude Code.

**Status:** pronto.

---

## O que faz

Quando alguém compartilha uma ideia, ferramenta ou skill (slide, post de Reddit/X, link de repositório no GitHub, texto colado), essa skill avalia se vale a pena adotar em algum ponto do seu processo ou negócio.

Regras centrais:
- Sempre lê a fonte real (código-fonte de um repo, o link de verdade de um post) — nunca julga pela descrição ou pelo marketing. Se a fonte for hoax/clickbait, separa "funciona de verdade?" de "tem um mecanismo aproveitável por outro caminho?" em vez de descartar de cara.
- Processo em duas passadas na ordem certa: primeiro gera o leque completo de oportunidades cross-domain sem filtro (varrendo copy, revisão de texto, produto, vídeo, captação de cliente, páginas etc. — não só o domínio óbvio da fonte), só depois aplica risco/custo/corner cases — inverter a ordem poda ideia boa antes dela aparecer.
- Antes de propor integrar algo, mapeia sinergia e arquitetura contra o que já existe no projeto — paths explícitos, sem falar em abstrato — e pesa o custo de reinventar a roda contra adotar o que já está pronto.
- Risco sempre separado em três eixos (segurança/dados, jurídico/regulatório, ToS de plataforma) em vez de um "risco" genérico misturado, mais checagem de instalação/dependência de terceiro e aviso de qualquer custo (API ou uso elevado de tokens).
- Decisão de publicar em repositório público é separada e nunca automática — sempre com confirmação explícita antes do push.
- Termina em veredito por oportunidade: Adotar / Adaptar / Vigiar / Descartar.

## Como instalar

Copiar esta pasta para `.claude/skills/avaliar-ideia/` no seu projeto e invocar com `/avaliar-ideia` no Claude Code, colando o link, texto ou imagem a avaliar (o `user-invocable: true` no `SKILL.md` já registra o comando, sem precisar de wrapper em `.claude/commands/`).

## Configurar antes de usar

Nenhuma configuração obrigatória — a skill lê o contexto do produto/projeto ativo dinamicamente. Se quiser registrar ideias aprovadas em um backlog, criar um arquivo (ex: `Backlog/Ideias Avaliadas.md`) e ajustar o caminho na seção "Registro se aprovada" do `SKILL.md`.
