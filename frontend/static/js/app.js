class VideoUploadManager {
    constructor() {
        this.uploadArea = document.getElementById("uploadArea");
        this.fileInput = document.getElementById("fileInput");
        this.progressSection = document.getElementById("progressSection");
        this.progressFill = document.getElementById("progressFill");
        this.progressStep = document.getElementById("progressStep");
        this.progressPercentage = document.getElementById("progressPercentage");
        this.successAlert = document.getElementById("successAlert");
        this.errorAlert = document.getElementById("errorAlert");
        this.errorText = document.getElementById("errorText");
        
        this.ws = null;
        this.isProcessing = false;
        
        this.init();
    }
    
    init() {
        // Click to upload
        this.uploadArea.addEventListener("click", () => this.fileInput.click());
        
        // Drag and drop
        this.uploadArea.addEventListener("dragover", (e) => this.onDragOver(e));
        this.uploadArea.addEventListener("dragleave", (e) => this.onDragLeave(e));
        this.uploadArea.addEventListener("drop", (e) => this.onDrop(e));
        
        // File input change
        this.fileInput.addEventListener("change", () => this.handleFile());
        
        console.log("✅ VideoUploadManager initialized");
    }
    
    onDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadArea.classList.add("dragover");
    }
    
    onDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadArea.classList.remove("dragover");
    }
    
    onDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadArea.classList.remove("dragover");
        this.fileInput.files = e.dataTransfer.files;
        this.handleFile();
    }
    
    async handleFile() {
        const file = this.fileInput.files[0];
        if (!file) return;
        
        console.log("📤 File selected:", file.name, `(${(file.size / 1024 / 1024).toFixed(2)} MB)`);
        
        this.hideAlerts();
        this.isProcessing = true;
        
        try {
            await this.uploadFile(file);
        } catch (error) {
            this.showError(error.message);
            this.isProcessing = false;
        }
    }
    
    async uploadFile(file) {
        const formData = new FormData();
        formData.append("file", file);
        
        console.log("🔄 POST /api/video/upload");
        
        const response = await fetch("/api/video/upload", {
            method: "POST",
            body: formData
        });
        
        console.log(`📊 Status: ${response.status}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || error.detail || "Erreur upload");
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || "Upload échoué");
        }
        
        console.log("✅ Upload OK:", data);
        
        const fileId = data.file_id;
        
        // Show progress
        this.showProgress();
        
        // Start WebSocket
        await this.connectWebSocket(fileId);
    }
    
    async connectWebSocket(fileId) {
        return new Promise((resolve, reject) => {
            const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
            const wsUrl = `${protocol}//localhost:8000/api/video/ws/process/${fileId}`;
            console.log("🔌 Connecting WebSocket:", wsUrl);
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log("✅ WebSocket connected");
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const progress = JSON.parse(event.data);
                    console.log("📊 Progress:", progress);
                    this.updateProgress(progress);
                    
                    if (progress.percentage === 100) {
                        this.showSuccess();
                        setTimeout(() => window.location.href = "/dashboard", 2000);
                    }
                } catch (error) {
                    console.error("❌ Parse error:", error);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error("❌ WebSocket error:", error);
                this.showError("Erreur WebSocket");
                reject(error);
            };
            
            this.ws.onclose = () => {
                console.log("🔌 WebSocket closed");
                this.isProcessing = false;
                resolve();
            };
        });
    }
    
    updateProgress(progress) {
        const percentage = Math.min(progress.percentage, 100);
        this.progressFill.style.width = percentage + "%";
        this.progressFill.textContent = percentage + "%";
        this.progressPercentage.textContent = percentage + "%";
        this.progressStep.textContent = `${progress.step.toUpperCase()}: ${progress.message}`;
    }
    
    showProgress() {
        this.progressSection.classList.add("active");
    }
    
    hideAlerts() {
        this.successAlert.classList.remove("show");
        this.errorAlert.classList.remove("show");
    }
    
    showSuccess() {
        this.successAlert.classList.add("show");
    }
    
    showError(message) {
        this.errorText.textContent = `❌ ${message}`;
        this.errorAlert.classList.add("show");
    }
}

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    new VideoUploadManager();
});

// Navigation
function goHome() {
    window.location.href = "/";
}

function goDashboard() {
    window.location.href = "/dashboard";
}