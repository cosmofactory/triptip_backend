FROM ubuntu:jammy

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    wget \
    libssl-dev \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    tk-dev \
    libgdbm-dev \
    libc6-dev \
    libbz2-dev \
    libffi-dev \
    git \
    liblzma-dev \
    uuid-dev

RUN wget https://www.python.org/ftp/python/3.12.2/Python-3.12.2.tgz \
    && mkdir -p /usr/src/python \
    && tar xzf Python-3.12.2.tgz -C /usr/src/python \
    && rm Python-3.12.2.tgz \
    && cd /usr/src/python/Python-3.12.2 \
    && ./configure --enable-optimizations \
    && make -j "$(nproc)" \
		LDFLAGS="-Wl,--strip-all" \
    && make install

RUN python3 --version \
    && pip3 --version

RUN pip3 install poetry==1.8.2 lockfile

WORKDIR /app

COPY pyproject.toml poetry.lock ./

ENV PATH="${PATH}:/root/.poetry/bin"

RUN set -ex; \
    poetry config --list && poetry install -vvv --no-interaction --no-dev

COPY . .

CMD ["poetry", "run", "gunicorn", "src.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", \
"--bind", "0.0.0.0:8000"]

