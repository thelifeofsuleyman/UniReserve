"""Start UniReserve with Waitress on this computer (no Flask development server).

This localhost convenience launcher is not a public HTTPS deployment.
"""
from pathlib import Path
import os
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
os.environ.setdefault("UNIRESERVE_MODE","local")
os.environ.setdefault("UNIRESERVE_AUTO_SAMPLE_CATALOG","1")

from waitress import serve
from unireserve.web.app import create_app

if __name__=="__main__":
    app=create_app()
    port=int(os.environ.get("UNIRESERVE_PORT","5000"))
    print(f"UniReserve: http://127.0.0.1:{port}")
    serve(app,host="127.0.0.1",port=port,threads=4)
