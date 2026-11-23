"""Waitress WSGI entry point for a managed HTTPS reverse proxy.

Explicitly use UNIRESERVE_MODE=production. This launcher binds localhost only;
your reverse proxy must manage HTTPS and the public domain.
"""
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

if os.environ.get("UNIRESERVE_MODE") != "production":
    raise SystemExit("Set UNIRESERVE_MODE=production and configure the documented secret/hosts first.")

from waitress import serve
from unireserve.web.app import create_app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("UNIRESERVE_PORT", "8080"))
    serve(app, host="127.0.0.1", port=port, threads=4)
