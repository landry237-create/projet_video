/*document.getElementById("videoFile").addEventListener("change", function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const preview = document.getElementById("preview");
    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";
});


document.getElementById("processBtn").onclick = async function () {
    const file = document.getElementById("videoFile").files[0];

    if (!file) {
        alert("Veuillez sélectionner un fichier vidéo !");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const progressBar = document.getElementById("progressBar");
    const resultBox = document.getElementById("uploadResult");

    resultBox.innerHTML = "";
    progressBar.style.width = "0%";

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/video/process");

    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
            const percent = (e.loaded / e.total) * 100;
            progressBar.style.width = percent + "%";
        }
    };

    xhr.onload = function() {
        if(xhr.status === 200){
            const data = JSON.parse(xhr.responseText);
            resultBox.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        } else {
            resultBox.innerHTML = "<p style='color:red'>Erreur lors du traitement.</p>";
        }
    };

    xhr.send(formData);
};
*/

document.getElementById("processBtn").onclick = async () => {

    const file = document.getElementById("videoFile").files[0];
    const resultBox = document.getElementById("uploadResult");
    resultBox.innerHTML = "";

    if (!file) {
        alert("Choisissez une vidéo !");
        return;
    }

    // 1) UPLOAD DU FICHIER
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/api/video/upload", {
        method: "POST",
        headers:{
            'content-Type': 'multipart/form-Data'
        },
        body: formData
    });

    const data = await res.json();
    const jobId = data.job_id;

    resultBox.innerHTML += "<p><b>Analyse en temps réel :</b></p>";

    // 2) STREAMING EN TEMPS RÉEL
    const evtSource = new EventSource(`/api/video/stream_status/${jobId}`);

    evtSource.onmessage = function (event) {
        const message = event.data;

        resultBox.innerHTML += `<p>${message}</p>`;
        resultBox.scrollTop = resultBox.scrollHeight;

        if (message.includes("Traitement terminé")) {
            evtSource.close();
        }
    };
};
