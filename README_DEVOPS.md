# 🎬 Video AI Pipeline - DevOps Complete

## 🎯 Projet

Pipeline complète d'intelligence artificielle pour traitement vidéo:
1. **Downscale** - Compression FFmpeg
2. **Animal Detection** - YOLO11 
3. **Language Detection** - Speech Recognition
4. **Subtitles Generation** - Whisper AI
5. **Video Merger** ⭐ - Fusion vidéo + sous-titres

## ✨ Nouveau: 5ème Conteneur - Video Merger

Service innovant qui reçoit:
- Vidéo downscalée (MP4)
- Fichier VTT (sous-titres)

Et produit:
- Vidéo finale avec sous-titres intégrés (hardsub/softsub)

### Technologie
- **Base**: FFmpeg 6.0 + Python 3.11
- **Framework**: FastAPI
- **Fusion**: FFmpeg hardcoding + webvtt-py

## 🚀 Quick Start

### 1. Local (Docker Compose)
```bash
bash docker-deploy.sh start
# Accès: http://localhost:8000
```

### 2. Production (Kubernetes)
```bash
# Linux/Mac
kubectl apply -f k8s/01-namespace-configmap-pvc.yaml
kubectl apply -f k8s/02-services-deployments.yaml
kubectl apply -f k8s/03-api-gateway-ingress-hpa.yaml
kubectl apply -f k8s/04-orchestrator-webhook.yaml

# Windows PowerShell
.\k8s-deploy.ps1 -Action deploy
```

## 📊 Architecture

```
┌─────────────────────────────────────┐
│          INGRESS (Nginx)            │
│      video.yourdomain.com           │
└─────────────┬───────────────────────┘
              │
        ┌─────▼──────────┐
        │  API GATEWAY   │ (8000)
        └─────┬──────────┘
              │
    ┌─────────┴─────────┐
    │     WEBHOOK       │
    └─────────┬─────────┘
              │
    ┌─────────▼────────────────────┐
    │    ORCHESTRATOR (8006)       │
    │  Gère la pipeline entière    │
    └─────────┬────────────────────┘
              │
     ┌────────┴────────────────────────┐
     │                                 │
┌────▼────┐  ┌──────────┐  ┌─────────┐│
│DOWNSCALE│  │ ANIMAL   │  │LANGUAGE ││
│ (8003)  │  │DETECTOR  │  │DETECTOR ││
│FFmpeg   │  │(8001)    │  │(8002)   ││ Parallèle
└────┬────┘  └──────────┘  └─────────┘│
     │                                 │
     └────────────┬────────────────────┘
                  │
          ┌───────▼─────────┐
          │  SUBTITLES      │
          │  (8004)         │
          │  Whisper + VTT  │
          └───────┬─────────┘
                  │
          ┌───────▼──────────────────────────┐
          │  VIDEO MERGER ⭐ NOUVEAU (8005)  │
          │  Fusionne vidéo + subs           │
          │  Output: final_video.mp4         │
          └───────┬──────────────────────────┘
                  │
          ┌───────▼──────────────┐
          │ PERSISTENT STORAGE   │
          │ - Shared Data 100Gi  │
          │ - Outputs 50Gi       │
          │ - Redis 10Gi         │
          └──────────────────────┘
```

## 📦 Fichiers Clés

### Dockerfiles
- `Dockerfile.api` - API Gateway FastAPI
- `Dockerfile.animal-detector` - YOLO11 Detection
- `Dockerfile.language-detector` - Speech Recognition
- `Dockerfile.downscale` - FFmpeg Compression
- `Dockerfile.subtitles` - Whisper VTT Generation
- `Dockerfile.video-merger` ⭐ - Fusion Vidéo + Sous-titres

### Services Backend
- `backend/services/video_merger/` - 5ème service
  - `merger.py` - Logique fusion FFmpeg
  - `api.py` - Endpoints FastAPI
  - `requirements.txt` - Dépendances

### Kubernetes Manifests
- `k8s/01-namespace-configmap-pvc.yaml` - Configuration
- `k8s/02-services-deployments.yaml` - Pods + Services
- `k8s/03-api-gateway-ingress-hpa.yaml` - API + Ingress + Auto-scaling
- `k8s/04-orchestrator-webhook.yaml` - Orchestration

### Scripts Déploiement
- `docker-deploy.sh` - Orchestration Docker Compose (Bash)
- `k8s-deploy.ps1` - Orchestration Kubernetes (PowerShell)

### Documentation
- `DEVOPS_ARCHITECTURE.md` - Architecture détaillée
- `DEPLOYMENT_GUIDE.md` - Guide pas à pas
- `DEVOPS_SUMMARY.md` - Résumé complet

## 🔄 Flux de Traitement

### 1. Upload Vidéo
```
POST /video/upload
Content-Type: multipart/form-data
```

### 2. Orchestration Webhook Déclenche
```
Orchestrator lance pipeline:
├─ Downscale (FFmpeg)
├─ Animal Detection (YOLO11) [Parallèle]
├─ Language Detection (Speech) [Parallèle]
├─ Subtitles (Whisper)
└─ Video Merger (FFmpeg + VTT) [⭐ NOUVEAU]
```

### 3. Résultat Final
```json
{
  "task_id": "abc123",
  "status": "completed",
  "result": {
    "final_video": "/data/outputs/final_xxxxx.mp4",
    "animals": ["chat", "chien"],
    "language": "fr",
    "subtitles": "/data/outputs/video.vtt"
  }
}
```

## 🐳 Services Conteneurisés

| Service | Port | Base Image | Framework | Replicas |
|---------|------|-----------|-----------|----------|
| API Gateway | 8000 | python:3.11 | FastAPI | 3-10* |
| Animal Detector | 8001 | python:3.11 | FastAPI+YOLO | 2-8* |
| Language Detector | 8002 | ffmpeg:6.0 | FastAPI+Speech | 2-8* |
| Downscale | 8003 | ffmpeg:6.0 | FastAPI+FFmpeg | 2-6* |
| Subtitles | 8004 | ffmpeg:6.0 | FastAPI+Whisper | 2-6* |
| Video Merger | 8005 | ffmpeg:6.0 | FastAPI+FFmpeg | 2-6* |

*: Auto-scaling avec HPA

## 📈 Scaling Automatique

**Horizontal Pod Autoscaler (HPA)** activé par défaut:
```yaml
API Gateway:       3-10 pods   (CPU 70%)
Microservices:     2-8 pods    (CPU 75%)
```

## 🔒 Sécurité

- ✅ HTTPS/TLS (Let's Encrypt)
- ✅ Rate limiting (Nginx)
- ✅ CORS configuré
- ✅ Secrets management
- ✅ Resource limits
- ✅ Health checks
- ✅ Network policies (optionnel)

## 🛠️ Commandes Utiles

### Docker Compose
```bash
bash docker-deploy.sh start       # Démarrer
bash docker-deploy.sh stop        # Arrêter
bash docker-deploy.sh restart     # Redémarrer
bash docker-deploy.sh logs api    # Voir logs API
bash docker-deploy.sh test        # Tester upload
bash docker-deploy.sh status      # Statut containers
```

### Kubernetes
```bash
# Déployer
./k8s-deploy.ps1 -Action deploy

# Statut
./k8s-deploy.ps1 -Action status

# Logs
./k8s-deploy.ps1 -Action logs -Service video-merger

# Scaling
./k8s-deploy.ps1 -Action scale -Service video-merger -Replicas 5

# Redémarrer
./k8s-deploy.ps1 -Action restart -Service api-gateway
```

## 📚 Documentation Complète

1. **[DEVOPS_ARCHITECTURE.md](DEVOPS_ARCHITECTURE.md)** - Architecture détaillée avec diagrams
2. **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Guide pas à pas de déploiement
3. **[DEVOPS_SUMMARY.md](DEVOPS_SUMMARY.md)** - Résumé complet du projet

## 📞 Endpoints API

### Upload & Status
- `POST /video/upload` - Upload vidéo
- `GET /video/status/{file_id}` - Récupérer statut

### Video Merger ⭐
- `POST /video-merger/merge` - Fusionner vidéo + subs
- `POST /video-merger/webhook/merge` - Webhook orchestration
- `GET /video-merger/download/{filename}` - Télécharger résultat

### Orchestration
- `POST /orchestrate` - Lancer pipeline complète
- `GET /status/{task_id}` - Récupérer statut tâche

### Santé Services
- `GET /health` - Health check API
- `GET /animal-detector/health` - Health YOLO11
- `GET /language-detector/health` - Health Speech
- `GET /downscale/health` - Health FFmpeg
- `GET /subtitles/health` - Health Whisper
- `GET /video-merger/health` - Health Video Merger

## 🎓 Prérequis

### Local (Docker Compose)
- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 20GB disque libre

### Production (Kubernetes)
- Kubernetes 1.24+
- kubectl configuré
- Helm 3.0+ (optionnel)
- StorageClass configuré
- Domain registré

## 📋 Checklist Production

- [ ] Images Docker buildées
- [ ] Docker Compose testé localement
- [ ] Kubernetes cluster disponible
- [ ] Registry configuré
- [ ] Secrets créés
- [ ] StorageClass présent
- [ ] Ingress controller installé
- [ ] Let's Encrypt configuré
- [ ] Monitoring setup
- [ ] Logs centralisés
- [ ] Tests fonctionnels réussis
- [ ] Pipeline complète exécutée

## 🤝 Support

Pour plus d'informations:
1. Lire la documentation dans le répertoire `k8s/`
2. Consulter les logs: `kubectl logs -f deployment/xxx`
3. Port forward: `kubectl port-forward svc/api-gateway 8000:8000`

## 📝 Version

- **Version**: 1.0.0
- **Status**: ✅ Production Ready
- **Date**: Janvier 2026
- **DevOps Team**: Video AI Pipeline

---

**✨ Dockerisé. Orchestré. Scalable. Prêt pour la production.**
