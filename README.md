# Video Processing Pipeline (Docker) — Downscale / Transcription / Subtitles / Animal Detection / S3 + DynamoDB

Architecture, des services isolés en Docker, une orchestration via docker-compose, la logique de traitement vidéo (downscale, extraction de langue/transcription, sous-titres, détection d’animaux), l’upload vers S3 et l’enregistrement des métadonnées dans DynamoDB

Ce projet fournit une pipeline modulaire pour traiter des vidéos :
- Downscale (MoviePy / ffmpeg)
- Transcription (Whisper)
- Génération de sous-titres (.srt)
- Détection d'animaux (YOLOv8)
- Upload des résultats sur Amazon S3 et stockage des métadonnées dans DynamoDB

Chaque fonction est empaquetée comme un *worker* en conteneur. Un service `api` orchestre le flux (uploader -> workers -> S3/DynamoDB).

---

## Pré-requis

- **Docker** & **Docker Compose**
- * **Python 3.10+**
* **AWS CLI** configuré
* **Terraform CLI** (pour le déploiement Cloud)
- Compte AWS + **S3 bucket** + **DynamoDB table** (nom mentionné dans `.env`)
- Pour une meilleure performance :
  - GPU recommandé pour Whisper et YOLO ; sinon CPU acceptable mais plus lent.

---

## Installation & exécution

1. Clone le repo
```bash
git clone <ton_repo>
cd video-pipeline
```
2. Copie .env.example en .env et remplir les valeurs AWS
```bash
cp .env.example .env
# puis édite .env
```

3. Lancer docker-compose
```bash
docker compose up --build
```

4. Uploader une vidéo (exemple en curl)
```bash
curl -F "file=@/chemin/vers/ma_video.mp4" http://localhost:8000/upload
```
La réponse JSON contiendra `job_id` et les métadonnées stockées dans DynamoDB. Les fichiers vidéo et `.srt` sont uploadés sur S3.

## Architecture & choix techniques

![Logo du projet](architecture-projet.jpeg)

- `Isolation des tâches`: chaque worker est un service indépendant exposant une endpoint REST simple `/process`. Cela permet scalabilité horizontale (kubernetes / ecs).

- `Stockage intermédiaire`: volume partagé `./data` monté sur tous les services  simple et efficace en local / VM.

- `Transcription`: Whisper  pour robustesse multi-langue. Sur GPU, utiliser `large/medium` pour meilleure qualité.

- `Detection d’objets`: Ultralytics YOLOv8 (poids `yolov8n` pour démarrer), filtrage sur labels animal courants.


- `S3 + DynamoDB`: stockage durable des assets + métadonnées (recherche, indexation).

- ![Logo du projet](cloud.png)


