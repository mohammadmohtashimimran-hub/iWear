"""Run the Flask app (from project root: python backend/run.py or from backend: python run.py)."""
import os
import sys
from pathlib import Path

_backend_dir = Path(__file__).resolve().parent
_root = _backend_dir.parent

# Ensure only backend is used for imports so "app" is always backend.app
if str(_backend_dir) in sys.path:
    sys.path.remove(str(_backend_dir))
sys.path.insert(0, str(_backend_dir))

# Optional: load .env from project root (config.py also loads from root)
_root_env = _root / ".env"
if _root_env.exists():
    from dotenv import load_dotenv
    load_dotenv(_root_env)

# Import app from backend only (backend/app/__init__.py)
from app import create_app

app = create_app()


# Root route: show simple page so user knows where to open the web app
@app.route("/")
def index():
    from flask import Response
    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>iWear API</title></head>
<body style="font-family:sans-serif; max-width:600px; margin:2rem auto; padding:1rem;">
  <h1>iWear API</h1>
  <p>Backend is running. This is the <strong>API</strong> (port 5000).</p>
  <p>To use the <strong>Web App</strong> (storefront), run in another terminal:</p>
  <pre style="background:#eee; padding:1rem;">cd frontend
npm install
npm run dev</pre>
  <p>Then open: <a href="http://localhost:3000">http://localhost:3000</a></p>
  <p><a href="/api/health">API health</a></p>
</body></html>"""
    return Response(html, mimetype="text/html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
