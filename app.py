import os, json, subprocess
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

MEDIA_DIR = "media"
SCENE_FILE = "scenes.json"
FFMPEG = None
YOUTUBE_RTMP = "rtmp://a.rtmp.youtube.com/live2"

os.makedirs("media/images", exist_ok=True)
os.makedirs("media/videos", exist_ok=True)
os.makedirs("media/audio", exist_ok=True)

if not os.path.exists(SCENE_FILE):
    with open(SCENE_FILE, "w") as f:
        json.dump([], f)

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    ftype = request.form["type"]
    path = f"{MEDIA_DIR}/{ftype}/{file.filename}"
    file.save(path)
    return jsonify({"path": path})

@app.route("/scene", methods=["GET", "POST"])
def scene():
    if request.method == "POST":
        with open(SCENE_FILE, "w") as f:
            json.dump(request.json, f)
        return "ok"
    with open(SCENE_FILE) as f:
        return jsonify(json.load(f))

@app.route("/start", methods=["POST"])
def start():
    global FFMPEG
    key = request.json["key"]

    cmd = [
        "ffmpeg",
        "-re",
        "-f", "x11grab",
        "-s", "1280x720",
        "-i", ":0.0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-b:v", "3000k",
        "-pix_fmt", "yuv420p",
        "-g", "60",
        "-f", "flv",
        f"{YOUTUBE_RTMP}/{key}"
    ]

    FFMPEG = subprocess.Popen(cmd)
    return "started"

@app.route("/stop")
def stop():
    global FFMPEG
    if FFMPEG:
        FFMPEG.terminate()
        FFMPEG = None
    return "stopped"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
