from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import aiohttp
import os


load_dotenv()
NASA_API_KEY = os.getenv('NASA_API_KEY')

# Criamos o nosso tradutor configurado: do inglês (en) para o português (pt)
tradutor = GoogleTranslator(source='en', target='pt')


async def buscar_foto_nasa(data_especifica=None):
  url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
  
  if data_especifica:
    url += f"&date={data_especifica}"
      
  async with aiohttp.ClientSession() as session:
    try:
      async with session.get(url) as response:
        if response.status == 200:
          dados = await response.json()
          
          # Pegamos os dados originais em inglês
          titulo_original = dados.get("title", "Astronomy Picture")
          explicacao_original = dados.get("explanation", "")
          imagem_url = dados.get("url", "")
          
          # --- A TRADUÇÃO ACONTECE AQUI ---
          # Traduzimos o título e a explicação
          titulo_pt = tradutor.translate(titulo_original)
          explicacao_pt = tradutor.translate(explicacao_original)
          # --------------------------------
          
          # Fazemos o corte de 800 caracteres no texto que já está em português
          if len(explicacao_pt) > 800:
            explicacao_pt = explicacao_pt[:800] + "... (texto encurtado)"
              
          # Devolvemos o pacote pronto, agora 100% em português
          return {
            "sucesso": True,
            "titulo": titulo_pt,
            "imagem_url": imagem_url,
            "explicacao": explicacao_pt
          }
        else:
          return {
            "sucesso": False, 
            "erro": f"A API da NASA retornou o status {response.status}"
          }
                
    except Exception as e:
      return {
        "sucesso": False, 
        "erro": f"Falha de conexão: {str(e)}"
      }

