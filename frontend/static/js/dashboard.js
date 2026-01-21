let allVideos = [];
let deleteFileId = null;
let currentVideoId = null;
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
        
        await this.loadData();
        
        // Actualiser automatiquement toutes les 3 secondes
        autoRefreshInterval = setInterval(() => this.loadData(), 3000000);
        
        console.log("🔄 Auto-refresh activé (3s)");
    }
    
    async loadData() {
        try {
            console.log("📊 Loading videos...");
            
            const videosResponse = await fetch("/api/video/videos");
            
            if (!videosResponse.ok) {
                throw new Error(`HTTP ${videosResponse.status}`);
            }
            
            const videos = await videosResponse.json();
            console.log("✅ Videos loaded:", videos);
            
            const statsResponse = await fetch("/api/dashboard/stats");
            const stats = await statsResponse.json();
            console.log("✅ Stats loaded:", stats);
            
            allVideos = videos || [];
            this.updateStats(stats);
            this.renderVideos(videos);
            
        } catch (error) {
            console.error("❌ Error loading data:", error);
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
        
        const cardsHTML = videos.map(video => this.createVideoCard(video)).join("");
        this.videosList.innerHTML = cardsHTML;
        
        console.log("✅ Cartes créées");
    }
    
    createVideoCard(video) {
        const statusClass = video.status === "completed" ? "status-completed" : "status-processing";
        const statusText = video.status === "completed" ? "✅ Complété" : "⏳ En cours";
        
        const fileId = video.file_id || "unknown";
        const language = video.language || "Détection...";
        const animals = video.animals || "Détection...";
        
        return `
            <div class="video-card">
                <div class="video-thumbnail">
                    <video width="100%" height="180" style="background: #000; object-fit: cover;" controls>
                        <source src="/api/video/downscaled/${this.escapeJs(fileId)}" type="video/mp4">
                        🎬
                    </video>
                </div>
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
                                <span class="video-info-label">📽️ Sous-titres:</span>
                                <span>✓ VTT</span>
                            </div>
                        ` : ""}
                    </div>
                    
                    <div class="video-buttons">
                        ${video.status === "completed" ? `
                            <button class="btn btn-download" onclick="openDetailsModal('${this.escapeJs(fileId)}')">
                                👁️ Voir plus
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

// ============================================
// MODAL DÉTAILS
// ============================================
async function openDetailsModal(fileId) {
    console.log("👁️ Opening details for:", fileId);
    
    currentVideoId = fileId;
    
    // Trouver la vidéo
    const video = allVideos.find(v => v.file_id === fileId);
    
    if (!video) {
        alert("Vidéo non trouvée");
        return;
    }
    
    // Afficher le modal
    document.getElementById("detailsModalOverlay").style.display = "flex";
    
    // Remplir le titre
    document.getElementById("modalTitle").textContent = `📽️ ${fileId}`;
    
    // Remplir les métadonnées
    displayMetadata(video);
    
    // Remplir les boutons de téléchargement
    displayDownloadButtons(video);
    
    // Charger les sous-titres
    await loadSubtitles(fileId);
    
    // Charger le JSON
    loadJsonMetadata(video);
}

function closeDetailsModal(event) {
    // Fermer uniquement si on clique sur l'overlay, pas sur le modal
    if (event && event.target.id !== 'detailsModalOverlay') {
        return;
    }
    
    document.getElementById("detailsModalOverlay").style.display = "none";
    currentVideoId = null;
}

function displayMetadata(video) {
    const grid = document.getElementById("metadataGrid");
    
    const metadata = [
        { label: "🗂️ Fichier ID", value: video.file_id },
        { label: "📝 Nom Original", value: video.filename },
        { label: "🗣️ Langue", value: video.language || "N/A" },
        { label: "🦁 Animaux", value: video.animals || "N/A" },
        { label: "📦 Taille", value: video.file_size ? `${(video.file_size / 1024 / 1024).toFixed(2)} MB` : "N/A" },
        { label: "📅 Date", value: video.created_at ? new Date(video.created_at).toLocaleString() : "N/A" },
        { label: "✅ Statut", value: video.status },
        { label: "⏱️ Complété", value: video.completed_at ? new Date(video.completed_at).toLocaleString() : "En cours..." },
    ];
    
    grid.innerHTML = metadata.map(item => `
        <div class="metadata-item">
            <div class="metadata-label">${item.label}</div>
            <div class="metadata-value">${escapeHtml(item.value)}</div>
        </div>
    `).join("");
}

function displayDownloadButtons(video) {
    const buttons = document.getElementById("downloadButtons");
    
    let html = ``;
    
    if (video.subtitles_path) {
        html += `
            <button class="btn btn-download" onclick="downloadSubtitles('${escapeJs(currentVideoId)}')">
                📥 Télécharger Sous-titres
            </button>
        `;
    }
    
    html += `
        <button class="btn btn-download" onclick="downloadMetadata('${escapeJs(currentVideoId)}')">
            📥 Télécharger JSON
        </button>
    `;
    
    buttons.innerHTML = html;
}

async function loadSubtitles(fileId) {
    try {
        console.log("📺 Loading subtitles for:", fileId);
        
        const response = await fetch(`/api/video/subtitles/${fileId}`);
        const data = await response.json();
        
        if (!data.success) {
            document.getElementById("vttContent").textContent = "❌ " + (data.error || "Sous-titres non disponibles");
            return;
        }
        
        document.getElementById("vttContent").textContent = data.content;
        
    } catch (error) {
        console.error("❌ Error:", error);
        document.getElementById("vttContent").textContent = `❌ Erreur: ${error.message}`;
    }
}

function loadJsonMetadata(video) {
    try {
        const jsonData = {
            file_id: video.file_id,
            filename: video.filename,
            status: video.status,
            language: video.language,
            animals: video.animals ? video.animals.split(", ") : [],
            file_size_mb: video.file_size ? (video.file_size / 1024 / 1024).toFixed(2) : 0,
            created_at: video.created_at,
            completed_at: video.completed_at,
            subtitles_path: video.subtitles_path
        };
        
        const jsonStr = JSON.stringify(jsonData, null, 2);
        
        // Ajouter de la coloration syntaxique simple
        const highlighted = jsonStr
            .replace(/(".*?")\s*:/g, '<span class="json-key">$1</span>:')
            .replace(/:\s*(".*?")/g, ': <span class="json-string">$1</span>')
            .replace(/:\s*(\d+)/g, ': <span class="json-number">$1</span>')
            .replace(/:\s*(true|false)/g, ': <span class="json-boolean">$1</span>')
            .replace(/:\s*(null)/g, ': <span class="json-boolean">$1</span>');
        
        document.getElementById("jsonContent").innerHTML = highlighted;
        
    } catch (error) {
        console.error("❌ Error:", error);
        document.getElementById("jsonContent").textContent = `❌ Erreur: ${error.message}`;
    }
}

// ============================================
// TABS SWITCHING
// ============================================
function switchTab(event, tabName) {
    // Activer le bouton
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Afficher le contenu
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
}

// ============================================
// TÉLÉCHARGEMENT
// ============================================
function downloadSubtitles(fileId) {
    const vttContent = document.getElementById("vttContent").textContent;
    
    const blob = new Blob([vttContent], { type: "text/vtt;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${fileId}_subtitles.vtt`;
    link.click();
    URL.revokeObjectURL(link.href);
    
    console.log("✅ Sous-titres téléchargés");
}

function downloadMetadata(fileId) {
    const video = allVideos.find(v => v.file_id === fileId);
    
    if (!video) return;
    
    const jsonData = {
        file_id: video.file_id,
        filename: video.filename,
        status: video.status,
        language: video.language,
        animals: video.animals ? video.animals.split(", ") : [],
        file_size_mb: video.file_size ? (video.file_size / 1024 / 1024).toFixed(2) : 0,
        created_at: video.created_at,
        completed_at: video.completed_at,
        subtitles_path: video.subtitles_path
    };
    
    const jsonStr = JSON.stringify(jsonData, null, 2);
    
    const blob = new Blob([jsonStr], { type: "application/json;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${fileId}_metadata.json`;
    link.click();
    URL.revokeObjectURL(link.href);
    
    console.log("✅ JSON téléchargé");
}

// ============================================
// SUPPRESSION
// ============================================
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
        closeDetailsModal();
        
        await window.dashboardManager.loadData();
        
    } catch (error) {
        console.error("❌ Error:", error);
        alert(`Erreur: ${error.message}`);
    }
}

// ============================================
// GLOBAL FUNCTIONS
// ============================================
async function refreshDashboard() {
    console.log("🔄 Refreshing dashboard manually...");
    const manager = window.dashboardManager;
    if (manager) {
        await manager.loadData();
    }
}

function goUpload() {
    window.location.href = "/upload";
}

function escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function escapeJs(text) {
    if (!text) return "";
    return text.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

// ============================================
// INITIALIZE
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    console.log("📄 DOM loaded");
    window.dashboardManager = new DashboardManager();
});

window.addEventListener("beforeunload", () => {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
});
