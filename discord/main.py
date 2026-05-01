import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv


load_dotenv() # Isso puxa as informações do arquivo .env para a memória
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event # EVENTO DE INICIALIZAÇÃO
async def on_ready():
  print(f'Bot {bot.user} online')
  print('------------------------------------------------------')


# CARREGANDO AS ENGRENAGENS (COGS)
async def carregar_cogs():
  cogs_iniciais = [
    'cogs.comandos', # Vai carregar o arquivo cogs/comandos.py
    'cogs.rotinas'   # Vai carregar o arquivo cogs/rotinas.py
  ]
    
  for cog in cogs_iniciais:
    try:
      await bot.load_extension(cog)
      print(f'✅ Módulo carregado: {cog}')
    except Exception as e:
      print(f'❌ Erro ao carregar o módulo {cog}: {e}')


# FUNÇÃO PRINCIPAL QUE RODA TUDO
async def main():
  async with bot:
    # Primeiro ele carrega os módulos separados
    await carregar_cogs()
    # Depois ele liga de fato usando o Token seguro
    await bot.start(TOKEN)



if __name__ == '__main__':
  asyncio.run(main())

