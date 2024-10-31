import asyncio
import uuid

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
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

# Stocker les messages SSE par client
clients = {}

class Transcript(BaseModel):
    message:str
    chunk_index: int
    client_id:str

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


@app.post("/audio")
async def receive_audio_chunk(
    audio_chunk: UploadFile = File(...),
    chunk_index: int = Form(...),
    client_id: str = Form(...)
):
    from redis_client import redis_factory_get
    from http_service import http_service_factory_get
    from app_settings import app_settings_factory_get
    import msgpack
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
    # Sérialisation avec MessagePack
    chunk_packed = msgpack.packb(chunk, use_bin_type=True)
    redis_instance.set_key(chunk_id, chunk_packed)

    http_service = http_service_factory_get()()
    response = await http_service.post( app_settings.url_slimfaas + "/async-function/ia-worker/transcribe", data={"chunk_id": chunk_id})
    print("Reponse code: " + str(response.status_code))

    return {"status": "Chunk received"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    from app_settings import app_settings_factory_get

    app_settings = app_settings_factory_get()()
    uvicorn.run(app, host=app_settings.server_host, port=app_settings.server_port)
