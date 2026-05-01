import discord
from discord.ext import commands
import datetime
import os
from dotenv import load_dotenv

from services.nasa_api import buscar_foto_nasa


class Comandos(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
    load_dotenv()
    self.CANAL_DE_COMANDOS_ID = int(os.getenv("CHANNEL_ID_Galeria"))

  @commands.command()
  async def galeria(self, ctx):
    await ctx.send('Pong! 🏓')

  @commands.command()
  async def data(self, ctx, data_digitada: str):
      
    if ctx.channel.id != self.CANAL_DE_COMANDOS_ID:
      await ctx.send(f"⚠️ Ei! Por favor, use os comandos de pesquisa lá no canal <#{self.CANAL_DE_COMANDOS_ID}>.")
      return

    async with ctx.typing():
      try:
        data_convertida = datetime.datetime.strptime(data_digitada, "%d/%m/%Y")
        data_nasa = data_convertida.strftime("%Y-%m-%d")
      except ValueError:
        await ctx.send("❌ Formato inválido! Por favor, use Dia/Mês/Ano. Exemplo: `!data 20/07/1969`")
        return

      resultado = await buscar_foto_nasa(data_especifica=data_nasa)

      if resultado["sucesso"]:
        embed = discord.Embed(
          title=f"{resultado['titulo']}", 
          description=resultado['explicacao'],
          color=0x9B59B6 
        )
        
        embed.set_image(url=resultado['imagem_url'])
        embed.set_footer(text=f"Data solicitada: {data_digitada} • NASA APOD API")

        await ctx.send(embed=embed)
      else:
        await ctx.send(f"⚠️ Poxa, não consegui pegar a imagem: {resultado['erro']}")

async def setup(bot):
  await bot.add_cog(Comandos(bot))

