import logging
import os

import requests
import schedule
import time
from atproto import Client
from deep_translator import GoogleTranslator
from dotenv import load_dotenv


logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("bluesky-bot")


load_dotenv()


def _required_env(name: str) -> str:
  value = os.getenv(name)
  if not value:
    raise RuntimeError(f"Variável de ambiente obrigatória ausente: {name}")
  return value


BLUESKY_USERNAME = _required_env("BLUESKY_USERNAME")
BLUESKY_PASSWORD = _required_env("BLUESKY_PASSWORD")
API_NASA_KEY = _required_env("API_NASA_KEY")

HTTP_TIMEOUT = 30
HASHTAGS = "#astronomy  #science  #space  #universe  #cosmology  #astrophotos  #nasa"


def fetch_nasa_media_data(api_key: str) -> dict | None:
  try:
    response = requests.get(
      f"https://api.nasa.gov/planetary/apod?api_key={api_key}",
      timeout=HTTP_TIMEOUT,
    )
    response.raise_for_status()
  except requests.RequestException as exc:
    log.error("Falha ao obter dados da API da NASA: %s", exc)
    return None

  data = response.json()
  return {
    "copyright": data.get("copyright", ""),
    "date": data.get("date", ""),
    "url": data.get("url", ""),
    "title": data.get("title", "Astronomy Picture"),
    "media_type": data.get("media_type", "image"),
  }


def download_media(url: str) -> tuple[str | None, str | None]:
  media_type = "video" if url.endswith((".mp4", ".mov")) else "image"
  file_extension = ".mp4" if media_type == "video" else ".jpg"
  file_path = f"nasa_media{file_extension}"

  try:
    with requests.get(url, timeout=HTTP_TIMEOUT, stream=True) as response:
      response.raise_for_status()
      with open(file_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
          file.write(chunk)
  except requests.RequestException as exc:
    log.error("Falha ao baixar a mídia: %s", exc)
    return None, None

  log.info("%s baixado(a) com sucesso.", media_type.capitalize())
  return file_path, media_type


def upload_to_bluesky(
  username: str,
  password: str,
  title: str,
  date: str,
  copyright_: str,
  media_path: str,
  media_type: str,
) -> None:
  client = Client()
  client.login(username, password)

  with open(media_path, "rb") as media_file:
    media_data = media_file.read()

  try:
    translated_title = GoogleTranslator(source="en", target="pt").translate(title)
  except Exception as exc:
    log.warning("Falha ao traduzir título, usando original: %s", exc)
    translated_title = title

  credit_line = f"\n\nCrédito: {copyright_.replace(chr(10), '')}" if copyright_ else ""
  text = (
    f"Midia Astronômica do Dia: {date}\n\n"
    f"Título: {translated_title}"
    f"{credit_line}\n\n{HASHTAGS}"
  )

  if media_type == "image":
    client.send_image(text=text, image=media_data, image_alt=translated_title)
  elif media_type == "video":
    client.send_video(text=text, video=media_data, video_alt=translated_title)
  else:
    log.warning("Tipo de mídia '%s' não suportado, pulando upload.", media_type)
    return

  log.info("Mídia (%s) enviada com sucesso para o Bluesky.", media_type)


def delete_local_file(file_path: str) -> None:
  if os.path.exists(file_path):
    os.remove(file_path)
    log.info("Mídia local deletada.")
  else:
    log.warning("Arquivo local não encontrado: %s", file_path)


def main() -> None:
  media_data = fetch_nasa_media_data(API_NASA_KEY)
  if not media_data or not media_data["url"]:
    return

  media_path, media_type = download_media(media_data["url"])
  if not media_path:
    return

  try:
    upload_to_bluesky(
      BLUESKY_USERNAME,
      BLUESKY_PASSWORD,
      media_data["title"],
      media_data["date"],
      media_data["copyright"],
      media_path,
      media_type,
    )
  finally:
    delete_local_file(media_path)


if __name__ == "__main__":
  schedule_time = os.getenv("BLUESKY_SCHEDULE_TIME")
  if schedule_time:
    log.info("Agendado para rodar diariamente às %s.", schedule_time)
    schedule.every().day.at(schedule_time).do(main)
    while True:
      schedule.run_pending()
      time.sleep(60)
  else:
    main()
