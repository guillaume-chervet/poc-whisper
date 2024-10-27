FROM python:3.11-slim

# Mettre à jour les paquets et installer les dépendances requises
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    software-properties-common

# Ajouter le dépôt LLVM pour obtenir la version la plus récente
RUN echo "deb http://apt.llvm.org/bookworm/ llvm-toolchain-bookworm main" > /etc/apt/sources.list.d/llvm.list && \
    wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - && \
    apt-get update && \
    apt-get install -y llvm

# Ajouter LLVM au PATH
ENV PATH="/usr/lib/llvm/bin:${PATH}"

# Installer ffmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg

# Nettoyer le cache pour réduire la taille de l'image
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Vérification de l'installation
RUN ffmpeg -version && llvm-config --version

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY . /app

EXPOSE 8002

RUN useradd -ms /bin/bash appuser
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
