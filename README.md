# Poc Whisper

Because I'm lacking of time, my **deliverable** is a **prompt** to use with ChatGPT o1 preview. You will be surprised by the result.

# Context

My context: I received the file on Wednesday afternoon while I was teaching a course at IG2I Lens (on MLOps). I got home, and my child had been vomiting all night. I took care of him on Thursday morning until his grandmother arrived to look after him. I then went to Cloud Nord to give a talk on SlimFaas and returned home. I’m getting married on Saturday, October 19, and I have a lot of preparations to make. I’m also teaching two afternoons next week in addition to my regular work, so I only have 1.5 hours available this Friday to work on the file (during my sick child’s nap time, whom I’m taking care of).

Last commit: I did not receive response to questions bellow (yet). So I choose the coolest use case, real time transcription with Whisper.

# Questions 

## Functional Questions:
- Where are the vendors located? Which countries or regions?
- Which languages they are speaking.
- Are users using a mobile phone through a specific application (web browser, WhatsApp, Discord, Teams, etc.)?
- How many calls do they make per day, and what is the average duration of these calls?
- Are there any load peaks at certain times? For example, are all calls made between 1 PM and 2 PM?
- Does the speech-to-text need to be in real-time? If not, how long after the call is the transcription expected?
- How many participants are in the conversations? Do we need to identify/differentiate them? If so, how do you identify the participants?
- Do you have an idea of the volume (in GB) of call data?
- Is there specific vocabulary that would require custom training of the Whisper model for the medical domain?
- Is it critical if conversations are lost during a system failure or crash?
- Do we need to implement a Feedback Loop at the API level, i.e., allowing the end user to correct the text?
- Can a user see other users' data or only their own?


## Technical Questions:
- What is your continuous integration stack? (Including plugins like Sonar, etc.)
- Which Cloud or On-Premise stack do you use?
- Do you use Kubernetes? And/or PaaS (Platform As A Service) services?
- What is your training platform or infrastructure?
- What are your security constraints for data storage and retention?
- Do you know of an annotation/labelling application for transcription? If so, which one?
- Which Message Queue component are we allowed to use?
- Which database are we allowed to use?
- What is your monitoring stack?
- Which tool do you use to detect data drift?
- How do you manage authentication? Via OpenID-Connect?
- Which languages the team can we use, code with? For exemple : Pyhton, dotnet, etc. 

# Production Architecture

With the use Keda whith prometeus to scale up. Use GitOps to deploy the architecture in production.

![scenario1.png](documentation%2Fscenario1.png)


![scenario2.png](documentation%2Fscenario2.png)
# Train Architecture

I would use architecture/workflow explained her https://www.youtube.com/watch?v=h7xqgl3cIQs&list=PL8EMdIH6MzxxyJM0iBvdY02ka1tvY0f4Y adpated to your architecture.

# My Starter Prompt (chatgpt o1 preview)

My first iteration is to use the chatgpt model to generate the code. I used the following prompt:

```
**Je souhaite mettre en place une architecture basée sur FastAPI, Kafka, et Whisper pour un service de transcription audio en temps réel. Voici le scénario complet :**
1.	Un client (navigateur) envoie un fichier audio .wav découpé en chunks via une connexion WebSocket à une API FastAPI. Utilise Poetry pour la gestion des dépendences. Le script doit être dans un dossier "/production/api".
2.	FastAPI reçoit ces chunks audio, génère un identifiant unique pour chaque fichier .wav, et envoie chaque chunk dans un topic Kafka (audio_chunks). Chaque message Kafka doit contenir les données audio ainsi qu'un identifiant unique pour le fichier audio et la connexion WebSocket ainsi qu'un identifiant ClientId.
3.	Un consommateur Kafka (écrit dans un script Python séparé et utilise Poetry pour la gestion des dépendences.) écoute le topic Kafka audio_chunks, traite les chunks audio avec le modèle Whisper pour générer la transcription en temps réel, et publie la transcription dans un autre topic Kafka (transcriptions). Chaque message doit contenir l'identifiant de la connexion WebSocket d'origine ainsi que la transcription générée. Le script doit être dans un dossier "/production/worker-ia".
4.	FastAPI doit aussi être un consommateur Kafka : il écoute le topic transcriptions, récupère les transcriptions, et les renvoie au client d'origine via la connexion WebSocket existante (basée sur l'identifiant WebSocket initial).
5.  Un consommateur Kafka (écrit dans un script Python séparé et utilise Poetry pour la gestion des dépendences.) qui écoute le topic des transcriptions et les stocke dans une base de données (PostgreSQL) en fonction du SessionID et ClientID provenant de l'API. Le script doit être dans un dossier "/production/worker-database".

**Je voudrais un code complet qui montre comment :**
•	Mettre en place l'API FastAPI qui gère les connexions WebSocket et envoie les chunks à Kafka (en python 3.11).
•	Mettre en place le consommateur Kafka qui utilise Whisper pour traiter les chunks audio et produire les transcriptions (en python 3.11).
•	Écouter Kafka dans FastAPI pour récupérer les transcriptions et les renvoyer au client via WebSocket.

N'oubliez pas d'inclure les tâches asynchrones nécessaires pour écouter Kafka dans FastAPI et garantir que les connexions WebSocket restent ouvertes.
Fournissez-moi un exemple complet, avec le code des deux parties (FastAPI et le consommateur Kafka Whisper).

**Je souhaite déployer cette architecture sur Kubernetes de façon automatique depuis une github action (il faut utiliser le gestionnaire de conteneur de github), je dispose d'un user et secret SPN azure avec un rôle contributeur sur toute la souscription**
1. Je veux un script terraform pour deployer un Kubernetes sur Azure avec des machines GPU. Ce script doit être dans un dossier "deploy".
2. Je veux un fichier dockerfile pour chaque partie de l'architecture (FastAPI et Whisper et Sauvegarde en base de donnée). Optimisez-les pour qu'il soit sécurisé (créer un user non root qui a uniqement des droits d'éxécutions sur l'application) et que l'image soit la plus petite possible (utilise des multi-stages). N'oublie pas que le worker doit avoir un driver GPU nvidia à jour. 
3. Je veux un fichier docker-compose pour lancer l'architecture complète en local. Il doit être dans le dossier "production".
4. je veux le script Github Action dans le dossier ".github/workflows" qui permet de déployer l'architecture sur Kubernetes. Vous pouvez utiliser les secrets Github pour stocker les secrets Azure.
````