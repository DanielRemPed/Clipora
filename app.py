from flask import Flask, render_template, session, url_for, request, redirect
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)

app.secret_key = "clipora_secret_key"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "mov", "webm"}

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("register.html", error="Please enter a username and password.")

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashed_password)
            )

            conn.commit()
            conn.close()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            return render_template("register.html", error="Username already exists. Please choose a different username.")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,)
        )

        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid username or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/upload", methods=["GET", "POST"])
def upload():

    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        file = request.files.get("media")

        if file and allowed_file(file.filename):
            
            filename = secure_filename(file.filename)

            user_folder = os.path.join(app.config["UPLOAD_FOLDER"], str(session["user_id"]))

            os.makedirs(user_folder, exist_ok=True)

            file.save(os.path.join(user_folder, filename))

            return redirect(url_for("dashboard"))

        return render_template("upload.html", error="Please upload a valid photo or video file.")

    return render_template("upload.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    uploaded_files = []

    user_folder = os.path.join(
        app.config["UPLOAD_FOLDER"],
        str(session["user_id"])
    )

    if os.path.exists(user_folder):
        for filename in os.listdir(user_folder):
            if allowed_file(filename):
                uploaded_files.append({
                    "name": filename,
                    "url": url_for("static", filename=f"uploads/{session['user_id']}/{filename}"),
                    "is_video": filename.lower().endswith(("mp4", "mov", "webm"))
                })

    return render_template("dashboard.html", files=uploaded_files)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
