FROM python:3.11-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates gnupg && rm -rf /var/lib/apt/lists/*
ENV POETRY_VERSION=1.8.4
RUN pip install "poetry==${POETRY_VERSION}"
WORKDIR /app
COPY . /app
RUN poetry config virtualenvs.create false && poetry install --no-root --only main

FROM python:3.11-slim
RUN useradd -ms /bin/bash appuser
# ffmpeg seulement en runtime
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --chown=appuser:appuser --from=build /app /app
USER appuser
ENV PATH="/usr/local/bin:${PATH}"
# Optionnel: pré‑download du modèle (peut rallonger le build)
RUN python -c "import whisper; whisper.load_model('small')"
CMD ["python", "./app/main.py"]
