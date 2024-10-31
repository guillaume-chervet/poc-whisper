# Première étape : Construire l'environnement avec les dépendances nécessaires
FROM python:3.11-slim AS build

# Installer Poetry
ENV POETRY_VERSION=1.8.4
RUN pip install "poetry==${POETRY_VERSION}"

# Configurer le dossier de travail
WORKDIR /app

# Copier uniquement les fichiers nécessaires pour installer les dépendances
COPY . /app

# Installer les dépendances sans les dev packages
RUN poetry config virtualenvs.create false && poetry install --no-root --only main

# Deuxième étape : Construire l'image finale allégée
FROM python:3.11-slim

# Créer l'utilisateur non-root
RUN useradd -ms /bin/bash appuser

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
