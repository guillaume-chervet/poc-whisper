# Première étape : Construire l'environnement avec les dépendances nécessaires
FROM python:3.11-slim AS build

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

# Installer ffmpeg
RUN apt-get install -y --no-install-recommends ffmpeg

# Trouver les chemins exacts des binaires et les stocker dans des variables d'environnement
RUN export LLVM_PATH=$(which llvm-config) && \
    export FFMPEG_PATH=$(which ffmpeg) && \
    echo "LLVM_PATH=${LLVM_PATH}" >> /etc/environment && \
    echo "FFMPEG_PATH=${FFMPEG_PATH}" >> /etc/environment

# Installer Poetry
RUN pip install poetry

# Configurer le dossier de travail
WORKDIR /app

# Copier uniquement les fichiers nécessaires pour installer les dépendances
COPY pyproject.toml poetry.lock /app/

# Installer les dépendances sans les dev packages
RUN poetry config virtualenvs.create false && poetry install --only main

# Stocker le chemin de uvicorn dans une variable d'environnement
RUN export UVICORN_PATH=$(which uvicorn) && echo "UVICORN_PATH=${UVICORN_PATH}" >> /etc/environment


# Deuxième étape : Construire l'image finale allégée
FROM python:3.11-slim

# Récupérer les chemins des binaires depuis l'étape de build
ARG LLVM_PATH
ARG FFMPEG_PATH
ARG UVICORN_PATH

# Copier les binaires en utilisant les chemins détectés
COPY --from=build ${UVICORN_PATH} /usr/local/bin/uvicorn
COPY --from=build ${LLVM_PATH} /usr/local/bin/llvm-config
COPY --from=build ${FFMPEG_PATH} /usr/local/bin/ffmpeg

# Copier l'environnement de l'application et ses dépendances
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /app /app

# Ajouter les binaires au PATH
ENV PATH="/usr/local/bin:${PATH}"

# Définir le dossier de travail
WORKDIR /app

# Créer et utiliser un utilisateur non-root
RUN useradd -ms /bin/bash appuser
USER appuser

# Exposer le port de l'application
EXPOSE 8002

# Commande pour démarrer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
