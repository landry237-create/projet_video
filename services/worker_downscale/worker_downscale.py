from flask import Flask, request, jsonify
import os
from moviepy.editor import VideoFileClip
import uuid

app = Flask(__name__)
SHARED_DIR = os.getenv("SHARED_DIR", "/data")
os.makedirs(SHARED_DIR, exist_ok=True)

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    path = data.get("path")
    if not path or not os.path.exists(path):
        return jsonify({"error":"file not found", "path": path}), 400

    try:
        clip = VideoFileClip(path)
        # downscale width to 720 while keeping aspect ratio
        target_width = 720
        w, h = clip.size
        if w > target_width:
            new_h = int(target_width * h / w)
            clip_resized = clip.resize(newsize=(target_width, new_h))
        else:
            clip_resized = clip

        out_name = os.path.join(SHARED_DIR, f"{uuid.uuid4().hex}_downscaled.mp4")
        clip_resized.write_videofile(out_name, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        clip.close()
        return jsonify({"output": out_name, "width": clip_resized.w, "height": clip_resized.h})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
