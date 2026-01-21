# QUICK START - Démarrage Rapide

## 🚀 30 Secondes pour Démarrer

### Option 1: Docker Compose (Recommandé pour tester localement)

```bash
cd cloud
bash docker-deploy.sh start
```

**Accès immédiat:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Dashboard: http://localhost:8000/dashboard

### Option 2: Kubernetes (Production)

```bash
cd cloud
kubectl apply -f k8s/
```

**Accès:**
```bash
kubectl get ingress -n video-pipeline
# Puis accédez via le domaine configuré
```

## 📋 Ce Qui a Été Livré

### ✅ 5 Conteneurs Docker
1. **Animal Detector** (YOLO11)
2. **Language Detector** (Speech Recognition)
3. **Downscale** (FFmpeg)
4. **Subtitles** (Whisper)
5. **Video Merger** ⭐ **NOUVEAU** - Fusion vidéo + sous-titres

### ✅ Orchestration Complète

**Docker Compose** (Local)
- `docker-compose.yml` - Configuration 5 services + Redis + Nginx
- `nginx/nginx.conf` - Reverse proxy + Rate limiting
- `docker-deploy.sh` - Commandes deployment

**Kubernetes** (Production)
- `k8s/01-namespace-configmap-pvc.yaml` - Config centralisée
- `k8s/02-services-deployments.yaml` - Services + Deployments
- `k8s/03-api-gateway-ingress-hpa.yaml` - API + Ingress + Auto-scaling
- `k8s/04-orchestrator-webhook.yaml` - Orchestration webhook
- `k8s-deploy.ps1` - Script PowerShell pour K8s

### ✅ Services Backend

**Video Merger** (Nouveau)
- `backend/services/video_merger/merger.py` - Logique fusion FFmpeg
- `backend/services/video_merger/api.py` - Endpoints FastAPI
- `backend/services/video_merger/requirements.txt` - Dépendances

**Dockerfiles**
- `Dockerfile.api` - API Gateway
- `Dockerfile.animal-detector` - YOLO11
- `Dockerfile.language-detector` - Speech Rec
- `Dockerfile.downscale` - FFmpeg
- `Dockerfile.subtitles` - Whisper
- `Dockerfile.video-merger` - ⭐ Merger

### ✅ Documentation Complète

- `README_DEVOPS.md` - README principal
- `DEVOPS_ARCHITECTURE.md` - Architecture détaillée + diagrams
- `DEPLOYMENT_GUIDE.md` - Guide step-by-step
- `DEVOPS_SUMMARY.md` - Résumé complet

## 🎬 Architecture - Vue d'Ensemble

```
Upload Vidéo
    ↓
API Gateway (8000)
    ↓
Orchestrator Webhook
    ↓
[PARALLÈLE]
├─ Downscale (FFmpeg) 8003
├─ Animal Detect (YOLO11) 8001
└─ Language Detect (Speech) 8002
    ↓
Subtitles Generation (Whisper) 8004
    ↓
Video Merger ⭐ (FFmpeg + VTT) 8005
    ↓
Final Video with Subtitles
```

## 📊 Déploiement

### Ressources Requises

**Local (Docker Compose)**
- RAM: 8GB minimum
- Disk: 20GB minimum

**Production (Kubernetes)**
- Cluster 1.24+
- StorageClass disponible
- 3+ worker nodes pour HA

### Auto-Scaling Activé

- API Gateway: 3-10 pods
- Services: 2-8 pods chacun
- Basé sur CPU utilization (70-75%)

## 🔄 Flux Complet (Orchestration Automatique)

### 1. Upload Vidéo
```
POST /video/upload
```

### 2. Orchestrator Webhook Déclenche
```
Orchestrator lança pipeline séquentiellement:
1. Downscale ✓
2. Animal Detection + Language Detection (parallèle) ✓
3. Subtitles Generation ✓
4. Video Merger ✓
```

### 3. Récupérer Résultat
```
GET /status/{task_id}

Response:
{
  "status": "completed",
  "result": {
    "final_video": "/data/outputs/final_xxxxx.mp4",
    "animals": ["chat", "chien"],
    "language": "fr",
    "subtitles": "video.vtt"
  }
}
```

## 📞 Endpoints Clés

### Upload & Status
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/video/upload` | POST | Upload vidéo |
| `/video/status/{id}` | GET | Récupérer statut |
| `/dashboard` | GET | Interface web |

### Video Merger ⭐ (Nouveau)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/video-merger/merge` | POST | Fusionner vidéo + subs |
| `/video-merger/webhook/merge` | POST | Webhook orchestration |
| `/video-merger/download/{file}` | GET | Télécharger résultat |
| `/video-merger/health` | GET | Health check |

### Orchestration
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/orchestrate` | POST | Lancer pipeline |
| `/status/{task_id}` | GET | Récupérer statut tâche |

## 🐛 Troubleshooting Rapide

### Docker Compose Problème?
```bash
# Voir logs
bash docker-deploy.sh logs video-merger

# Redémarrer service
docker-compose restart video-merger

# Tout nettoyer
bash docker-deploy.sh clean
```

### Kubernetes Problème?
```bash
# Voir statut pods
kubectl get pods -n video-pipeline

# Voir logs
kubectl logs -f deployment/video-merger -n video-pipeline

# Port forward pour accès local
kubectl port-forward svc/api-gateway 8000:8000 -n video-pipeline
```

## ✨ Next Steps

1. **Tester Localement**
   ```bash
   bash docker-deploy.sh start
   bash docker-deploy.sh test
   ```

2. **Déployer en Production**
   ```bash
   ./k8s-deploy.ps1 -Action deploy
   ```

3. **Configurer Monitoring** (Optionnel)
   ```bash
   helm install prometheus prometheus-community/kube-prometheus-stack
   ```

4. **Lire la Documentation**
   - `DEVOPS_ARCHITECTURE.md` - Comprenez l'architecture
   - `DEPLOYMENT_GUIDE.md` - Suivez les étapes détaillées
   - `DEVOPS_SUMMARY.md` - Vue d'ensemble complète

## 🎉 Success Metrics

✅ **Architecture**
- 5 conteneurs Docker
- Orchestration Docker Compose
- Orchestration Kubernetes
- Auto-scaling HPA

✅ **Services**
- API Gateway
- Animal Detection
- Language Detection
- Downscale
- Subtitles Generation
- Video Merger ⭐

✅ **Features**
- Webhook orchestration
- Parallel processing
- Status tracking (Redis)
- Health checks
- Rate limiting
- CORS support
- HTTPS/TLS

✅ **Documentation**
- Architecture diagrams
- Deployment guides
- Kubernetes manifests
- Shell scripts
- PowerShell scripts

## 📞 Support

Pour des questions ou problèmes:

1. Vérifiez les logs: `bash docker-deploy.sh logs <service>`
2. Consultez la documentation: `DEVOPS_ARCHITECTURE.md`
3. Testez health: `curl http://localhost:8000/health`

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Date**: Janvier 2026
