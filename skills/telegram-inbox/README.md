# telegram-inbox

Infraestrutura comum para skills que recebem conteúdo do celular por um bot de Telegram (ex: `avaliar-telegram`). Não é uma skill invocável: é o script que coleta, transcreve, agrupa e enfileira.

- Um bot por finalidade, cada um com a própria pasta de config: `~/.config/telegram-inbox/<nome>/`
- Um item: cada mensagem, mais as respostas (reply) a ela, mesmo dias depois; álbum de fotos é um item só. Comentário ou instrução vai na mesma mensagem ou em resposta
- Transcrição sem loop (`condition_on_previous_text=False`) e com `alertas` no JSON quando parece incompleta (poucas palavras pro tempo de áudio, fim repetitivo)
- Lock da sessão Telethon: vários bots usam a mesma sessão; o script espera o próprio lock e os de `WAIT_LOCKS` (outros programas na mesma sessão)

## Setup

Compartilhe links, textos, áudios, vídeos e arquivos do celular para um bot de Telegram; `/avaliar-telegram` puxa e avalia tudo. O bot não precisa de servidor: o script lê o histórico do seu chat com ele pela user API (Telethon).

1. Criar o bot no @BotFather (`/newbot`) e mandar `/start` para ele
2. Criar credenciais em https://my.telegram.org (API ID e API hash)
3. `pip install telethon mlx-whisper` (mlx-whisper é Apple Silicon; em outra máquina, trocar a função `transcribe`); `ffmpeg` e `yt-dlp` no PATH
4. Criar `~/.config/telegram-inbox/<nome>/config`:
   ```
   TELEGRAM_API_ID=SEU_API_ID
   TELEGRAM_API_HASH=SEU_API_HASH
   BOT_USERNAME=seu_bot
   TELETHON_SESSION=/caminho/para/sessao   # sem .session; criada no 1º login
   INBOX_DIR=/caminho/para/inbox
   ```
5. Primeira execução: `python3 inbox_telegram.py --bot <nome>` pede telefone e código do Telegram para criar a sessão

Opcional no config: `WAIT_LOCKS=/caminho/outro.lock`
