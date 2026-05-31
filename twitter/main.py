import logging
import os

import requests
import tweepy
from deep_translator import GoogleTranslator
from dotenv import load_dotenv


logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("twitter-bot")


load_dotenv()


def _required_env(name: str) -> str:
  value = os.getenv(name)
  if not value:
    raise RuntimeError(f"Variável de ambiente obrigatória ausente: {name}")
  return value


API_KEY = _required_env("API_KEY")
API_SECRET = _required_env("API_SECRET")
ACCESS_TOKEN = _required_env("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = _required_env("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = _required_env("BEARER_TOKEN")
NASA_API_KEY = _required_env("NASA_API_KEY")

HTTP_TIMEOUT = 30
MAX_TWEET_LENGTH = 280


def fetch_nasa_apod() -> dict | None:
  url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
  try:
    response = requests.get(url, timeout=HTTP_TIMEOUT)
    response.raise_for_status()
  except requests.RequestException as exc:
    log.error("Falha ao consultar a NASA APOD: %s", exc)
    return None

  data = response.json()
  return {
    "title": data.get("title", "Astronomy Picture"),
    "date": data.get("date", ""),
    "url": data.get("url", ""),
    "copyright": data.get("copyright", ""),
    "media_type": data.get("media_type", "image"),
  }


def download_image(url: str, dest: str = "nasa_image.jpg") -> str | None:
  try:
    with requests.get(url, timeout=HTTP_TIMEOUT, stream=True) as response:
      response.raise_for_status()
      with open(dest, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
          file.write(chunk)
  except requests.RequestException as exc:
    log.error("Falha ao baixar imagem: %s", exc)
    return None
  return dest


def translate(text: str) -> str:
  if not text:
    return text
  try:
    return GoogleTranslator(source="en", target="pt").translate(text)
  except Exception as exc:
    log.warning("Falha ao traduzir, usando original: %s", exc)
    return text


def build_status(title_pt: str, date: str, copyright_: str) -> str:
  credit = f"\nCrédito: {copyright_.strip()}" if copyright_ else ""
  status = f"Foto Astronômica do Dia ({date})\n{title_pt}{credit}\n#NASA #space"
  if len(status) > MAX_TWEET_LENGTH:
    status = status[: MAX_TWEET_LENGTH - 1] + "…"
  return status


def post_to_twitter(status: str, image_path: str | None) -> None:
  client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
  )

  media_ids = None
  if image_path:
    auth = tweepy.OAuth1UserHandler(
      API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
    )
    api_v1 = tweepy.API(auth)
    media = api_v1.media_upload(filename=image_path)
    media_ids = [media.media_id]

  client.create_tweet(text=status, media_ids=media_ids)
  log.info("Tweet publicado com sucesso.")


def cleanup(path: str | None) -> None:
  if path and os.path.exists(path):
    os.remove(path)
    log.info("Arquivo local removido: %s", path)


def main() -> None:
  data = fetch_nasa_apod()
  if not data:
    return

  if data["media_type"] != "image":
    log.warning("APOD de hoje não é imagem (tipo=%s). Postando apenas o link.", data["media_type"])
    status = build_status(translate(data["title"]), data["date"], data["copyright"])
    post_to_twitter(f"{status}\n{data['url']}", None)
    return

  image_path = download_image(data["url"])
  status = build_status(translate(data["title"]), data["date"], data["copyright"])
  try:
    post_to_twitter(status, image_path)
  finally:
    cleanup(image_path)


if __name__ == "__main__":
  main()
