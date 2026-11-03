# Skill: /avaliar-telegram

Puxa a fila de um bot de Telegram (links, textos, áudios, vídeos, fotos e documentos compartilhados do celular) e avalia cada ideia com a skill `avaliar-ideia`, que precisa estar instalada ao lado.

## Setup

Compartilhe links, textos, áudios, vídeos e arquivos do celular para um bot de Telegram; `/avaliar-telegram` puxa e avalia tudo. O bot não precisa de servidor: o script lê o histórico do seu chat com ele pela user API (Telethon).

1. Criar o bot no @BotFather (`/newbot`) e mandar `/start` para ele
2. Criar credenciais em https://my.telegram.org (API ID e API hash)
3. `pip install telethon mlx-whisper` (mlx-whisper é Apple Silicon; em outra máquina, trocar a função `transcribe`); `ffmpeg` e `yt-dlp` no PATH
4. Criar `~/.config/avaliar-ideia-inbox/config`:
   ```
   TELEGRAM_API_ID=SEU_API_ID
   TELEGRAM_API_HASH=SEU_API_HASH
   BOT_USERNAME=seu_bot
   TELETHON_SESSION=/caminho/para/sessao   # sem .session; criada no 1º login
   INBOX_DIR=/caminho/para/inbox
   ```
5. Primeira execução: `python3 scripts/inbox_telegram.py` pede telefone e código do Telegram para criar a sessão
