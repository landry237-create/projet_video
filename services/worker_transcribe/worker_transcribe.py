from flask import Flask, request, jsonify
import whisper
import os
import tempfile
import uuid

app = Flask(__name__)
model = whisper.load_model("small")  # small works on CPU; change to base/tiny for speed

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    path = data.get("path")
    if not path or not os.path.exists(path):
        return jsonify({"error":"file not found", "path": path}), 400
    try:
        # transcribe (extract audio implicitly)
        result = model.transcribe(path)
        transcript = result.get("text", "")
        return jsonify({"transcript": transcript, "full_result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082)
