let allVideos = [];
let deleteFileId = null;
let autoRefreshInterval = null;

class DashboardManager {
    constructor() {
        this.videosList = document.getElementById("videosList");
        this.emptyState = document.getElementById("emptyState");
        this.totalVideosEl = document.getElementById("totalVideos");
        this.processedVideosEl = document.getElementById("processedVideos");
        this.storageUsedEl = document.getElementById("storageUsed");
        this.deleteModal = document.getElementById("deleteModal");
        this.modalOverlay = document.getElementById("modalOverlay");
        
        this.init();
    }
    
    async init() {
        console.log("🚀 DashboardManager initialized");
        
        // Charger les données au démarrage
        await this.loadData();
        
        // Actualiser automatiquement toutes les 3 secondes
        autoRefreshInterval = setInterval(() => this.loadData(), 3000);
        
        console.log("🔄 Auto-refresh activé (3s)");
    }
    
    async loadData() {
        try {
            console.log("📊 Loading videos...");
            
            // Charger les vidéos depuis la BD
            const videosResponse = await fetch("/api/video/videos");
            
            if (!videosResponse.ok) {
                throw new Error(`HTTP ${videosResponse.status}`);
            }
            
            const videos = await videosResponse.json();
            console.log("✅ Videos loaded:", videos);
            
            // Charger les stats
            const statsResponse = await fetch("/api/dashboard/stats");
            const stats = await statsResponse.json();
            console.log("✅ Stats loaded:", stats);
            
            // Mettre à jour l'état
            allVideos = videos || [];
            this.updateStats(stats);
            this.renderVideos(videos);
            
        } catch (error) {
            console.error("❌ Error loading data:", error);
            // Ne pas afficher d'erreur, juste continuer à rafraîchir
        }
    }
    
    updateStats(stats) {
        console.log("📊 Updating stats:", stats);
        
        this.totalVideosEl.textContent = stats.total_videos || 0;
        this.processedVideosEl.textContent = stats.processed || 0;
        this.storageUsedEl.textContent = stats.storage_used || "0 MB";
    }
    
    renderVideos(videos) {
        console.log("🎬 Rendering videos:", videos ? videos.length : 0);
        
        if (!videos || videos.length === 0) {
            console.log("📭 Aucune vidéo");
            this.videosList.style.display = "none";
            this.emptyState.style.display = "block";
            this.videosList.innerHTML = "";
            return;
        }
        
        this.videosList.style.display = "flex";
        this.emptyState.style.display = "none";
        
        // Créer les cartes
        const cardsHTML = videos.map(video => this.createVideoCard(video)).join("");
        this.videosList.innerHTML = cardsHTML;
        
        console.log("✅ Cartes créées");
    }
    
    createVideoCard(video) {
        const statusClass = video.status === "completed" ? "status-completed" : "status-processing";
        const statusText = video.status === "completed" ? "✅ Complété" : "⏳ En cours";
        
        const fileId = video.file_id || "unknown";
        const animals = video.animals && video.animals.length > 0 ? video.animals.join(", ") : "Aucun";
        const language = video.language || "Détection...";
        
        return `
            <div class="video-card">
                <div class="video-thumbnail">🎬</div>
                <div class="video-content">
                    <div class="video-title" title="${this.escapeHtml(fileId)}">
                        ${this.escapeHtml(fileId)}
                    </div>
                    
                    <div class="video-status ${statusClass}" style="margin-top: 8px;">
                        ${statusText}
                    </div>
                    
                    <div class="video-details">
                        <div class="video-info">
                            <span class="video-info-label">🗣️ Langue:</span>
                            <span>${this.escapeHtml(language)}</span>
                        </div>
                        
                        <div class="video-info">
                            <span class="video-info-label">🦁 Animaux:</span>
                            <span>${this.escapeHtml(animals)}</span>
                        </div>
                        
                        ${video.file_size ? `
                            <div class="video-info">
                                <span class="video-info-label">📦 Taille:</span>
                                <span>${(video.file_size / 1024 / 1024).toFixed(2)} MB</span>
                            </div>
                        ` : ""}
                        
                        ${video.subtitles_path ? `
                            <div class="video-info">
                                <span class="video-info-label">📝 Sous-titres:</span>
                                <span>✓ Oui</span>
                            </div>
                        ` : ""}
                    </div>
                    
                    <div class="video-buttons">
                        ${video.subtitles_path ? `
                            <button class="btn btn-download" onclick="downloadSubtitles('${this.escapeJs(fileId)}')">
                                📥 Sous-titres
                            </button>
                        ` : ""}
                        <button class="btn btn-delete" onclick="openDeleteModal('${this.escapeJs(fileId)}')">
                            🗑️ Supprimer
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    escapeHtml(text) {
        if (!text) return "";
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }
    
    escapeJs(text) {
        if (!text) return "";
        return text.replace(/'/g, "\\'").replace(/"/g, '\\"');
    }
}

// Global functions
async function refreshDashboard() {
    console.log("🔄 Refreshing dashboard manually...");
    const manager = window.dashboardManager;
    if (manager) {
        await manager.loadData();
    }
}

async function downloadSubtitles(fileId) {
    try {
        console.log("📥 Downloading subtitles for:", fileId);
        
        const response = await fetch(`/api/video/subtitles/${fileId}`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || "Erreur lors du téléchargement");
        }
        
        // Créer un blob et télécharger
        const blob = new Blob([data.content], { type: "text/vtt;charset=utf-8" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `${fileId}_subtitles.vtt`;
        link.click();
        URL.revokeObjectURL(link.href);
        
        console.log("✅ Subtitles downloaded");
    } catch (error) {
        console.error("❌ Error:", error);
        alert(`Erreur: ${error.message}`);
    }
}

function openDeleteModal(fileId) {
    console.log("🗑️ Opening delete modal for:", fileId);
    deleteFileId = fileId;
    document.getElementById("deleteModal").style.display = "block";
    document.getElementById("modalOverlay").style.display = "block";
}

function closeDeleteModal() {
    document.getElementById("deleteModal").style.display = "none";
    document.getElementById("modalOverlay").style.display = "none";
    deleteFileId = null;
}

async function confirmDelete() {
    if (!deleteFileId) return;
    
    try {
        console.log("🗑️ Deleting:", deleteFileId);
        
        const response = await fetch(`/api/video/delete/${deleteFileId}`, {
            method: "DELETE"
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || "Erreur lors de la suppression");
        }
        
        console.log("✅ Video deleted");
        closeDeleteModal();
        
        // Rafraîchir immédiatement
        await window.dashboardManager.loadData();
        
    } catch (error) {
        console.error("❌ Error:", error);
        alert(`Erreur: ${error.message}`);
    }
}

function goHome() {
    window.location.href = "/";
}

function goUpload() {
    window.location.href = "/upload";
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    console.log("📄 DOM loaded");
    window.dashboardManager = new DashboardManager();
});

// Cleanup on page unload
window.addEventListener("beforeunload", () => {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
});
