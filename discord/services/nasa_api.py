import asyncio
import logging
import os

import aiohttp
from deep_translator import GoogleTranslator


log = logging.getLogger(__name__)

NASA_API_KEY = os.getenv("NASA_API_KEY")
APOD_URL = "https://api.nasa.gov/planetary/apod"
HTTP_TIMEOUT = aiohttp.ClientTimeout(total=30)
MAX_EXPLANATION_CHARS = 800

_translator = GoogleTranslator(source="en", target="pt")
_session: aiohttp.ClientSession | None = None


async def get_session() -> aiohttp.ClientSession:
  global _session
  if _session is None or _session.closed:
    _session = aiohttp.ClientSession(timeout=HTTP_TIMEOUT)
  return _session


async def close_session() -> None:
  global _session
  if _session and not _session.closed:
    await _session.close()
    _session = None


async def _translate(text: str) -> str:
  if not text:
    return text
  try:
    return await asyncio.to_thread(_translator.translate, text)
  except Exception as exc:
    log.warning("Falha ao traduzir, usando original: %s", exc)
    return text


async def buscar_foto_nasa(data_especifica: str | None = None) -> dict:
  if not NASA_API_KEY:
    return {"sucesso": False, "erro": "NASA_API_KEY não configurada."}

  params = {"api_key": NASA_API_KEY}
  if data_especifica:
    params["date"] = data_especifica

  try:
    session = await get_session()
    async with session.get(APOD_URL, params=params) as response:
      if response.status != 200:
        return {
          "sucesso": False,
          "erro": f"A API da NASA retornou o status {response.status}",
        }
      dados = await response.json()
  except aiohttp.ClientError as exc:
    return {"sucesso": False, "erro": f"Falha de conexão: {exc}"}

  titulo_pt = await _translate(dados.get("title", "Astronomy Picture"))
  explicacao_pt = await _translate(dados.get("explanation", ""))

  if len(explicacao_pt) > MAX_EXPLANATION_CHARS:
    explicacao_pt = explicacao_pt[:MAX_EXPLANATION_CHARS] + "... (texto encurtado)"

  return {
    "sucesso": True,
    "titulo": titulo_pt,
    "imagem_url": dados.get("url", ""),
    "explicacao": explicacao_pt,
    "media_type": dados.get("media_type", "image"),
  }
