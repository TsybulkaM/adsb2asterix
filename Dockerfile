# Dockerfile
FROM python:3.11-slim

RUN pip install poetry

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY ./src/adsb-asterix-gateway /app/adsb-asterix-gateway

CMD ["poetry", "run", "python", "-m", "adsb-asterix-gateway.main"]