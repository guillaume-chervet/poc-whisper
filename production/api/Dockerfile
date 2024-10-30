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

# Installer Poetry
RUN pip install poetry

# Configurer le dossier de travail
WORKDIR /app

# Copier uniquement les fichiers nécessaires pour installer les dépendances
COPY . /app

# Installer les dépendances sans les dev packages
RUN poetry config virtualenvs.create false && poetry install --no-root --only main

# Stocker les chemins des binaires dans des fichiers temporaires
RUN which llvm-config > /llvm_path

# Deuxième étape : Construire l'image finale allégée
FROM python:3.11-slim

# Créer l'utilisateur non-root
RUN useradd -ms /bin/bash appuser

# Copier les chemins des binaires stockés dans des fichiers temporaires
COPY --from=build /llvm_path /ffmpeg_path /tmp/

# Charger les chemins des binaires depuis les fichiers temporaires en utilisant RUN pour définir les variables d’environnement
RUN export LLVM_PATH=$(cat /tmp/llvm_path)

COPY $LLVM_PATH /usr/local/bin/llvm-config

# Install ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg

# Copier les packages Python installés
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Donner les permissions appropriées pour l'utilisateur non-root
RUN chown -R appuser:appuser /usr/local/lib/python3.11/site-packages /usr/local/bin

# Définir le dossier de travail
WORKDIR /app

# Copier le code de l'application
COPY --chown=appuser:appuser --from=build /app /app

# Exécuter l'application en tant qu'utilisateur non-root
USER appuser

# Ajouter l'environnement virtuel au PATH
ENV PATH="/usr/local/bin:${PATH}"

# Commande pour démarrer l'application
CMD ["python", "./app/main.py"]
