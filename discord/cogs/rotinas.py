import datetime
import logging
import os

import discord
from discord.ext import commands, tasks

from services.nasa_api import buscar_foto_nasa


log = logging.getLogger(__name__)


class Rotinas(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    canal_id = os.getenv("CHANNEL_ID_Imagem")
    if not canal_id:
      raise RuntimeError("CHANNEL_ID_Imagem não definido no .env")
    self.CHANNEL_ID = int(canal_id)
    self.postar_foto_nasa.start()

  def cog_unload(self):
    self.postar_foto_nasa.cancel()

  @tasks.loop(time=datetime.time(hour=9, minute=0, second=0))
  async def postar_foto_nasa(self):
    canal = self.bot.get_channel(self.CHANNEL_ID)
    if not canal:
      log.error("Canal não encontrado (CHANNEL_ID=%s). Verifique o .env.", self.CHANNEL_ID)
      return

    resultado = await buscar_foto_nasa()
    if not resultado["sucesso"]:
      log.error("Falha na rotina: %s", resultado["erro"])
      await canal.send(f"⚠️ Não foi possível obter a foto de hoje: {resultado['erro']}")
      return

    embed = discord.Embed(
      title=resultado["titulo"],
      description=resultado["explicacao"],
      color=0x9B59B6,
    )
    if resultado.get("media_type") == "image" and resultado.get("imagem_url"):
      embed.set_image(url=resultado["imagem_url"])
    elif resultado.get("imagem_url"):
      embed.add_field(name="Mídia (vídeo)", value=resultado["imagem_url"], inline=False)
    embed.set_footer(text="Foto Astronômica do Dia • NASA APOD")

    await canal.send(embed=embed)
    log.info("Foto diária postada com sucesso.")

  @postar_foto_nasa.before_loop
  async def antes_do_loop(self):
    await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
  await bot.add_cog(Rotinas(bot))
