# Proof Of Concept scale with Whisper
 
This project is a proof of concept to transcribe audio in real-time using a serverless architecture using: python, slimfaas, terraform, kubernetes on azure

## Getting Started


### Online

```shell

git clone https://github.com/guillaume-chervet/poc-whisper
cd poc-whisper
docker-compose up webapp
# open your browser at : http://localhost:4000/
# then copy/paste this baseUrl in the textfield: http://57.153.23.150/function/api

# webapp is available at http://20.8.16.190/ but it requires HTTPS to access the microphone
```

### With Docker Compose

```shell
git clone https://github.com/guillaume-chervet/poc-whisper
cd poc-whisper
cd production
docker-compose up
# open your browser at : http://localhost:4000/
# then copy/paste this baseUrl in the textfield: http://localhost:5020/function/api
```

# Architecture

![scenario slimfaas.png](documentation%2Fscenario%20slimfaas.png)

- **Step 1** : We split the audio into multiple chunks (each time there is a drop in intensity over a specified period).
- **Step 2** : We push the data into Redis with an ID, then make an asynchronous call to the worker (via a Queue). Only one instance of the AI-Worker will handle the processing.
- **Step 3** : We receive the ID that allows us to retrieve the data from Redis. We process the message and send an event to all instances of the front-end APIs.
- **Step 4** : The API instance connected to the web front-end returns the transcription.



# Roadmap
- [infrastructure] Configure a URL with HTTPS on Kubernetes
- [ia-worker] Set up GPU on Kubernetes
- [infrastructure] For scaling, add keda to scale from GPU consumption or queue length or wait Slimfaas to add this feature
- Set up Redis with high availability
- Set up Slimfaas with high availability
- Add monitoring
- Add alerting
- Add logging
- Add Tests
- [api] Manage cors policy
- [webapp] Manage CSP policy 
- [api] Manage rate limiting
- [api/webapp] Manage authentication and authorization
- [webapp] Send small chunks to the api while recording
- [all] Add retry pattern
- [train] Train / deploy / tests the model like explain in https://www.youtube.com/watch?v=QFOdB9GPf_Y&list=PL8EMdIH6Mzxw5mVb0hz4n7xeIa5aloVmC
- [deployment] Set up GitOps
