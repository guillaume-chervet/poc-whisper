import React, {useContext, useEffect, useRef, useState} from 'react';
import AudioRecorder from './AudioRecorder.js';
import BaseUrlContext from "./BaseUrlContext.js"; // Ajustez le chemin si nécessaire

function generateColor(index) {
    return `hsl(${Math.sin(index) * 360}, 100%, 50%)`;
}

const sendAudioChunk= (baseUrl) => (chunk, clientId, chunkIndex) => {
    const formData = new FormData();
    formData.append('audio_chunk', chunk);
    formData.append('chunk_index', chunkIndex);
    formData.append('client_id', clientId);

    fetch(`${baseUrl}/audio-queue`, {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            console.error('Échec de l\'envoi du chunk audio :', response.statusText);
        }
    })
    .catch(err => {
        console.error('Erreur lors de l\'envoi du chunk audio :', err);
    });
}

const AudioRecorderComponent = ({}) => {
    const [status, setStatus] = useState('En attente de la parole...');
    const [isRecording, setIsRecording] = useState(false);
    const [error, setError] = useState(null);
    const [transcripts, setTranscripts] = useState([]);
    const [chunkIndex, setChunkIndex] = useState(0);
    const recorderRef = useRef(null);
    const eventSourceRef = useRef(null);
    const baseUrl = useContext(BaseUrlContext);

    useEffect(() => {
        console.log('Initialisation de l\'enregistreur audio');
        console.log('URL de base :', baseUrl);
        // Nettoyage des ressources précédentes
        if (recorderRef.current) {
            if (recorderRef.current.isRecording) {
                recorderRef.current.stopRecording();
            }
            if (recorderRef.current.audioContext) {
                recorderRef.current.audioContext.close();
            }
            recorderRef.current = null;
        }

        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }

        const clientId = Math.random().toString(36).substring(7);
        const eventSource = new EventSource(`${baseUrl}/stream?client_id=${clientId}`);
        eventSourceRef.current = eventSource;

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);

            setTranscripts((prev) => {
                if (prev.some(t => t.chunk_index === data.chunk_index)) {
                    return prev;
                }

                const updatedTranscripts = [...prev, data];
                console.log('Transcription reçue :', data.transcript);

                const ordered_transcripts = updatedTranscripts.sort((a, b) => a.chunk_index - b.chunk_index);
                return ordered_transcripts;
            });
        };

        eventSource.onerror = (err) => {
            console.error('Erreur SSE :', err);
            setError('Erreur de connexion avec le serveur.');
        };

        eventSource.onopen = () => {
            setError(null);
            console.log('Connexion SSE établie');
        };

        eventSource.onclose = () => {
            console.log('Connexion SSE fermée');
        };

        let closureChunkIndex = chunkIndex;

        const recorder = new AudioRecorder({
            onStart: () => {
                console.log('Enregistrement commencé (callback)');
                setIsRecording(true);
                setStatus('Enregistrement en cours...');
            },
            onStop: () => {
                console.log('Enregistrement terminé (callback)');
                setIsRecording(false);
                setStatus('En attente de la parole...');
            },
            onDataAvailable: (data) => {
                console.log('Enregistrement de données audio (callback)');
                setChunkIndex((prevIndex) =>{
                    closureChunkIndex++;
                    return prevIndex + 1;
                });
                sendAudioChunk(baseUrl)(data, clientId, closureChunkIndex);
            },
            onError: (err) => {
                console.error('Erreur de l\'enregistreur audio :', err);
                setError('Erreur lors de l\'accès au microphone.');
            },
            silenceDelay: 3000,
            speechThreshold: 10,
            silenceThreshold: 5,
        });

        recorderRef.current = recorder;
        recorder.init();

        return () => {
            if (recorderRef.current) {
                recorderRef.current.destroy();
                recorderRef.current = null;
            }
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
                eventSourceRef.current = null;
            }
        };
    }, [baseUrl]);

    return (
        <div>
            <h1>Enregistreur Audio avec Transcription en Temps Réel</h1>
            {error ? (
                <p style={{ color: 'red' }}>{error}</p>
            ) : (
                <p>{status}</p>
            )}
            <div>
                {chunkIndex > 0 && <h2>Transcription :</h2>}
                <p>{transcripts.map(t => (
                    <span key={t.chunk_index} style={{ color: generateColor(t.chunk_index) }}>
                        {t.transcript}
                    </span>
                ))}</p>
                {chunkIndex > transcripts.length && (
                    <p>Traitement de {chunkIndex - transcripts.length} chunk en cours...</p>
                )}
            </div>
        </div>
    );
};

export default AudioRecorderComponent;
