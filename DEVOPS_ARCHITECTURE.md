# 🚀 ARCHITECTURE DevOps - Video Processing Pipeline

## 📊 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                       INGRESS (Nginx/HAProxy)                   │
│                    video.yourdomain.com                          │
└────────────┬────────────────────────────────────────────────────┘
             │
    ┌────────┴─────────┐
    │                  │
┌───▼────────────┐   ┌─────────────────────┐
│  API GATEWAY   │   │   Load Balancer     │
│  (FastAPI)     │   │   (Horizontal)      │
└───┬────────────┘   └─────────────────────┘
    │
    │  ORCHESTRATION WEBHOOK
    │
┌───▼─────────────────────────────────────────┐
│         ORCHESTRATOR (8006)                  │
│   - Gère la pipeline entière                │
│   - Utilise Redis pour tracker l'état       │
│   - Déclenchement asynchrone                │
└───┬──────────────────────────────────────────┘
    │
    ├─────────────────────────────────────────────────────┐
    │                                                     │
┌───▼────────────┐  ┌───────────────┐  ┌──────────────┐
│  DOWNSCALE (8003)  │  LANGUAGE     │  │   ANIMAL    │
│  (FFmpeg)          │  DETECTOR(8002)  │  DETECTOR(8001)
│  Parallèle       │  Parallèle      │  │  Parallèle   │
└───┬────────────┘  └───────────────┘  └──────────────┘
    │
┌───▼─────────────────┐
│  SUBTITLES (8004)   │
│  (Whisper + VTT)    │
└───┬─────────────────┘
    │
┌───▼──────────────────────────────────┐
│  VIDEO MERGER (8005) ⭐ NOUVEAU      │
│  Fusionne vidéo + sous-titres       │
│  Génère fichier final avec subs     │
└───┬──────────────────────────────────┘
    │
┌───▼──────────────────────────────────────┐
│  STOCKAGE PERSISTENT                     │
│  - PVC: Shared Data                      │
│  - PVC: Merger Outputs                   │
│  - Redis Cache                           │
└──────────────────────────────────────────┘
```

## 🐳 5 CONTENEURS DOCKER

### 1️⃣ **Animal Detector** (Port 8001)
- **Base**: `python:3.11-slim`
- **Framework**: FastAPI + YOLO11
- **Entrée**: Vidéo MP4
- **Sortie**: JSON avec détections d'animaux
- **Ressources**: 2Gi RAM, 1-2 CPU

### 2️⃣ **Language Detector** (Port 8002)
- **Base**: `jrottenberg/ffmpeg:6.0-ubuntu2204`
- **Framework**: FastAPI + SpeechRecognition
- **Entrée**: Vidéo MP4
- **Sortie**: Code langue détecté
- **Ressources**: 2Gi RAM, 1-2 CPU

### 3️⃣ **Downscale** (Port 8003)
- **Base**: `jrottenberg/ffmpeg:6.0-ubuntu2204`
- **Framework**: FastAPI + FFmpeg
- **Entrée**: Vidéo originale
- **Sortie**: Vidéo downscalée (1080p max)
- **Ressources**: 1Gi RAM, 500m-1 CPU

### 4️⃣ **Subtitles** (Port 8004)
- **Base**: `jrottenberg/ffmpeg:6.0-ubuntu2204`
- **Framework**: FastAPI + Whisper
- **Entrée**: Vidéo downscalée
- **Sortie**: Fichier VTT
- **Ressources**: 2Gi RAM, 1-2 CPU

### 5️⃣ **Video Merger** ⭐ **NOUVEAU** (Port 8005)
- **Base**: `jrottenberg/ffmpeg:6.0-ubuntu2204`
- **Framework**: FastAPI + FFmpeg
- **Entrée**: Vidéo downscalée + VTT
- **Sortie**: Vidéo avec sous-titres intégrés
- **Ressources**: 1Gi RAM, 500m-1 CPU
- **Fonctionnalité**: Fusion hardsub ou softsub

## ⚙️ ORCHESTRATION

### Docker Compose (Local)
```bash
docker-compose up -d
```
- Tous les services s'exécutent localement
- Redis pour gestion des tâches
- Nginx reverse proxy

### Kubernetes (Production)
```bash
# Déployer namespace + config
kubectl apply -f k8s/01-namespace-configmap-pvc.yaml

# Déployer services + deployments
kubectl apply -f k8s/02-services-deployments.yaml

# Déployer API Gateway + Ingress + HPA
kubectl apply -f k8s/03-api-gateway-ingress-hpa.yaml

# Déployer Orchestrator
kubectl apply -f k8s/04-orchestrator-webhook.yaml
```

## 🔄 FLUX DE TRAITEMENT

### 1. Upload Vidéo
```
POST /video/upload
Content-Type: multipart/form-data
- file: video.mp4
```

### 2. Orchestration Déclenche
```
API Gateway →  Orchestrator Webhook
session_id: uuid
video_id: uuid
video_path: /data/uploads/video_xxxxx.mp4
```

### 3. Exécution Pipeline
```
[PARALLÈLE]
├─ Downscale (FFmpeg)
├─ Language Detection (Whisper)
└─ Animal Detection (YOLO11)
│
[SÉQUENTIEL]
├─ Subtitles Generation (Whisper + VTT)
└─ Video Merger (FFmpeg + Subs)
│
[RÉSULTAT]
Final Video: /data/outputs/final_xxxxx.mp4
```

### 4. Statut Tracking
```
GET /status/{task_id}

Response:
{
  "task_id": "abc12345",
  "status": "completed",
  "stages": {
    "downscale": {"status": "completed", "progress": 100},
    "language_detection": {"status": "completed", "progress": 100},
    "animal_detection": {"status": "completed", "progress": 100},
    "subtitles": {"status": "completed", "progress": 100},
    "merger": {"status": "completed", "progress": 100}
  },
  "result": {
    "final_video": "/data/outputs/final_xxxxx.mp4",
    "language": "fr",
    "animals_detected": ["chat", "chien"],
    "subtitles": "/data/final_xxxxx.vtt"
  }
}
```

## 📦 KUBERNETES MANIFESTS

### Structure des Fichiers
```
k8s/
├── 01-namespace-configmap-pvc.yaml      # Namespace + Config centralisée
├── 02-services-deployments.yaml         # Services + Deployments (Redis + 4 services)
├── 03-api-gateway-ingress-hpa.yaml      # API + Ingress + Auto-scaling
└── 04-orchestrator-webhook.yaml         # Orchestrator + Pipeline Controller
```

### Composants Kubernetes

**1. Namespace**: `video-pipeline`

**2. PersistentVolumes**:
- `shared-data-pvc`: 100Gi (partagé entre tous les services)
- `merger-outputs-pvc`: 50Gi (vidéos finales)
- `redis-data-pvc`: 10Gi (cache Redis)

**3. ConfigMap**: Variables centralisées
```yaml
PYTHONUNBUFFERED: 1
LOG_LEVEL: INFO
DEVICE: cpu (ou cuda pour GPU)
PROCESSING_TIMEOUT: 1800
```

**4. Secrets**: Credentials
```yaml
REDIS_PASSWORD: xxxxx
DATABASE_URL: xxxxx
API_KEY: xxxxx
```

**5. Deployments** (avec 2-3 replicas chacun):
- `api-gateway` (3 replicas)
- `redis` (1 replica)
- `animal-detector` (2 replicas)
- `language-detector` (2 replicas)
- `downscale` (2 replicas)
- `subtitles` (2 replicas)
- `video-merger` (2 replicas)
- `orchestrator` (2 replicas)

**6. Services** (ClusterIP pour communication interne):
- Chaque Pod expose son service interne

**7. Ingress** (Accès externe):
- `video-pipeline-ingress`: video.yourdomain.com
- Rate limiting: 10req/s API, 2req/s upload
- HTTPS avec Let's Encrypt

**8. HorizontalPodAutoscaler (HPA)**:
- API Gateway: 3-10 replicas (CPU 70%, Mémoire 80%)
- Microservices: 2-8 replicas (CPU 75%)

## 📈 SCALING & PERFORMANCE

### Horizontal Scaling
```bash
# Vérifier HPA
kubectl get hpa -n video-pipeline

# Scales automatiquement selon:
- CPU utilization
- Memory utilization
- Custom metrics (optionnel)
```

### Ressources Par Service
```
API Gateway:        512Mi → 1Gi    | 250m → 500m
Animal Detector:    2Gi            | 1 → 2 CPU
Language Detector:  2Gi            | 1 → 2 CPU
Downscale:          1Gi            | 500m → 1 CPU
Subtitles:          2Gi            | 1 → 2 CPU
Video Merger:       1Gi            | 500m → 1 CPU
Redis:              256Mi          | 100m
Orchestrator:       256Mi          | 100m
```

## 🔐 SÉCURITÉ

### Network Policies (Optionnel)
```yaml
# Isoler les services
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

### RBAC
```bash
# Service Account avec permissions minimales
kubectl apply -f rbac.yaml
```

### Secrets Management
```bash
# Utiliser Sealed Secrets ou HashiCorp Vault
kubectl create secret generic video-pipeline-secrets \
  --from-literal=REDIS_PASSWORD=xxxxx \
  --namespace=video-pipeline
```

## 📝 COMMANDES KUBERNETES

### Deployment
```bash
# Créer namespace
kubectl create namespace video-pipeline

# Déployer tout
kubectl apply -f k8s/ -n video-pipeline

# Vérifier status
kubectl get all -n video-pipeline
kubectl get pvc -n video-pipeline
kubectl get ingress -n video-pipeline
```

### Logs & Monitoring
```bash
# Logs API Gateway
kubectl logs -f deployment/api-gateway -n video-pipeline

# Logs tous les services
kubectl logs -f deployment/animal-detector -n video-pipeline
kubectl logs -f deployment/downscale -n video-pipeline
kubectl logs -f deployment/subtitles -n video-pipeline
kubectl logs -f deployment/video-merger -n video-pipeline

# Monitoring en temps réel
kubectl top pods -n video-pipeline
kubectl top nodes
```

### Debugging
```bash
# Port forward pour accès local
kubectl port-forward svc/api-gateway 8000:8000 -n video-pipeline
kubectl port-forward svc/orchestrator 8006:8006 -n video-pipeline

# Exec dans un pod
kubectl exec -it pod/api-gateway-xxxxx -n video-pipeline -- bash

# Vérifier les events
kubectl describe pod pod-name -n video-pipeline
```

### Scaling Manuel
```bash
# Scaler un deployment
kubectl scale deployment animal-detector --replicas=5 -n video-pipeline

# Vérifier HPA
kubectl get hpa -n video-pipeline -w
```

## 🚢 CI/CD PIPELINE

### GitLab CI / GitHub Actions
```yaml
stages:
  - build
  - test
  - push
  - deploy

build_images:
  stage: build
  script:
    - docker build -t video-pipeline/animal-detector:latest -f Dockerfile.animal-detector .
    - docker build -t video-pipeline/language-detector:latest -f Dockerfile.language-detector .
    - docker build -t video-pipeline/downscale:latest -f Dockerfile.downscale .
    - docker build -t video-pipeline/subtitles:latest -f Dockerfile.subtitles .
    - docker build -t video-pipeline/video-merger:latest -f Dockerfile.video-merger .

push_registry:
  stage: push
  script:
    - docker push video-pipeline/animal-detector:latest
    - docker push video-pipeline/language-detector:latest
    - docker push video-pipeline/downscale:latest
    - docker push video-pipeline/subtitles:latest
    - docker push video-pipeline/video-merger:latest

deploy_k8s:
  stage: deploy
  script:
    - kubectl apply -f k8s/ -n video-pipeline
    - kubectl rollout status deployment/api-gateway -n video-pipeline
```

## 📊 MONITORING & LOGGING

### Prometheus + Grafana
```bash
# Installer Prometheus Operator
helm install prometheus prometheus-community/kube-prometheus-stack -n video-pipeline

# Dashboards:
- CPU/Memory usage
- Request rate
- Error rate
- Processing time
```

### ELK Stack (Elasticsearch + Logstash + Kibana)
```bash
# Installer ELK
helm install elasticsearch elastic/elasticsearch
helm install logstash elastic/logstash
helm install kibana elastic/kibana
```

## 🐛 TROUBLESHOOTING

### Problème: Pod Not Running
```bash
kubectl describe pod pod-name -n video-pipeline
kubectl logs pod-name -n video-pipeline
```

### Problème: PVC Pending
```bash
# Vérifier StorageClass disponible
kubectl get storageclass

# Créer un StorageClass si absent
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: kubernetes.io/aws-ebs
EOF
```

### Problème: ImagePullBackOff
```bash
# Vérifier image disponible dans registry
docker pull video-pipeline/api:latest

# Créer imagePullSecret
kubectl create secret docker-registry regcred \
  --docker-server=yourdomain.com \
  --docker-username=xxxxx \
  --docker-password=xxxxx
```

## 💾 BACKUP & DISASTER RECOVERY

### Backup Data
```bash
# Backup PVC
kubectl exec -it pvc-pod -n video-pipeline -- tar czf - /data | tar xzf - -C /backup

# Snapshot PVC (si provider supporte)
kubectl patch volumesnapshotclass csi-hostpath-snapclass \
  -p '{"deletionPolicy":"Delete"}'
```

### Restauration
```bash
# Restore from backup
kubectl cp backup/data pvc-pod:/data -n video-pipeline
```

## 📞 SUPPORT & DOCUMENTATION

- API Docs: `http://localhost:8000/docs`
- Orchestrator Docs: `http://localhost:8006/docs`
- Service Health: `http://localhost:8000/health`

---

**Version**: 1.0.0
**Dernière mise à jour**: Janvier 2026
**Mainteneur**: DevOps Team
