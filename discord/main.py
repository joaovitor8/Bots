import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from services.nasa_api import close_session


logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("discord-bot")


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
  raise RuntimeError("DISCORD_TOKEN não definido no .env")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
  log.info("Bot %s online.", bot.user)
  log.info("-" * 54)


async def carregar_cogs():
  cogs_iniciais = ["cogs.comandos", "cogs.rotinas"]
  for cog in cogs_iniciais:
    try:
      await bot.load_extension(cog)
      log.info("Módulo carregado: %s", cog)
    except Exception as exc:
      log.exception("Erro ao carregar o módulo %s: %s", cog, exc)


async def main():
  async with bot:
    await carregar_cogs()
    try:
      await bot.start(TOKEN)
    finally:
      await close_session()


if __name__ == "__main__":
  asyncio.run(main())
