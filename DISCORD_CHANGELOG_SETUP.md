# Configuração do Change-log do Discord

A página lê as publicações do arquivo `discord-changelog.json`. Esse arquivo é
atualizado pelo script `scripts/sync_discord_changelog.py` e nunca expõe o token
do bot no navegador.

## Configuração

1. Crie uma aplicação e um bot no Discord Developer Portal.
2. Ative o **Message Content Intent** do bot.
3. Adicione o bot ao servidor e permita **View Channel** e
   **Read Message History** no canal de change-logs.
4. No repositório GitHub, crie o secret `DISCORD_BOT_TOKEN` com o token do bot.
5. Em **Actions > General > Workflow permissions**, permita escrita no
   repositório para que a automação publique o JSON atualizado.

O workflow `.github/workflows/sync-discord-changelog.yml` verifica novas
publicações a cada 5 minutos e também pode ser executado manualmente.

Para sincronizar localmente:

```powershell
$env:DISCORD_BOT_TOKEN = "token-do-bot"
python scripts/sync_discord_changelog.py
```
