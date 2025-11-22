from flask import Flask, request, jsonify
import os, uuid, math
import pysrt

app = Flask(__name__)
SHARED_DIR = os.getenv("SHARED_DIR", "/data")
os.makedirs(SHARED_DIR, exist_ok=True)

def naive_split_transcript(transcript, words_per_block=12):
    words = transcript.strip().split()
    blocks = []
    for i in range(0, len(words), words_per_block):
        blocks.append(" ".join(words[i:i+words_per_block]))
    return blocks

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    path = data.get("path")
    transcription = data.get("transcription", {})
    # transcription could be dict or string
    if isinstance(transcription, dict):
        transcript = transcription.get("transcript") or transcription.get("text") or ""
    else:
        transcript = transcription or ""

    if not os.path.exists(path):
        return jsonify({"error":"file not found"}), 400

    if not transcript:
        return jsonify({"error":"no transcript provided"}), 400

    try:
        blocks = naive_split_transcript(transcript, words_per_block=12)
        subs = pysrt.SubRipFile()
        # estimate duration via video length
        import moviepy.editor as mp
        clip = mp.VideoFileClip(path)
        duration = clip.duration
        clip.close()
        per_block = max(1.0, duration / max(1, len(blocks)))
        start = 0.0
        for i, b in enumerate(blocks, start=1):
            end = start + per_block
            # convert to h,m,s,ms
            def to_srt_time(t):
                h = int(t // 3600)
                m = int((t % 3600) // 60)
                s = int(t % 60)
                ms = int((t - int(t)) * 1000)
                return pysrt.SubRipTime(hours=h, minutes=m, seconds=s, milliseconds=ms)
            subs.append(pysrt.SubRipItem(index=i, start=to_srt_time(start), end=to_srt_time(end), text=b))
            start = end
        out_srt = os.path.join(SHARED_DIR, f"{uuid.uuid4().hex}.srt")
        subs.save(out_srt, encoding='utf-8')
        return jsonify({"srt": out_srt})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8083)
