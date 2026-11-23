"""Start the local-only UniReserve web demo: python scripts/run_web.py"""
from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from unireserve.web.app import create_app

if __name__ == "__main__":
    # The normal local demo repairs an old starter database on its first run.
    # Set UNIRESERVE_AUTO_SAMPLE_CATALOG=0 to keep a custom catalogue unchanged.
    os.environ.setdefault("UNIRESERVE_AUTO_SAMPLE_CATALOG", "1")
    app = create_app()
    print("UniReserve: open http://127.0.0.1:5000 in your browser")
    print("Local development demo only. Do not expose this server to the internet.")
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
