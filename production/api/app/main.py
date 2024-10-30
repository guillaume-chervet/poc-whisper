import asyncio
import json
import uuid

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import whisper
import ffmpeg
import io
import torchaudio
from pydantic import BaseModel

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

class Transcript(BaseModel):
    message:str
    chunk_index: int
    client_id:str

@app.post("/audio")
async def receive_audio_chunk(
    audio_chunk: UploadFile = File(...),
    chunk_index: int = Form(...),
    client_id: str = Form(...)
):
    if client_id not in clients:
        clients[client_id] = {
            "sse_messages": []
        }

    content = await audio_chunk.read()

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
        await send_sse_message(client_id, message)

    except Exception as e:
        print(f"Erreur lors de la transcription : {e}")
        # Impression de la stacktrace complète
        import traceback
        traceback.print_exc()


async def send_sse_message(client_id, message):
    if client_id in clients:
        clients[client_id]["sse_messages"].append(message)
    else:
        # Si le client n'est plus présent, ignorer le message
        print(f"Client {client_id} non trouvé pour envoyer le message.")


@app.get("/stream")
async def sse_endpoint(request: Request, client_id: str):
    print(f"Client {client_id} connected")

    if client_id not in clients:
        clients[client_id] = {
            "sse_messages": []
        }

    async def event_generator():
        try:
            # Tant que la connexion est active avec FastAPI
            while not await request.is_disconnected():
                client_data = clients.get(client_id)
                if client_data and client_data["sse_messages"]:

                    message = client_data["sse_messages"].pop(0)
                    print(f"Sending message to client {client_id} : {message}")
                    yield message
                else:
                    await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            print(f"Connexion interrompue par le client {client_id}.")
            return  # Sortie propre de la boucle lorsque le client se déconnecte

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "text/event-stream",
    }
    response = StreamingResponse(event_generator(), headers=headers, media_type="text/event-stream")
    # Ajouter les en-têtes CORS manuellement
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept'

    return response



@app.post("/transcript")
async def receive_transcript(transcript: Transcript):
    await send_sse_message(transcript.client_id, transcript.message)
    return {"status": "Transcript received"}


@app.post("/audio-queue")
async def receive_audio_chunk(
    audio_chunk: UploadFile = File(...),
    chunk_index: int = Form(...),
    client_id: str = Form(...)
):
    from redis_client import redis_factory_get
    from http_service import http_service_factory_get
    from app_settings import app_settings_factory_get
    if client_id not in clients:
        clients[client_id] = {
            "sse_messages": []
        }
    content = await audio_chunk.read()
    app_settings = app_settings_factory_get()()
    redis_instance = redis_factory_get(app_settings.redis_host, app_settings.redis_port)()
    chunk = {
        "content_bytes": content,
        "chunk_index": chunk_index,
        "client_id": client_id
    }
    # generate id
    chunk_id = str(uuid.uuid4())
    redis_instance.set_key(chunk_id, chunk)

    http_service = http_service_factory_get()()
    http_service.post( app_settings.url_slimfaas + "/async-function/ia-worker/transcribe", data={"chunk_id": chunk_id})

    return {"status": "Chunk received"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    from app_settings import app_settings_factory_get

    app_settings = app_settings_factory_get()()
    uvicorn.run(app, host=app_settings.server_host, port=app_settings.server_port)
