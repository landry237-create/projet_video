#!/bin/bash
# ============================================
# Script: Orchestration locale avec Docker Compose
# Utilisation: bash docker-deploy.sh [start|stop|logs|rebuild]
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================
# FUNCTIONS
# ============================================

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# ============================================
# CREATE DIRECTORIES
# ============================================

create_dirs() {
    print_header "Création des répertoires"
    
    mkdir -p database
    mkdir -p backend/data/{uploads,temp,outputs}
    mkdir -p nginx
    mkdir -p k8s
    
    print_success "Répertoires créés"
}

# ============================================
# BUILD IMAGES
# ============================================

build_images() {
    print_header "Build des images Docker"
    
    print_warning "Building animal-detector..."
    docker build -t video-pipeline/animal-detector:latest -f Dockerfile.animal-detector .
    print_success "Animal Detector built"
    
    print_warning "Building language-detector..."
    docker build -t video-pipeline/language-detector:latest -f Dockerfile.language-detector .
    print_success "Language Detector built"
    
    print_warning "Building downscale..."
    docker build -t video-pipeline/downscale:latest -f Dockerfile.downscale .
    print_success "Downscale built"
    
    print_warning "Building subtitles..."
    docker build -t video-pipeline/subtitles:latest -f Dockerfile.subtitles .
    print_success "Subtitles built"
    
    print_warning "Building video-merger..."
    docker build -t video-pipeline/video-merger:latest -f Dockerfile.video-merger .
    print_success "Video Merger built"
    
    print_warning "Building API..."
    docker build -t video-pipeline/api:latest -f Dockerfile.api .
    print_success "API built"
    
    print_success "Toutes les images sont construites ✓"
}

# ============================================
# START CONTAINERS
# ============================================

start_containers() {
    print_header "Démarrage des conteneurs"
    
    docker-compose up -d
    
    print_warning "Attente du démarrage des services..."
    sleep 10
    
    # Vérifier health
    check_health
}

# ============================================
# STOP CONTAINERS
# ============================================

stop_containers() {
    print_header "Arrêt des conteneurs"
    
    docker-compose down
    
    print_success "Conteneurs arrêtés"
}

# ============================================
# CHECK HEALTH
# ============================================

check_health() {
    print_header "Vérification de la santé des services"
    
    local services=(
        "8000:API Gateway"
        "8001:Animal Detector"
        "8002:Language Detector"
        "8003:Downscale"
        "8004:Subtitles"
        "8005:Video Merger"
        "6379:Redis"
    )
    
    for service in "${services[@]}"; do
        local port="${service%%:*}"
        local name="${service##*:}"
        
        if curl -s http://localhost:$port/health > /dev/null 2>&1 || redis-cli -p $port ping > /dev/null 2>&1; then
            print_success "$name (Port $port) ✓"
        else
            print_warning "$name (Port $port) - Not ready yet"
        fi
    done
}

# ============================================
# LOGS
# ============================================

show_logs() {
    print_header "Affichage des logs"
    
    if [ -z "$1" ]; then
        echo "Services disponibles:"
        echo "  - api"
        echo "  - animal-detector"
        echo "  - language-detector"
        echo "  - downscale"
        echo "  - subtitles"
        echo "  - video-merger"
        echo "  - redis"
        echo ""
        echo "Usage: bash docker-deploy.sh logs <service>"
        return 1
    fi
    
    docker-compose logs -f "$1"
}

# ============================================
# TEST UPLOAD
# ============================================

test_upload() {
    print_header "Test d'upload vidéo"
    
    if [ ! -f "sample_video.mp4" ]; then
        print_error "Fichier sample_video.mp4 non trouvé"
        print_warning "Créez un fichier vidéo de test: sample_video.mp4"
        return 1
    fi
    
    print_warning "Envoi du fichier..."
    
    response=$(curl -s -X POST http://localhost:8000/video/upload \
        -F "file=@sample_video.mp4" \
        -w "\n%{http_code}")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        print_success "Upload réussi"
        echo "$body" | python -m json.tool
    else
        print_error "Upload échoué (HTTP $http_code)"
        echo "$body"
    fi
}

# ============================================
# CLEAN
# ============================================

clean_all() {
    print_header "Nettoyage complet"
    
    print_warning "Arrêt des conteneurs..."
    docker-compose down -v
    
    print_warning "Suppression des images..."
    docker rmi -f video-pipeline/api:latest
    docker rmi -f video-pipeline/animal-detector:latest
    docker rmi -f video-pipeline/language-detector:latest
    docker rmi -f video-pipeline/downscale:latest
    docker rmi -f video-pipeline/subtitles:latest
    docker rmi -f video-pipeline/video-merger:latest
    
    print_warning "Suppression des volumes..."
    docker volume rm -f video-pipeline_shared_data
    docker volume rm -f video-pipeline_redis_data
    docker volume rm -f video-pipeline_merger_outputs
    
    print_success "Nettoyage terminé"
}

# ============================================
# SHOW STATUS
# ============================================

show_status() {
    print_header "Statut des conteneurs"
    
    docker-compose ps
    
    print_header "Utilisation des ressources"
    
    docker stats --no-stream
}

# ============================================
# MAIN
# ============================================

main() {
    case "${1:-help}" in
        start)
            create_dirs
            build_images
            start_containers
            print_header "✨ Pipeline démarrée avec succès!"
            print_success "API disponible sur: http://localhost:8000"
            print_success "Documentation: http://localhost:8000/docs"
            print_warning "Prochaines étapes:"
            echo "  1. Accédez à http://localhost:8000"
            echo "  2. Uploadez une vidéo"
            echo "  3. Vérifiez le statut avec: bash docker-deploy.sh status"
            ;;
        stop)
            stop_containers
            ;;
        restart)
            stop_containers
            sleep 2
            start_containers
            print_success "Conteneurs redémarrés"
            ;;
        logs)
            show_logs "$2"
            ;;
        test)
            test_upload
            ;;
        clean)
            read -p "⚠️  Cette action supprimera tous les conteneurs, images et volumes. Continuer? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                clean_all
            fi
            ;;
        status)
            show_status
            ;;
        health)
            check_health
            ;;
        build)
            build_images
            ;;
        rebuild)
            clean_all
            build_images
            start_containers
            print_success "Reconstruction terminée"
            ;;
        *)
            print_header "Video Pipeline Docker Orchestration"
            echo ""
            echo "Usage: bash docker-deploy.sh <commande>"
            echo ""
            echo "Commandes disponibles:"
            echo "  start      - Build & Démarrer tous les services"
            echo "  stop       - Arrêter tous les services"
            echo "  restart    - Redémarrer tous les services"
            echo "  rebuild    - Nettoyer et reconstruire tout"
            echo "  logs       - Afficher les logs d'un service"
            echo "  status     - Afficher le statut des conteneurs"
            echo "  health     - Vérifier la santé des services"
            echo "  test       - Tester un upload vidéo"
            echo "  clean      - Supprimer tous les conteneurs/images/volumes"
            echo "  build      - Builder les images"
            echo ""
            echo "Exemples:"
            echo "  bash docker-deploy.sh start"
            echo "  bash docker-deploy.sh logs api"
            echo "  bash docker-deploy.sh test"
            echo ""
            ;;
    esac
}

main "$@"
