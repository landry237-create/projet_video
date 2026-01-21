# 🚀 GUIDE DE DÉPLOIEMENT - Video Processing Pipeline

## 📋 PRÉREQUIS

### Local (Docker Compose)
- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 20GB disque libre

### Production (Kubernetes)
- Kubernetes 1.24+
- kubectl configuré
- Helm 3.0+ (optionnel)
- Ingress Controller (nginx-ingress)
- Storage Class configuré
- Domain registré

## 🐳 DÉPLOIEMENT LOCAL (Docker Compose)

### 1. Préparation
```bash
cd /path/to/cloud

# Créer structure des répertoires
mkdir -p database
mkdir -p frontend/static frontend/templates
mkdir -p backend/data/{uploads,temp,outputs}

# Donner les permissions
chmod -R 755 database backend/data
```

### 2. Configuration Environment
```bash
# Créer .env
cat > .env <<EOF
PYTHONUNBUFFERED=1
DEVICE=cpu
MAX_FILE_SIZE=5000000000
REDIS_URL=redis://redis:6379
DATABASE_URL=sqlite:///./database/local_db.json
UPLOADS_DIR=/app/data/uploads
DATA_DIR=/app/data
EOF
```

### 3. Builder les Images Docker
```bash
# Build tous les services
docker-compose build

# Ou build individuellement
docker build -t video-pipeline/animal-detector:latest -f Dockerfile.animal-detector .
docker build -t video-pipeline/language-detector:latest -f Dockerfile.language-detector .
docker build -t video-pipeline/downscale:latest -f Dockerfile.downscale .
docker build -t video-pipeline/subtitles:latest -f Dockerfile.subtitles .
docker build -t video-pipeline/video-merger:latest -f Dockerfile.video-merger .
```

### 4. Démarrer les Conteneurs
```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier le statut
docker-compose ps

# Voir les logs
docker-compose logs -f api
docker-compose logs -f video-merger
```

### 5. Vérifier la Santé
```bash
# Health checks
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health

# Redis
redis-cli ping
```

### 6. Tester l'Upload
```bash
# Upload une vidéo
curl -X POST http://localhost:8000/video/upload \
  -F "file=@sample_video.mp4"

# Récupérer le statut
curl http://localhost:8000/video/status/{file_id}
```

### 7. Arrêter les Services
```bash
# Arrêter tous les conteneurs
docker-compose down

# Arrêter + supprimer volumes
docker-compose down -v
```

## ☸️ DÉPLOIEMENT KUBERNETES

### 1. Préparation du Cluster

```bash
# Vérifier connexion à Kubernetes
kubectl cluster-info
kubectl get nodes

# Créer namespace
kubectl create namespace video-pipeline

# Vérifier StorageClass disponible
kubectl get storageclass
```

### 2. Préparer les Images

**Option A: Build local puis push**
```bash
# Build images localement
docker build -t yourdomain.com/video-pipeline/animal-detector:latest -f Dockerfile.animal-detector .
docker build -t yourdomain.com/video-pipeline/language-detector:latest -f Dockerfile.language-detector .
docker build -t yourdomain.com/video-pipeline/downscale:latest -f Dockerfile.downscale .
docker build -t yourdomain.com/video-pipeline/subtitles:latest -f Dockerfile.subtitles .
docker build -t yourdomain.com/video-pipeline/video-merger:latest -f Dockerfile.video-merger .

# Push vers registry
docker push yourdomain.com/video-pipeline/animal-detector:latest
docker push yourdomain.com/video-pipeline/language-detector:latest
docker push yourdomain.com/video-pipeline/downscale:latest
docker push yourdomain.com/video-pipeline/subtitles:latest
docker push yourdomain.com/video-pipeline/video-merger:latest
```

**Option B: Utiliser Docker Hub**
```bash
docker tag animal-detector:latest yourusername/animal-detector:latest
docker push yourusername/animal-detector:latest
# ... répéter pour autres services
```

### 3. Configurer Secrets & ConfigMap
```bash
# Créer secrets
kubectl create secret generic video-pipeline-secrets \
  -n video-pipeline \
  --from-literal=REDIS_PASSWORD=your-secure-password \
  --from-literal=API_KEY=your-api-key

# Vérifier
kubectl get secrets -n video-pipeline
```

### 4. Appliquer les Manifests Kubernetes

```bash
# Appliquer dans l'ordre
kubectl apply -f k8s/01-namespace-configmap-pvc.yaml
kubectl apply -f k8s/02-services-deployments.yaml
kubectl apply -f k8s/03-api-gateway-ingress-hpa.yaml
kubectl apply -f k8s/04-orchestrator-webhook.yaml

# Vérifier deployment
kubectl get deployments -n video-pipeline
kubectl get pods -n video-pipeline
kubectl get svc -n video-pipeline
kubectl get pvc -n video-pipeline
```

### 5. Configurer Ingress

```bash
# Installer Nginx Ingress Controller (si pas déjà fait)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install nginx ingress-nginx/ingress-nginx

# Modifier Ingress pour votre domaine
kubectl edit ingress video-pipeline-ingress -n video-pipeline

# Changer: video.yourdomain.com → votre domaine réel
```

### 6. Configurer HTTPS (Let's Encrypt)

```bash
# Installer cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Créer ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Vérifier certificat
kubectl get certificate -n video-pipeline
```

### 7. Vérifier le Déploiement

```bash
# Attendre que tous les pods soient Running
kubectl wait --for=condition=ready pod -l app=api-gateway -n video-pipeline --timeout=300s

# Logs pods
kubectl logs -f deployment/api-gateway -n video-pipeline
kubectl logs -f deployment/video-merger -n video-pipeline

# Port forward pour test local
kubectl port-forward svc/api-gateway 8000:8000 -n video-pipeline
# Ensuite: curl http://localhost:8000/health
```

### 8. Tester Upload

```bash
# Via port-forward
curl -X POST http://localhost:8000/video/upload \
  -F "file=@sample_video.mp4"

# Via Ingress (une fois configuré)
curl -X POST https://video.yourdomain.com/video/upload \
  -F "file=@sample_video.mp4"
```

## 🔄 ORCHESTRATION AUTOMATIQUE

### Webhook Upload → Pipeline

Modifier [backend/routers/video.py](backend/routers/video.py):

```python
@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    # ... code upload existant ...
    
    # NOUVEAU: Déclencher orchestration
    import httpx
    
    session_id = str(uuid.uuid4())
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://orchestrator:8006/orchestrate",
                json={
                    "session_id": session_id,
                    "video_id": file_id,
                    "video_path": str(file_path),
                    "metadata": {
                        "filename": file.filename,
                        "size_bytes": file_size,
                        "uploaded_at": datetime.now().isoformat()
                    }
                },
                timeout=3600.0
            )
            
            return {
                "status": "ok",
                "file_id": file_id,
                "task_id": response.json().get("task_id"),
                "message": "Pipeline orchestration lancée"
            }
    except Exception as e:
        logger.error(f"Orchestration error: {e}")
        return {
            "status": "warning",
            "file_id": file_id,
            "message": "Upload OK, orchestration non disponible"
        }
```

## 📊 MONITORING & LOGS

### Vérifier HPA (Auto-scaling)

```bash
kubectl get hpa -n video-pipeline
kubectl watch hpa -n video-pipeline

# Details
kubectl describe hpa api-gateway-hpa -n video-pipeline
```

### Monitorer l'Utilisation

```bash
# Resources utilisation
kubectl top pods -n video-pipeline
kubectl top nodes

# Metrics détaillés (si Prometheus installé)
kubectl port-forward svc/prometheus 9090:9090 -n video-pipeline
# Accès: http://localhost:9090
```

### Logs Centralisés

```bash
# Récupérer les logs d'un service
kubectl logs -f deployment/api-gateway -n video-pipeline --tail=100

# Logs d'un pod spécifique
kubectl logs -f pod/api-gateway-xxxxx -n video-pipeline

# Export logs
kubectl logs deployment/api-gateway -n video-pipeline > api_logs.txt
```

## 🔄 MISE À JOUR & ROLLBACK

### Mise à Jour d'une Image

```bash
# Mettre à jour image
kubectl set image deployment/video-merger \
  video-merger=video-pipeline/video-merger:v2.0 \
  -n video-pipeline

# Monitoring rollout
kubectl rollout status deployment/video-merger -n video-pipeline -w

# Vérifier historique
kubectl rollout history deployment/video-merger -n video-pipeline

# Rollback si problème
kubectl rollout undo deployment/video-merger -n video-pipeline
```

### Update tous les services

```bash
# Re-appliquer manifests (si images mises à jour)
kubectl apply -f k8s/ -n video-pipeline

# Force restart
kubectl rollout restart deployment/api-gateway -n video-pipeline
kubectl rollout restart deployment/video-merger -n video-pipeline
```

## 🗑️ CLEANUP

### Supprimer tout (Attention!)

```bash
# Supprimer tout le namespace (tous les resources)
kubectl delete namespace video-pipeline

# Ou supprimer ressources spécifiques
kubectl delete deployment -n video-pipeline --all
kubectl delete pvc -n video-pipeline --all
```

## 📞 TROUBLESHOOTING

### Problème: Pod CrashLoopBackOff

```bash
# Voir logs d'erreur
kubectl logs pod/xxx -n video-pipeline --previous

# Décrire le pod
kubectl describe pod/xxx -n video-pipeline

# Vérifier environment variables
kubectl exec pod/xxx -n video-pipeline -- env
```

### Problème: PVC Pending

```bash
# Vérifier PVC
kubectl get pvc -n video-pipeline

# Décrire PVC
kubectl describe pvc shared-data-pvc -n video-pipeline

# Vérifier StorageClass
kubectl get storageclass

# Créer StorageClass si absent
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
EOF
```

### Problème: ImagePullBackOff

```bash
# Vérifier image registry
docker pull yourdomain.com/video-pipeline/api:latest

# Ajouter imagePullSecret
kubectl create secret docker-registry regcred \
  --docker-server=yourdomain.com \
  --docker-username=username \
  --docker-password=password \
  -n video-pipeline

# Ajouter à deployment
# imagePullSecrets:
# - name: regcred
```

### Problème: Timeouts Upload

```bash
# Vérifier Ingress settings
kubectl edit ingress video-pipeline-ingress -n video-pipeline

# Augmenter timeouts nginx:
# nginx.ingress.kubernetes.io/proxy-read-timeout: "1200"
# nginx.ingress.kubernetes.io/proxy-send-timeout: "1200"
```

## ✅ CHECKLIST FINAL

- [x] Namespace créé
- [x] ConfigMaps & Secrets appliqués
- [x] PVCs créés et bound
- [x] Services en Running
- [x] Pods healthy (tous Running)
- [x] Ingress configuré
- [x] SSL/TLS activé
- [x] Load balancer distribuant le trafic
- [x] Auto-scaling configuré
- [x] Orchestrator actif
- [x] Upload video testés
- [x] Pipeline pipeline complète executée
- [x] Monitoring en place
- [x] Logs centralisés

---

**Version**: 1.0.0
**Date**: Janvier 2026
