# Karezma Bot

A Discord.py bot for the Karezma server.

## Included

- Slash commands (`/`)
- Automatic Friends role on member join
- Welcome embed + GIF
- `/test`
- `/clear`
- `/mute`
- `/unmute`
- `/ban`
- `/unban`
- `/lock`
- `/unlock`
- Owner-only secret role command
- Color-role commands

## Setup

1. Put the new Karezma server IDs and GIF URL in `config.py`.
2. Create a Discord bot application and invite it to Karezma with the required permissions.
3. Enable **Server Members Intent** and **Message Content Intent** in the Discord Developer Portal.
4. Set the Railway environment variable:

   `DISCORD_TOKEN=YOUR_BOT_TOKEN`

5. Deploy with the included `Procfile`.

Never put your Discord bot token in GitHub.
