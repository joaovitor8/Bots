import datetime
import logging
import os

import discord
from discord.ext import commands

from services.nasa_api import buscar_foto_nasa


log = logging.getLogger(__name__)


class Comandos(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    canal_id = os.getenv("CHANNEL_ID_Galeria")
    if not canal_id:
      raise RuntimeError("CHANNEL_ID_Galeria não definido no .env")
    self.CANAL_DE_COMANDOS_ID = int(canal_id)

  def _montar_embed(self, resultado: dict, footer: str) -> discord.Embed:
    embed = discord.Embed(
      title=resultado["titulo"],
      description=resultado["explicacao"],
      color=0x9B59B6,
    )
    if resultado.get("media_type") == "image" and resultado.get("imagem_url"):
      embed.set_image(url=resultado["imagem_url"])
    elif resultado.get("imagem_url"):
      embed.add_field(name="Mídia (vídeo)", value=resultado["imagem_url"], inline=False)
    embed.set_footer(text=footer)
    return embed

  @commands.command()
  async def data(self, ctx: commands.Context, data_digitada: str):
    if ctx.channel.id != self.CANAL_DE_COMANDOS_ID:
      await ctx.send(
        f"⚠️ Ei! Por favor, use os comandos de pesquisa lá no canal <#{self.CANAL_DE_COMANDOS_ID}>."
      )
      return

    async with ctx.typing():
      try:
        data_convertida = datetime.datetime.strptime(data_digitada, "%d/%m/%Y")
        data_nasa = data_convertida.strftime("%Y-%m-%d")
      except ValueError:
        await ctx.send(
          "❌ Formato inválido! Use Dia/Mês/Ano. Exemplo: `!data 20/07/1969`"
        )
        return

      resultado = await buscar_foto_nasa(data_especifica=data_nasa)

      if resultado["sucesso"]:
        embed = self._montar_embed(
          resultado, f"Data solicitada: {data_digitada} • NASA APOD API"
        )
        await ctx.send(embed=embed)
      else:
        await ctx.send(f"⚠️ Poxa, não consegui pegar a imagem: {resultado['erro']}")

  @commands.command()
  async def hoje(self, ctx: commands.Context):
    """Mostra a foto astronômica do dia atual."""
    if ctx.channel.id != self.CANAL_DE_COMANDOS_ID:
      await ctx.send(
        f"⚠️ Use os comandos lá no canal <#{self.CANAL_DE_COMANDOS_ID}>."
      )
      return

    async with ctx.typing():
      resultado = await buscar_foto_nasa()
      if resultado["sucesso"]:
        embed = self._montar_embed(resultado, "Foto Astronômica do Dia • NASA APOD")
        await ctx.send(embed=embed)
      else:
        await ctx.send(f"⚠️ Falha ao buscar a foto: {resultado['erro']}")


async def setup(bot: commands.Bot):
  await bot.add_cog(Comandos(bot))
