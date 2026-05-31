# bots

Coleção de bots que publicam a Astronomy Picture of the Day (APOD) da NASA em três redes diferentes.

| Bot       | Função                                                                                  |
|-----------|------------------------------------------------------------------------------------------|
| `bluesky` | Baixa a mídia da APOD e publica em uma conta do Bluesky (com tradução PT-BR).            |
| `discord` | Bot do Discord com rotina diária + comandos `!hoje` e `!data DD/MM/AAAA`.                |
| `twitter` | Publica a foto do dia no X/Twitter via API v2 (com fallback para link em caso de vídeo). |

Cada bot é independente: tem o próprio `.env`, `requirements.txt` e ponto de entrada.

## Setup geral

Pré-requisitos: Python 3.10+ e uma chave da [NASA API](https://api.nasa.gov).

```bash
cd <pasta-do-bot>
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
cp exemplo.env .env   # depois edite preenchendo as variáveis
python main.py
```

## Bluesky

Variáveis em `bluesky/exemplo.env`:
- `BLUESKY_USERNAME` / `BLUESKY_PASSWORD` — use uma [App Password](https://bsky.app/settings/app-passwords).
- `API_NASA_KEY` — chave da NASA.
- `BLUESKY_SCHEDULE_TIME` (opcional) — `HH:MM` para rodar diariamente. Vazio = roda uma vez e encerra.

## Discord

Variáveis em `discord/exemplo.env`:
- `DISCORD_TOKEN` — token do bot ([Discord Developer Portal](https://discord.com/developers/applications)).
- `NASA_API_KEY` — chave da NASA.
- `CHANNEL_ID_Imagem` — canal onde a rotina diária (09:00) publica.
- `CHANNEL_ID_Galeria` — canal autorizado para os comandos `!hoje` e `!data`.

Comandos disponíveis:
- `!hoje` — foto do dia.
- `!data DD/MM/AAAA` — foto de uma data específica.

## Twitter / X

Variáveis em `twitter/exemplo.env`:
- `API_KEY`, `API_SECRET`, `ACCESS_TOKEN`, `ACCESS_TOKEN_SECRET`, `BEARER_TOKEN` — credenciais OAuth do app (X Developer Portal).
- `NASA_API_KEY` — chave da NASA.

Observação: a API v2 do X exige plano **Basic** ou superior para publicar com mídia.

## Licença

MIT — ver [LICENSE](LICENSE).
