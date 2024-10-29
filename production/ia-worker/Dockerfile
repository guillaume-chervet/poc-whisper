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

# Installer Poetry
RUN pip install poetry

# Configurer le dossier de travail
WORKDIR /app

# Copier uniquement les fichiers nécessaires pour installer les dépendances
COPY pyproject.toml poetry.lock /app/

# Installer les dépendances sans les dev packages
RUN poetry config virtualenvs.create false && poetry install --only main

# Deuxième étape : Construire l'image finale allégée
FROM python:3.11-slim

# Copier tous les exécutables installés de l'étape de build vers l'image finale
COPY --from=build /usr/local/bin /usr/local/bin

# Copier les packages Python installés
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copier le code de l'application
COPY --from=build /app /app

# Configurer le PATH pour inclure /usr/local/bin
ENV PATH="/usr/local/bin:${PATH}"

# Définir le dossier de travail
WORKDIR /app

# Créer et utiliser un utilisateur non-root
RUN useradd -ms /bin/bash appuser
USER appuser

# Commande pour démarrer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
