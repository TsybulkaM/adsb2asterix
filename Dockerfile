# Dockerfile
FROM python:3.11-slim

RUN pip install poetry

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY ./src/asterix_gateway /app/asterix_gateway

CMD ["poetry", "run", "python", "-m", "asterix_gateway.main"]
