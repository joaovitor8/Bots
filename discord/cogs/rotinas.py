import discord
from discord.ext import commands, tasks
import datetime
import os
from dotenv import load_dotenv

from services.nasa_api import buscar_foto_nasa


class Rotinas(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
    load_dotenv()
    self.CHANNEL_ID = int(os.getenv('CHANNEL_ID_Imagem'))
    self.postar_foto_nasa.start()

  def cog_unload(self):
    # se o bot desligar ou recarregar, essa linha garante que o loop pare
    self.postar_foto_nasa.cancel()


  @tasks.loop(time=datetime.time(hour=9, minute=0, second=0))  # Configura para rodar todo dia às 9:00 da manhã
  async def postar_foto_nasa(self):
    canal = self.bot.get_channel(self.CHANNEL_ID)
    
    if not canal:
      print("❌ Erro na Rotina: Canal não encontrado. Verifique o CHANNEL_ID no seu .env.")
      return

    resultado = await buscar_foto_nasa()

    if resultado["sucesso"]:
      embed = discord.Embed(
        title=f"{resultado['titulo']}",
        description=resultado['explicacao'],
        color=0x9B59B6
      )
      embed.set_image(url=resultado['imagem_url'])
      embed.set_footer(text="Foto Astronômica do Dia • NASA APOD")

      await canal.send(embed=embed)
      print("✅ [Rotina Automática] Foto diária postada com sucesso!")

  @postar_foto_nasa.before_loop
  async def antes_do_loop(self):
    await self.bot.wait_until_ready()


async def setup(bot):
  await bot.add_cog(Rotinas(bot))

