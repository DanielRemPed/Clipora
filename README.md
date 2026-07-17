# Clipora - A Collaborative Event Gallery

Clipora is a web application built with Flask that helps event organizers collect photos and videos from guests in one shared gallery. Instead of asking guests to send media through texts, email, or group chats, Clipora creates a unique QR code for each event so guests can upload directly to the correct event page.

## Features

### Account Management

- Create Account: Users can register for an account.
- Login: Users can log in to manage their events.
- Logout: Users can safely log out when finished.

### Event Management

- Create Event: Users can create a separate gallery for each event.
- QR Code Generation: Each event gets its own QR code for guest uploads.
- Event Dashboard: Users can view all of their created events in one place.
- Delete Event: Users can remove an event if it is no longer needed.

### Media Uploads

- Upload Photos: Users and guests can upload image files to an event.
- Upload Videos: Users and guests can upload video files to an event.
- Guest Upload Page: Guests can upload media without creating an account.
- File Organization: Uploaded files are saved under the correct event.

### Gallery and Timeline

- Event Gallery: Each event has a page that displays uploaded media.
- Timeline View: Uploaded media appears in a clean timeline layout.
- Full-Size Preview: Photos can be opened in a larger view.
- Delete Media: Users can delete photos or videos that were uploaded by mistake.

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- QRCode
- Gunicorn
- Render

## Getting Started

> Clipora can be run locally with Python and can also be deployed online with Render.

### Running Locally

1. Clone the repository:

```bash
git clone https://github.com/DanielRemPed/Clipora.git
```

2. Move into the project folder:

```bash
cd Clipora
```

3. Create a virtual environment:

```bash
python3 -m venv venv
```

4. Activate the virtual environment:

```bash
source venv/bin/activate
```

5. Install the required packages:

```bash
pip install -r requirements.txt
```

6. Run the application:

```bash
python3 app.py
```

7. Open the application in a browser:

```text
http://127.0.0.1:5001
```

## Deployment

Clipora can be deployed on Render as a web service.

### Render Settings

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
gunicorn app:app
```

After deployment, the public Render URL can be used for QR codes so guests can scan and upload from their phones.

## Project Structure

```text
Clipora/
├── app.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── README.md
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── create_event.html
│   ├── event.html
│   ├── guest_upload.html
│   └── timeline.html
└── static/
    ├── css/
    │   └── styles.css
    ├── uploads/
    └── qrcodes/
```


## Team Members

- Om Patel
- Noah
- Daniel Remigio

## Purpose

Clipora was created as a software engineering group project. The project focuses on building a useful web application with user accounts, event creation, QR code sharing, media uploads, and a simple gallery system.
