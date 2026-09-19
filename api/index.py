import os
import sys
import tempfile
import traceback
from pathlib import Path

# Set writable cache directories for serverless environments (Vercel / AWS Lambda)
tmp_dir = tempfile.gettempdir()
os.environ["YFINANCE_CACHE_DIR"] = os.path.join(tmp_dir, "yfinance")
os.environ["MPLCONFIGDIR"] = os.path.join(tmp_dir, "matplotlib")
os.environ["NUMBA_CACHE_DIR"] = os.path.join(tmp_dir, "numba")

# Add project root directory to sys.path so modules like `src` can be imported
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from api.main import app as main_app
    app = main_app
except Exception as e:
    from fastapi import FastAPI
    app = FastAPI()
    err_msg = str(e)
    tb_msg = traceback.format_exc()

    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
    def fallback(full_path: str):
        return {"status": "error", "error": err_msg, "traceback": tb_msg}

handler = app
