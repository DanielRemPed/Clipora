from flask import Flask, render_template, url_for, request, redirect
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "mov", "webm"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("media")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return redirect(url_for("dashboard"))

        return render_template("upload.html", error="Please upload a valid photo or video file.")

    return render_template("upload.html")


@app.route("/dashboard")
def dashboard():
    uploaded_files = []

    for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
        if allowed_file(filename):
            uploaded_files.append({
                "name": filename,
                "url": url_for("static", filename=f"uploads/{filename}"),
                "is_video": filename.lower().endswith(("mp4", "mov", "webm"))
            })

    return render_template("dashboard.html", files=uploaded_files)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)