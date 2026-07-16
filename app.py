from flask import Flask, render_template, session, url_for, request, redirect
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import os
import uuid
import qrcode

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            event_code TEXT UNIQUE NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        event_id INTEGER NOT NULL,
        user_id INTEGER,
        uploaded_at TEXT NOT NULL,
        FOREIGN KEY (event_id) REFERENCES events(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

def create_qr(event_code):

    #For deployment on render: 
    url = f"https://clipora-1.onrender.com/guest_upload/{event_code}"
    
    #For virtual environment:
    #url = f"http://127.0.0.1:5001/guest_upload/{event_code}"

    img = qrcode.make(url)

    os.makedirs("static/qrcodes", exist_ok=True)

    img.save(
        f"static/qrcodes/{event_code}.png"
    )

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

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, event_code FROM events WHERE user_id = ?",
        (session["user_id"],)
    )

    events = cursor.fetchall()

    conn.close()


    selected_event = request.args.get("event_id")


    if request.method == "POST":

        file = request.files.get("media")
        event_id = request.form.get("event_id")

        # keep selected event after submit/error
        selected_event = event_id


        if not event_id:
            return render_template(
                "upload.html",
                error="Please select an event.",
                events=events,
                selected_event=selected_event
            )


        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)

            # Get event_code
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            cursor.execute(
                "SELECT event_code FROM events WHERE id = ?",
                (event_id,)
            )

            event_code = cursor.fetchone()[0]

            conn.close()

            # Save using event_code
            event_folder = os.path.join(
                app.config["UPLOAD_FOLDER"],
                event_code
            )

            os.makedirs(event_folder, exist_ok=True)

            file.save(
                os.path.join(event_folder, filename)
            )


            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()


            cursor.execute(
                """
                INSERT INTO uploads 
                (filename, event_id, user_id, uploaded_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    filename,
                    event_id,
                    session["user_id"],
                    datetime.now()
                )
            )


            conn.commit()
            conn.close()


            return redirect(url_for("dashboard"))


        return render_template(
            "upload.html",
            error="Please upload a valid photo or video file.",
            events=events,
            selected_event=selected_event
        )


    return render_template(
        "upload.html",
        events=events,
        selected_event=selected_event
    )
    
@app.route("/create_event", methods=["GET", "POST"])
def create_event():
    
    if "user_id" not in session:
        return redirect(url_for("login")) 
    
    if request.method == "POST":
        name = request.form.get("name")

        if not name:
            return render_template(
                "create_event.html",
                error="Please enter an event name"
            )

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        event_code = str(uuid.uuid4())[:8]

        cursor.execute("INSERT INTO events (name, date, user_id, event_code) VALUES (?, ?, ?, ?)",
            (name, datetime.now(), session["user_id"], event_code))

        conn.commit()
        conn.close()

        create_qr(event_code)

        return redirect(url_for("dashboard"))

    return render_template("create_event.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Get user's events
    cursor.execute(
        "SELECT id, name, date, event_code FROM events WHERE user_id = ?",
        (session["user_id"],)
    )

    events = cursor.fetchall()

    event_media = {}

    for event in events:
        event_id = event[0]
        event_code = event[3]

        cursor.execute(
            """
            SELECT filename, uploaded_at 
            FROM uploads
            WHERE event_id = ? AND user_id = ?
            ORDER BY uploaded_at DESC
            """,
            (event_id, session["user_id"])
        )

        media = cursor.fetchall()

        event_media[event_id] = []

        for item in media:
            filename = item[0]

            event_media[event_id].append({
                "name": filename,
                "url": url_for(
                    "static",
                    filename=f"uploads/{event_code}/{filename}"
                ),
                "is_video": filename.lower().endswith(
                    ("mp4", "mov", "webm")
                ),
                "uploaded_at": item[1]
            })

    conn.close()

    return render_template(
        "dashboard.html",
        events=events,
        event_media=event_media
    )

@app.route("/timeline")
def timeline():
    if "user_id" not in session:
        return redirect(url_for("login"))

    uploaded_files = []

    user_folder = os.path.join(
        app.config["UPLOAD_FOLDER"],
        str(session["user_id"])
    )

    if os.path.exists(user_folder):

        for event_id in os.listdir(user_folder):

            event_folder = os.path.join(
                user_folder,
                event_id
            )

            if os.path.isdir(event_folder):

                for filename in os.listdir(event_folder):

                    if allowed_file(filename):

                        file_path = os.path.join(
                            event_folder,
                            filename
                        )

                        upload_time = os.path.getmtime(file_path)

                        uploaded_files.append({
                            "name": filename,
                            "url": url_for(
                                "static",
                                filename=f"uploads/{event_id}/{filename}"
                            ),
                            "is_video": filename.lower().endswith(
                                ("mp4", "mov", "webm")
                            ),
                            "timestamp": upload_time,
                            "uploaded_at": datetime.fromtimestamp(upload_time).strftime(
                                "%B %d, %Y at %I:%M %p"
                            )
                        })

    uploaded_files.sort(key=lambda file: file["timestamp"])

    return render_template("timeline.html", files=uploaded_files)

@app.route("/guest_upload/<event_code>", methods=["GET","POST"])
def guest_upload(event_code):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name
        FROM events
        WHERE event_code = ?
        """,
        (event_code,)
    )

    event = cursor.fetchone()

    conn.close()

    if not event:
        return "Invalid event"

    event_id = event[0]

    if request.method == "POST":

        file = request.files.get("media")

        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)

            event_folder = os.path.join(
                app.config["UPLOAD_FOLDER"],
                event_code
            )

            os.makedirs(event_folder, exist_ok=True)

            file.save(
                os.path.join(event_folder, filename)
            )

            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO uploads
                (filename, event_id, user_id, uploaded_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    filename,
                    event_id,
                    None,
                    datetime.now()
                )
            )

            conn.commit()
            conn.close()

            return "Upload successful!"

    return render_template(
        "guest_upload.html",
        event=event
    )

@app.route("/event/<int:event_id>")
def event_page(event_id):
    
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, date, event_code
        FROM events
        WHERE id = ? AND user_id = ?
        """,
        (event_id, session["user_id"])
    )

    event = cursor.fetchone()

    if not event:
        conn.close()
        return "Event not found"

    cursor.execute(
        """
        SELECT filename, uploaded_at
        FROM uploads
        WHERE event_id = ?
        ORDER BY uploaded_at ASC
        """,
        (event_id,)
    )

    media = cursor.fetchall()

    print("EVENT PAGE LOADED:", event_id)
    print("EVENT:", event)
    print("MEDIA:", media)

    conn.close()

    return render_template(
        "event.html",
        event=event,
        media=media
    )
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
