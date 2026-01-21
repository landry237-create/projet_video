# ============================================
# Script: Orchestration Kubernetes
# Utilisation: .\k8s-deploy.ps1 -Action deploy
# ============================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("deploy", "status", "logs", "delete", "restart", "scale")]
    [string]$Action,
    
    [string]$Service,
    [int]$Replicas = 3,
    [int]$TailLines = 100
)

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Blue
    Write-Host "║ $Title" -ForegroundColor Blue
    Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Blue
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

# ============================================
# DEPLOY
# ============================================

function Deploy-Kubernetes {
    Write-Header "Déploiement Kubernetes"
    
    Write-Warning "Création du namespace..."
    kubectl create namespace video-pipeline --dry-run=client -o yaml | kubectl apply -f -
    Write-Success "Namespace créé/vérifié"
    
    Write-Warning "Application des manifests..."
    Get-ChildItem "k8s" -Filter "*.yaml" | Sort-Object Name | ForEach-Object {
        Write-Host "  - Appliquant: $($_.Name)"
        kubectl apply -f "k8s/$($_.Name)" -n video-pipeline
    }
    
    Write-Success "Manifests appliqués"
    
    Write-Warning "Attente du démarrage des pods..."
    kubectl wait --for=condition=ready pod -l app=api-gateway -n video-pipeline --timeout=300s
    
    Write-Success "Déploiement terminé ✓"
    
    Write-Header "Prochaines étapes"
    Write-Host "1. Récupérer l'adresse Ingress:"
    Write-Host "   kubectl get ingress -n video-pipeline"
    Write-Host ""
    Write-Host "2. Port forward pour accès local:"
    Write-Host "   kubectl port-forward svc/api-gateway 8000:8000 -n video-pipeline"
    Write-Host ""
    Write-Host "3. Vérifier la santé:"
    Write-Host "   kubectl get pods -n video-pipeline"
}

# ============================================
# STATUS
# ============================================

function Show-Status {
    Write-Header "Statut Kubernetes"
    
    Write-Host "Namespace: video-pipeline" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Deployments:" -ForegroundColor Cyan
    kubectl get deployments -n video-pipeline
    
    Write-Host ""
    Write-Host "Pods:" -ForegroundColor Cyan
    kubectl get pods -n video-pipeline
    
    Write-Host ""
    Write-Host "Services:" -ForegroundColor Cyan
    kubectl get services -n video-pipeline
    
    Write-Host ""
    Write-Host "PVCs:" -ForegroundColor Cyan
    kubectl get pvc -n video-pipeline
    
    Write-Host ""
    Write-Host "Ingress:" -ForegroundColor Cyan
    kubectl get ingress -n video-pipeline
    
    Write-Host ""
    Write-Host "HPA:" -ForegroundColor Cyan
    kubectl get hpa -n video-pipeline
}

# ============================================
# LOGS
# ============================================

function Show-Logs {
    param([string]$Service)
    
    if (-not $Service) {
        Write-Host "Services disponibles:" -ForegroundColor Cyan
        Write-Host "  - api-gateway"
        Write-Host "  - animal-detector"
        Write-Host "  - language-detector"
        Write-Host "  - downscale"
        Write-Host "  - subtitles"
        Write-Host "  - video-merger"
        Write-Host "  - orchestrator"
        Write-Host "  - redis"
        return
    }
    
    Write-Header "Logs: $Service"
    kubectl logs -f deployment/$Service -n video-pipeline --tail=$TailLines
}

# ============================================
# DELETE
# ============================================

function Delete-Kubernetes {
    Write-Header "Suppression Kubernetes"
    
    $confirmation = Read-Host "Êtes-vous sûr? (Tapez 'yes' pour confirmer)"
    
    if ($confirmation -ne "yes") {
        Write-Warning "Suppression annulée"
        return
    }
    
    Write-Warning "Suppression du namespace video-pipeline..."
    kubectl delete namespace video-pipeline
    
    Write-Success "Namespace supprimé"
}

# ============================================
# RESTART
# ============================================

function Restart-Deployment {
    param([string]$Service)
    
    if (-not $Service) {
        Write-Host "Déploiements disponibles:" -ForegroundColor Cyan
        kubectl get deployments -n video-pipeline --no-headers | awk '{print "  - " $1}'
        return
    }
    
    Write-Warning "Redémarrage de $Service..."
    kubectl rollout restart deployment/$Service -n video-pipeline
    Write-Success "$Service redémarré"
}

# ============================================
# SCALE
# ============================================

function Scale-Deployment {
    param([string]$Service, [int]$Replicas)
    
    if (-not $Service) {
        Write-Host "Déploiements disponibles:" -ForegroundColor Cyan
        kubectl get deployments -n video-pipeline --no-headers | awk '{print "  - " $1}'
        return
    }
    
    Write-Warning "Scaling $Service à $Replicas replicas..."
    kubectl scale deployment/$Service --replicas=$Replicas -n video-pipeline
    Write-Success "$Service scalé"
}

# ============================================
# MAIN
# ============================================

switch ($Action) {
    "deploy" {
        Deploy-Kubernetes
    }
    "status" {
        Show-Status
    }
    "logs" {
        Show-Logs $Service
    }
    "delete" {
        Delete-Kubernetes
    }
    "restart" {
        Restart-Deployment $Service
    }
    "scale" {
        Scale-Deployment $Service $Replicas
    }
}
