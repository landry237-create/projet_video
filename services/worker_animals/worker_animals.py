from flask import Flask, request, jsonify
import os, uuid, cv2, tempfile
from ultralytics import YOLO

app = Flask(__name__)
model = YOLO("yolov8n.pt")  # tiny model; ensure it's available or will be downloaded
SHARED_DIR = os.getenv("SHARED_DIR", "/data")

def extract_frames(video_path, n_frames=5):
    cap = cv2.VideoCapture(video_path)
    frames = []
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total == 0:
        cap.release()
        return frames
    indices = [max(0, int(total * i / max(1,n_frames-1))) for i in range(n_frames)]
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    cap.release()
    return frames

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    path = data.get("path")
    if not path or not os.path.exists(path):
        return jsonify({"error":"file not found"}), 400
    try:
        frames = extract_frames(path, n_frames=8)
        animals_detected = {}
        for i, f in enumerate(frames):
            res = model.predict(source=f, save=False, imgsz=640, verbose=False)
            # res is list-like; inspect boxes
            for r in res:
                for box in r.boxes:
                    cls = int(box.cls.cpu().numpy()[0]) if hasattr(box.cls, 'cpu') else int(box.cls)
                    name = r.names.get(cls, str(cls))
                    # basic filter: common animal names in COCO dataset
                    animals = ["bird","cat","dog","horse","sheep","cow","elephant","bear","zebra","giraffe"]
                    if name in animals:
                        animals_detected[name] = animals_detected.get(name, 0) + 1

        return jsonify({"animals": animals_detected})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8084)



"""
Remarque : YOLOv8 et ultralytics télécharge des poids la première fois.
Dans un contexte entreprise, tu stockes ces poids dans un volume partagé ou dans un dépôt de modèles.
"""