import discord
from discord.ext import commands, tasks
import aiohttp
import datetime


# Intents são as "permissões de visão" do bot. Aqui dizemos ao Discord o que o bot tem permissão de enxergar no servidor.
intents = discord.Intents.default()
intents.message_content = True # linha para ele ler os comandos!

# command_prefix='!' diz que, se formos criar comandos, eles começarão com '!'.
bot = commands.Bot(command_prefix='!', intents=intents)


# Aqui você vai colocar o ID do canal onde a imagem será postada.
CHANNEL_ID = 1499586625468895232
# A chave da API da NASA.
NASA_API_KEY = ""

url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"

fuso_horario_brasil = datetime.timezone(datetime.timedelta(hours=-3))
horario_postagem = datetime.time(hour=12, minute=00, second=0, tzinfo=fuso_horario_brasil)


# ----------


@bot.event
async def on_ready():
  print(f'🚀 Bot {bot.user} online e pronto para explorar o espaço!')
  postar_foto_nasa.start()


# ----------


# O @bot.command() avisa que a função abaixo é um comando do Discord
@bot.command()
async def galeria(ctx):
  await ctx.send('Pong! 🏓')


# ----------


# @tasks.loop diz ao bot: "repita o código abaixo a cada X tempo". No caso, 24 horas.
@tasks.loop(minutes=1)
async def postar_foto_nasa():
  canal = bot.get_channel(CHANNEL_ID)

  if not canal:
    print("Erro: Canal não encontrado. Verifique o CHANNEL_ID.")
    return  

  async with aiohttp.ClientSession() as session:
    # Aqui o bot "acessa" o site da NASA.
    async with session.get(url) as response:
        
      if response.status == 200:
        dados = await response.json() # Transformamos a resposta da NASA em um formato que o Python entende fácil (um dicionário).
        
        titulo = dados.get("title", "Foto Astronômica do Dia")
        imagem_url = dados.get("url", "")
        explicacao = dados.get("explanation", "")
        
        if len(explicacao) > 800:
          explicacao = explicacao[:800] + "... (texto encurtado pela NASA)"
        
        mensagem = f"🌌 **{titulo}**\n\n{explicacao}\n\n{imagem_url}"
        
        await canal.send(mensagem)
        
        print("Foto postada com sucesso!")
      
      else:
        print(f"Falha ao buscar a imagem. Status da NASA: {response.status}")

bot.run('')
