

class AudioRecorder {
    constructor(options = {}) {
        this.audioContext = null;
        this.mediaRecorder = null;
        this.analyserNode = null;
        this.isRecording = false;
        this.silenceTimer = null;
        this.audioChunks = [];
        this.onStart = options.onStart || function() {};
        this.onStop = options.onStop || function() {};
        this.onDataAvailable = options.onDataAvailable || function() {};
        this.onError = options.onError || function() {};
        this.silenceDelay = options.silenceDelay || 200;
        this.speechThreshold = options.speechThreshold || 10;
        this.silenceThreshold = options.silenceThreshold || 2;

        // Nouvelle propriété pour contrôler la détection de la parole
        this.isDetectingSpeech = false;
        this.speechDetectionLoop = null;
    }

    init() {
        return navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const sourceNode = this.audioContext.createMediaStreamSource(stream);
                this.analyserNode = this.audioContext.createAnalyser();
                this.analyserNode.fftSize = 2048;
                sourceNode.connect(this.analyserNode);

                // Déterminer le type MIME pris en charge
                let options = null;
                if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
                    options = { mimeType: 'audio/webm;codecs=opus' };
                } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
                    options = { mimeType: 'audio/ogg;codecs=opus' };
                } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
                    options = { mimeType: 'audio/mp4' };
                } else {
                    console.error('Aucun type MIME pris en charge trouvé pour MediaRecorder.');
                    this.onError('Aucun type MIME pris en charge trouvé pour MediaRecorder.');
                    return;
                }

                this.mediaRecorder = new MediaRecorder(stream, options);

                this.mediaRecorder.ondataavailable = e => {
                    this.audioChunks.push(e.data);
                    this.onDataAvailable(e.data);
                };

                this.mediaRecorder.onstop = () => {
                    const mimeType = this.mediaRecorder.mimeType;
                    const audioBlob = new Blob(this.audioChunks, { type: mimeType });

                    this.audioChunks = [];
                    this.isRecording = false;
                    this.isDetectingSpeech = false;
                    this.onStop(audioBlob);
                    // Relancer la détection de la parole
                    this.detectSpeechStart();
                };

                this.detectSpeechStart();
            })
            .catch(err => {
                console.error('Erreur lors de l\'accès au microphone :', err);
                this.onError(err);
            });
    }

    detectSpeechStart() {
        if (this.isDetectingSpeech) return; // Empêcher les appels multiples
        this.isDetectingSpeech = true;

        const dataArray = new Uint8Array(this.analyserNode.fftSize);

        const checkSpeech = () => {
            this.analyserNode.getByteTimeDomainData(dataArray);

            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
                sum += Math.abs(dataArray[i] - 128);
            }
            const average = sum / dataArray.length;

            if (!this.isRecording && average > this.speechThreshold) {
                this.startRecording();
            } else if (!this.isRecording && this.isDetectingSpeech) {
                this.speechDetectionLoop = requestAnimationFrame(checkSpeech);
            } else {
                console.log('Pas d\'enregistrement, en attente de parole');
            }
        };

        checkSpeech();
    }

    stopSpeechDetection() {
        if (this.isDetectingSpeech) {
            this.isDetectingSpeech = false;
            if (this.speechDetectionLoop) {
                cancelAnimationFrame(this.speechDetectionLoop);
                this.speechDetectionLoop = null;
            }
        }
    }

    startRecording() {
        console.log('Démarrage de l\'enregistrement...');
        if (this.mediaRecorder && this.mediaRecorder.state === 'inactive') {
            this.mediaRecorder.start();
            this.isRecording = true;

            // Arrêter la détection de la parole pendant l'enregistrement
            this.stopSpeechDetection();

            this.monitorSilence();
            console.log('Enregistrement démarré');
            this.onStart();
        }
    }

    monitorSilence() {
        const dataArray = new Uint8Array(this.analyserNode.fftSize);

        const checkSilence = () => {
            this.analyserNode.getByteTimeDomainData(dataArray);

            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
                sum += Math.abs(dataArray[i] - 128);
            }
            const average = sum / dataArray.length;

            if (average < this.silenceThreshold) {
                if (!this.silenceTimer) {
                    this.silenceTimer = setTimeout(() => {
                        this.stopRecording();
                    }, this.silenceDelay);
                }
            } else {
                if (this.silenceTimer) {
                    clearTimeout(this.silenceTimer);
                    this.silenceTimer = null;
                }
            }

            if (this.isRecording) {
                requestAnimationFrame(checkSilence);
            }
        };

        checkSilence();
    }

    stopRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
            if (this.silenceTimer) {
                clearTimeout(this.silenceTimer);
                this.silenceTimer = null;
            }
            this.isRecording = false;
            console.log('Enregistrement arrêté');
        }
    }
    destroy() {
        this.stopSpeechDetection();
        this.stopRecording();
        if (this.mediaRecorder) {
            this.mediaRecorder.stop();
            this.mediaRecorder = null;
        }
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        // delete event
        this.onStart = () => {};
        this.onStop = () => {};
        this.onDataAvailable = () => {};
    }
}

export default AudioRecorder;
