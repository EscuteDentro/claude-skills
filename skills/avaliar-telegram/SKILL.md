---
name: avaliar-telegram
description: Puxa a fila do bot de Telegram (links do X/Instagram, textos, áudios, vídeos, fotos e documentos que o usuário compartilhou do celular) e avalia cada ideia com o método completo do /avaliar-ideia. Use quando o usuário digitar /avaliar-telegram ou pedir "puxa a caixa", "avalia o que mandei no Telegram".
user-invocable: true
---

# Avaliar Telegram

Coleta o que chegou no bot e aplica `../avaliar-ideia/SKILL.md` a cada ideia. O método de avaliação vive só lá; esta skill cuida de entrada, modelo e fila.

1. Ler `../avaliar-ideia/SKILL.md` inteiro antes de avaliar
2. Rodar `python3 scripts/inbox_telegram.py` (caminho relativo à pasta da skill): baixa mensagens novas e mídia, transcreve áudio/vídeo (`.transcript.txt`), gera contact sheet de vídeo (`.sheet.jpg`) e imprime a fila pendente em JSON
	- Fila vazia: dizer em 1 linha e encerrar
	- Mensagens com até 2 min de intervalo viram uma ideia só (link + comentário, álbum). Agrupamento é sugestão: separar assuntos sem relação, juntar repetidos
	- Comentário do usuário junto ("pensei pra landing page") aponta um encaixe a checar, nunca limita o leque da passada 1
3. Toda ideia recebe a avaliação completa, com a profundidade de um pedido direto. O que chegou é o ponto de partida; a fonte é o que ele aponta
	- Link: seção 0 do avaliar-ideia inteira (post do X com comentários, artigo, repo, documento ou ferramenta citada, vídeo do post baixado e transcrito)
	- Áudio, vídeo, foto ou documento mandado direto: ler transcrição, contact sheet e arquivo; vídeo sem fala, avaliar pelos frames
	- Reel/post de Instagram: `yt-dlp` sem cookies, nunca com sessão
	- Ideia falada (áudio sem link): a transcrição é a ideia; buscar se já existe ferramenta ou prática que a realiza
4. Modelo: avaliação é julgamento profundo, nunca tarefa operacional; roda no modelo mais capaz disponível, nunca num menor (perde profundidade)
	- Até 4 ideias: sessão principal avalia direto
	- 5+: 1 subagente por ideia, no mesmo modelo; brief com o SKILL.md do avaliar-ideia inteiro + itens da ideia + inventário do sistema; orquestrador confere e consolida. Avisar em 1 linha ao lançar que consome o limite do plano mais rápido
5. Resposta: formato de lote do avaliar-ideia (seção 4) com 3+ ideias, numerada pelo número da ideia na fila; registro no backlog segue a seção 5 de lá
6. Ao entregar: `inbox_telegram.py done ID ...` com as avaliadas. Config em `~/.config/avaliar-ideia-inbox/config`; setup no `README.md`
