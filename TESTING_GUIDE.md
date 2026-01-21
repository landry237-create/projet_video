# Guide Complet - Test & Validation

## 🧪 VALIDATION LOCAL (Docker Compose)

### 1. Démarrer l'Infrastructure

```bash
cd cloud

# Build et start tous les services
bash docker-deploy.sh start
```

### 2. Vérifier que Tout Fonctionne

```bash
# Vérifier les conteneurs
docker-compose ps

# Résultat attendu:
# STATUS: Up x seconds (tous les services)
```

### 3. Tester Chaque Service Individuellement

#### Test 1: API Gateway (8000)
```bash
curl http://localhost:8000/health

# Résultat attendu:
# {"status": "healthy", "service": "api", ...}
```

#### Test 2: Redis (6379)
```bash
redis-cli ping

# Résultat attendu:
# PONG
```

#### Test 3: Animal Detector (8001)
```bash
curl http://localhost:8001/health

# Résultat attendu:
# {"status": "healthy", "service": "animal-detector", ...}
```

#### Test 4: Language Detector (8002)
```bash
curl http://localhost:8002/health

# Résultat attendu:
# {"status": "healthy", "service": "language-detector", ...}
```

#### Test 5: Downscale (8003)
```bash
curl http://localhost:8003/health

# Résultat attendu:
# {"status": "healthy", "service": "downscale", ...}
```

#### Test 6: Subtitles (8004)
```bash
curl http://localhost:8004/health

# Résultat attendu:
# {"status": "healthy", "service": "subtitles", ...}
```

#### Test 7: Video Merger ⭐ (8005)
```bash
curl http://localhost:8005/health

# Résultat attendu:
# {"status": "healthy", "service": "video-merger", ...}
```

### 4. Tester l'Upload de Vidéo

```bash
# Créer un fichier vidéo de test (optionnel)
# Si vous avez ffmpeg:
ffmpeg -f lavfi -i testsrc=s=320x240:d=10 -f lavfi -i sine=f=440:d=10 test_video.mp4

# Ou utiliser un fichier vidéo existant
# Upload
curl -X POST http://localhost:8000/video/upload \
  -F "file=@test_video.mp4"

# Résultat attendu:
# {
#   "status": "ok",
#   "file_id": "video_xxxxx_mp4",
#   "message": "Upload successful"
# }
```

### 5. Tester le Statut de Traitement

```bash
# Remplacer {file_id} par l'ID reçu
curl http://localhost:8000/video/status/video_xxxxx_mp4

# Résultat attendu:
# {
#   "status": "processing",
#   "file_id": "video_xxxxx_mp4",
#   "current_stage": "downscaling",
#   "progress": 25,
#   "details": {...}
# }
```

### 6. Voir les Logs en Temps Réel

```bash
# API Gateway logs
bash docker-deploy.sh logs api

# Video Merger logs (⭐ nouveau service)
bash docker-deploy.sh logs video-merger

# Orchestrator logs
bash docker-deploy.sh logs orchestrator

# Tous les logs
docker-compose logs -f
```

## ☸️ VALIDATION KUBERNETES

### 1. Déployer l'Infrastructure

```bash
# Appliquer tous les manifests
kubectl apply -f k8s/

# Ou avec PowerShell
.\k8s-deploy.ps1 -Action deploy
```

### 2. Vérifier le Déploiement

```bash
# Vérifier tous les pods sont Running
kubectl get pods -n video-pipeline

# Résultat attendu: Tous les pods en "Running"
```

### 3. Tester Connectivité Entre Services

```bash
# Port forward API Gateway
kubectl port-forward svc/api-gateway 8000:8000 -n video-pipeline &

# Test en arrière-plan
curl http://localhost:8000/health

# Vérifier accès aux services internes
kubectl exec -it deployment/api-gateway -n video-pipeline -- \
  curl http://animal-detector:8001/health
```

### 4. Vérifier Auto-Scaling

```bash
# Vérifier HPA
kubectl get hpa -n video-pipeline

# Monitorer les changes
kubectl get hpa -n video-pipeline -w

# Simuler charge (optionnel)
# Faire plusieurs uploads simultanés
```

### 5. Logs Kubernetes

```bash
# Logs API Gateway
kubectl logs -f deployment/api-gateway -n video-pipeline

# Logs Video Merger ⭐
kubectl logs -f deployment/video-merger -n video-pipeline

# Tous les logs d'un pod
kubectl logs -f pod/video-merger-xxxxx -n video-pipeline
```

## 📊 BENCHMARKS DE PERFORMANCE

### Temps de Traitement Estimé

| Étape | Durée | Service |
|-------|-------|---------|
| Downscale | 5-10s | FFmpeg |
| Animal Detection | 15-30s | YOLO11 |
| Language Detection | 10-20s | Speech Rec |
| Subtitles Gen | 20-60s | Whisper |
| Video Merger | 10-20s | FFmpeg |
| **TOTAL** | **60-140s** | Pipeline |

*Dépend de: résolution, durée vidéo, CPU disponible*

### Ressources Utilisés

```
API Gateway:        ~100MB RAM, ~5% CPU (idle)
Animal Detector:    ~1.5GB RAM, ~30% CPU (processing)
Language Detector:  ~1GB RAM, ~25% CPU (processing)
Downscale:          ~500MB RAM, ~40% CPU (processing)
Subtitles:          ~1.5GB RAM, ~35% CPU (processing)
Video Merger:       ~800MB RAM, ~45% CPU (processing)
Redis:              ~100MB RAM, ~1% CPU
Nginx:              ~50MB RAM, ~1% CPU
```

## 🔍 VALIDATION DÉTAILLÉE

### Checklist Complète

**Infrastructure**
- [ ] Tous les conteneurs en Running (Docker) ou tous les pods Running (K8s)
- [ ] Services accessibles sur les bons ports
- [ ] Health checks répondent 200 OK
- [ ] Redis connecté et fonctionnant
- [ ] Volumes persistants montés
- [ ] Ingress configuré (K8s)

**Fonctionnalité**
- [ ] Upload vidéo fonctionne
- [ ] Status tracking fonctionne
- [ ] Downscale produit fichier valide
- [ ] Animal detection retourne résultats
- [ ] Language detection retourne langue
- [ ] Subtitles génère VTT valide
- [ ] Video Merger fusionne correctement
- [ ] Fichier final joue avec subs

**Performance**
- [ ] Temps de traitement < 3 minutes
- [ ] Pas d'erreurs 500
- [ ] Pas de memory leaks
- [ ] Logs sans erreurs critiques
- [ ] Auto-scaling réactif (K8s)

**Sécurité**
- [ ] CORS fonctionne
- [ ] Rate limiting actif
- [ ] HTTPS/TLS valide (K8s)
- [ ] Secrets configurés
- [ ] Pas de credentials en logs

## 🐛 DEBUGGING

### Problème: Pods CrashLoopBackOff

```bash
# Vérifier les logs
kubectl describe pod video-merger-xxxxx -n video-pipeline

# Voir les erreurs
kubectl logs pod/video-merger-xxxxx -n video-pipeline --previous

# Vérifier l'image
kubectl get pod video-merger-xxxxx -n video-pipeline -o yaml | grep -A 5 image
```

### Problème: Upload Timeout

```bash
# Vérifier les timeouts nginx
kubectl get ingress video-pipeline-ingress -n video-pipeline -o yaml | grep timeout

# Vérifier les logs nginx
kubectl logs -f deployment/nginx -n video-pipeline
```

### Problème: Video Merger Erreur

```bash
# Voir logs détaillés
kubectl logs -f deployment/video-merger -n video-pipeline

# Vérifier fichiers d'entrée
kubectl exec -it pod/video-merger-xxxxx -n video-pipeline -- \
  ls -lah /data/

# Vérifier disque
kubectl exec -it pod/video-merger-xxxxx -n video-pipeline -- \
  df -h
```

## 📈 MONITORING

### Métriques à Vérifier

```bash
# Utilisation des ressources
kubectl top pods -n video-pipeline
kubectl top nodes

# Events Kubernetes
kubectl get events -n video-pipeline

# Statut des deployments
kubectl rollout status deployment/video-merger -n video-pipeline

# Vérifier HPA activé
kubectl get hpa -n video-pipeline --watch
```

## ✅ CHECKLIST DE PRODUCTION

Avant de passer à la production:

- [ ] Tous les tests locaux réussis
- [ ] Tous les tests K8s réussis
- [ ] Documentation lue et comprise
- [ ] Credentials configurés securely
- [ ] Backup strategy défini
- [ ] Monitoring setup (Prometheus, etc)
- [ ] Alertes configurées
- [ ] Runbooks préparés
- [ ] Load tests réussis
- [ ] Disaster recovery plan

## 📝 NOTES

- **Temps premier déploiement**: ~15 minutes
- **Temps tests complets**: ~30 minutes
- **Temps premier upload**: ~2-5 minutes (modèles à charger)
- **Uploads suivants**: ~1-2 minutes (caches chauds)

---

**Date**: Janvier 2026
**Status**: ✅ Ready to Test
