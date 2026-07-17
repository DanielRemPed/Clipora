# Clipora

## Run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open `http://127.0.0.1:5001`.

## Render deploy

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
gunicorn app:app
```
