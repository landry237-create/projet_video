/*
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
        
        await this.loadData();
        
        // Actualiser automatiquement toutes les 3 secondes
        autoRefreshInterval = setInterval(() => this.loadData(), 3000);
        
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
                                <span class="video-info-label">📽️ Sous-titres:</span>
                                <span>✓ VTT</span>
                            </div>
                        ` : ""}
                    </div>
                    
                    <div class="video-buttons">
                        ${video.subtitles_path ? `
                            <button class="btn btn-download" onclick="openSubtitlesModal('${this.escapeJs(fileId)}')">
                                📥 Voir Sous-titres
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

async function openSubtitlesModal(fileId) {
    try {
        console.log("📺 Opening subtitles for:", fileId);
        
        const response = await fetch(`/api/video/subtitles/${fileId}`);
        const data = await response.json();
        
        if (!data.success) {
            alert("Erreur: " + (data.error || "Sous-titres non disponibles"));
            return;
        }
        
        // Créer un modal avec les sous-titres
        showSubtitlesModal(data.content, fileId);
        
    } catch (error) {
        console.error("❌ Error:", error);
        alert(`Erreur: ${error.message}`);
    }
}

function showSubtitlesModal(vttContent, fileId) {
    const modal = document.createElement("div");
    modal.className = "modal";
    modal.style.cssText = "position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; border-radius: 15px; padding: 30px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); z-index: 1001; max-width: 600px; width: 90%; max-height: 70vh; overflow-y: auto;";
    
    const overlay = document.createElement("div");
    overlay.className = "modal-overlay";
    overlay.style.cssText = "position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.5); z-index: 1000;";
    
    modal.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3>📽️ Sous-titres VTT</h3>
            <button onclick="this.closest('.modal-overlay').parentElement.remove(); this.closest('.modal-overlay').remove();" style="background: none; border: none; font-size: 24px; cursor: pointer;">✕</button>
        </div>
        
        <div style="background: #f5f5f5; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; word-wrap: break-word; font-size: 12px; max-height: 400px; overflow-y: auto;">
            ${vttContent}
        </div>
        
        <div style="margin-top: 20px; display: flex; gap: 10px;">
            <button class="btn btn-download" onclick="downloadSubtitles('${fileId}', '${vttContent.replace(/'/g, "\\'")}')">
                📥 Télécharger
            </button>
            <button class="btn btn-cancel" onclick="this.closest('.modal-overlay').parentElement.remove(); this.closest('.modal-overlay').remove();">
                Fermer
            </button>
        </div>
    `;
    
    document.body.appendChild(overlay);
    overlay.appendChild(modal);
}

function downloadSubtitles(fileId, vttContent) {
    const blob = new Blob([vttContent], { type: "text/vtt;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${fileId}_subtitles.vtt`;
    link.click();
    URL.revokeObjectURL(link.href);
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
        
        await window.dashboardManager.loadData();
        
    } catch (error) {
        console.error("❌ Error:", error);
        alert(`Erreur: ${error.message}`);
    }
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
*/

setInterval(() => {
  console.log("❤️ heartbeat", new Date().toISOString());
}, 2000);
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

        this.isLoading = false;
        this.lastRenderedHTML = "";   // 🔒 empêche la destruction DOM inutile
        this.lastVideosHash = "";     // 🔒 empêche rerender logique

        this.init();
    }

    async init() {
        console.log("🚀 DashboardManager initialized");

        await this.loadData();

        // 🔄 Refresh raisonnable
        autoRefreshInterval = setInterval(() => this.loadData(), 1500000);
        console.log("🔄 Auto-refresh activé (15s)");
    }

    async loadData() {
        if (this.isLoading) {
            console.log("⏳ Load already in progress, skipping...");
            return;
        }

        this.isLoading = true;

        try {
            console.log("📊 Loading dashboard data...");

            const [videosResponse, statsResponse] = await Promise.all([
                fetch("/api/video/videos", { cache: "no-store" }),
                fetch("/api/dashboard/stats", { cache: "no-store" })
            ]);

            if (!videosResponse.ok) throw new Error(`HTTP ${videosResponse.status}`);
            if (!statsResponse.ok) throw new Error(`HTTP ${statsResponse.status}`);

            const videos = (await videosResponse.json()) || [];
            const stats = await statsResponse.json();

            // 🔐 Hash logique des vidéos (évite faux positifs JSON.stringify)
            const newHash = videos
                .map(v => `${v.file_id}|${v.status}|${v.language}|${v.animals}|${v.file_size}|${v.subtitles_path}`)
                .join("##");

            if (newHash !== this.lastVideosHash) {
                console.log("🔁 Videos changed → rerender");
                this.lastVideosHash = newHash;
                allVideos = videos;
                this.renderVideos(videos);
            } else {
                console.log("🛑 Videos unchanged → no rerender");
            }

            this.updateStats(stats);

        } catch (error) {
            console.error("❌ Error loading data:", error);
        } finally {
            this.isLoading = false;
        }
    }

    updateStats(stats) {
        this.totalVideosEl.textContent = stats.total_videos || 0;
        this.processedVideosEl.textContent = stats.processed || 0;
        this.storageUsedEl.textContent = stats.storage_used || "0 MB";
    }

    renderVideos(videos) {
        console.log("🎬 Rendering videos:", videos ? videos.length : 0);

        if (!videos || videos.length === 0) {
            if (this.lastRenderedHTML !== "EMPTY") {
                this.videosList.style.display = "none";
                this.emptyState.style.display = "block";
                this.videosList.innerHTML = "";
                this.lastRenderedHTML = "EMPTY";
            }
            return;
        }

        this.videosList.style.display = "flex";
        this.emptyState.style.display = "none";

        const cardsHTML = videos.map(v => this.createVideoCard(v)).join("");

        // 🔒 Ne touche au DOM que si visuellement différent
        if (cardsHTML !== this.lastRenderedHTML) {
            console.log("🧩 DOM update (visual diff)");
            this.videosList.innerHTML = cardsHTML;
            this.lastRenderedHTML = cardsHTML;
        } else {
            console.log("🛑 DOM unchanged → no flicker");
        }
    }

    createVideoCard(video) {
        const statusClass = video.status === "completed" ? "status-completed" : "status-processing";
        const statusText = video.status === "completed" ? "✅ Complété" : "⏳ En cours";

        const fileId = video.file_id || "unknown";
        const language = video.language || "Détection...";
        const animals = video.animals || "Détection...";

        return `
            <div class="video-card" data-id="${this.escapeHtml(fileId)}">
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
                            <span class="video-info-label">🗣 Langue:</span>
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
                                <span class="video-info-label">📽 Sous-titres:</span>
                                <span>✓ VTT</span>
                            </div>
                        ` : ""}
                    </div>

                    <div class="video-buttons">
                        ${video.subtitles_path ? `
                            <button class="btn btn-download" onclick="openSubtitlesModal('${this.escapeJs(fileId)}')">
                                📥 Voir Sous-titres
                            </button>
                        ` : ""}
                        <button class="btn btn-delete" onclick="openDeleteModal('${this.escapeJs(fileId)}')">
                            🗑 Supprimer
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

// --------------------
// Global functions
// --------------------

async function refreshDashboard() {
    const manager = window.dashboardManager;
    if (manager) {
        await manager.loadData();
    }
}

async function openSubtitlesModal(fileId) {
    try {
        const response = await fetch(`/api/video/subtitles/${fileId}`);
        const data = await response.json();

        if (!data.success) {
            alert("Erreur: " + (data.error || "Sous-titres non disponibles"));
            return;
        }

        showSubtitlesModal(data.content, fileId);

    } catch (error) {
        console.error("❌ Error:", error);
        alert(`Erreur: ${error.message}`);
    }
}

function showSubtitlesModal(vttContent, fileId) {
    const modal = document.createElement("div");
    modal.className = "modal";
    modal.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        z-index: 1001;
        max-width: 600px;
        width: 90%;
        max-height: 70vh;
        overflow-y: auto;
    `;

    const overlay = document.createElement("div");
    overlay.className = "modal-overlay";
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1000;
    `;

    modal.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
            <h3>📽 Sous-titres VTT</h3>
            <button onclick="this.closest('.modal-overlay').parentElement.remove(); this.closest('.modal-overlay').remove();"
                style="background:none;border:none;font-size:24px;cursor:pointer;">✕</button>
        </div>

        <div style="background:#f5f5f5;padding:15px;border-radius:10px;font-family:monospace;
                    white-space:pre-wrap;word-wrap:break-word;font-size:12px;max-height:400px;overflow-y:auto;">
            ${vttContent}
        </div>

        <div style="margin-top:20px;display:flex;gap:10px;">
            <button class="btn btn-download" onclick="downloadSubtitles('${fileId}', \`${vttContent.replace(/`/g, "\\`")}\`)">
                📥 Télécharger
            </button>
            <button class="btn btn-cancel"
                onclick="this.closest('.modal-overlay').parentElement.remove(); this.closest('.modal-overlay').remove();">
                Fermer
            </button>
        </div>
    `;

    document.body.appendChild(overlay);
    overlay.appendChild(modal);
}

function downloadSubtitles(fileId, vttContent) {
    const blob = new Blob([vttContent], { type: "text/vtt;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${fileId}_subtitles.vtt`;
    link.click();
    URL.revokeObjectURL(link.href);
}

function openDeleteModal(fileId) {
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
        const response = await fetch(`/api/video/delete/${deleteFileId}`, {
            method: "DELETE"
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || "Erreur lors de la suppression");
        }

        closeDeleteModal();
        await window.dashboardManager.loadData();

    } catch (error) {
        console.error("❌ Error:", error);
        alert(`Erreur: ${error.message}`);
    }
}

function goUpload() {
    window.location.href = "/upload";
}

// --------------------
// Init & cleanup
// --------------------

document.addEventListener("DOMContentLoaded", () => {
    window.dashboardManager = new DashboardManager();
});

window.addEventListener("beforeunload", () => {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
});
