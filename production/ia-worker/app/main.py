import asyncio
import json

from fastapi import FastAPI, Form

from fastapi.middleware.cors import CORSMiddleware
import whisper
import ffmpeg
import io
import torchaudio
import ast



app = FastAPI()

# Ajouter le middleware CORS
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger le modèle Whisper
model = whisper.load_model("small")

# Stocker les messages SSE par client
clients = {}

# Créer une file d'attente pour les tâches de transcription
transcription_queue = asyncio.Queue()



@app.post("/transcribe")
async def receive_audio_chunk(
    chunk_id: str = Form(...)
):
    from redis_client import redis_factory_get
    from app_settings import app_settings_factory_get
    import msgpack
    app_settings = app_settings_factory_get()()
    redis_instance = redis_factory_get(app_settings.redis_host, app_settings.redis_port)()
    chunk_data = redis_instance.get_key(chunk_id)

    # Désérialisation avec MessagePack
    chunk = msgpack.unpackb(chunk_data, raw=False)

    content = io.BytesIO(chunk["content_bytes"])
    chunk_index = chunk["chunk_index"]
    client_id = chunk["client_id"]

    # Placer le chunk dans la file d'attente de transcription
    await transcription_queue.put((client_id, content, chunk_index))

    return {"status": "Chunk received"}


async def transcription_worker():
    while True:
        client_id, content, chunk_index = await transcription_queue.get()
        await transcribe_audio(client_id, content, chunk_index)
        transcription_queue.task_done()
        await asyncio.sleep(0.1)


@app.on_event("startup")
async def startup_event():
    # Démarrer le worker de transcription en arrière-plan
    asyncio.create_task(transcription_worker())


async def transcribe_audio(client_id, chunk_data, chunk_index):
    try:
        # Convertir le chunk en WAV
        input_stream = io.BytesIO(chunk_data)
        input_data = input_stream.read()

        loop = asyncio.get_event_loop()
        # Exécuter ffmpeg avec les paramètres appropriés dans un exécuteur
        out, err = await loop.run_in_executor(None, lambda: (
            ffmpeg
            .input('pipe:0')
            .output('pipe:1', format='wav', acodec='pcm_s16le', ac=1, ar='16k')
            .run(input=input_data, capture_stdout=True, capture_stderr=True, overwrite_output=True)
        ))

        # Placer les données de sortie dans un flux BytesIO
        output_stream = io.BytesIO(out)
        output_stream.seek(0)

        # Lire les données audio à partir du flux BytesIO
        waveform, sample_rate = torchaudio.load(output_stream)

        # Si nécessaire, rééchantillonner à 16000 Hz
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            waveform = resampler(waveform)

        # Convertir le tenseur en tableau NumPy
        audio_data = waveform.numpy().flatten()

        # Transcrire l'audio dans un exécuteur
        result = await loop.run_in_executor(None, lambda: model.transcribe(audio_data, fp16=False, language="fr"))

        # Envoyer la transcription via SSE en incluant chunk_index
        data = {
            "transcript": result['text'],
            "chunk_index": chunk_index
        }
        message = f"data: {json.dumps(data)}\n\n"
        print(f"Transcription: {message}")
        await send_sse_message(client_id, message, chunk_index)

    except Exception as e:
        print(f"Erreur lors de la transcription : {e}")
        # Impression de la stacktrace complète
        import traceback
        traceback.print_exc()


async def send_sse_message(client_id, message, chunk_index):
    from app_settings import app_settings_factory_get
    from http_service import http_service_factory_get
    data = {
        "client_id": client_id,
        "message": message,
        "chunk_index": chunk_index
    }
    json_data = json.dumps(data)
    app_settings = app_settings_factory_get()()
    http_service = http_service_factory_get()()
    await http_service.post(app_settings.url_slimfaas + "/publish-event/transcript", data=json_data, headers={"Content-Type": "application/json"})

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    from app_settings import app_settings_factory_get

    app_settings = app_settings_factory_get()()
    uvicorn.run(app, host=app_settings.server_host, port=app_settings.server_port)
