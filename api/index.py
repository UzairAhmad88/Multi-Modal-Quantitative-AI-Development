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
    from api.main import app
except Exception as e:
    print(f"FATAL ERROR IMPORTING APP: {e}", file=sys.stderr)
    traceback.print_exc()
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/{full_path:path}")
    def fallback_error(full_path: str):
        return {
            "status": "error",
            "message": f"Initialization error: {str(e)}",
            "traceback": traceback.format_exc()
        }

handler = app
