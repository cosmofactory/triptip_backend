FROM python:3.12-slim

RUN pip3 install poetry==1.8.2 lockfile

WORKDIR /app

COPY pyproject.toml poetry.lock ./

ENV PATH="${PATH}:/root/.poetry/bin"

RUN set -ex; \
    poetry config --list && poetry install -vvv --no-interaction --no-dev

COPY . .
