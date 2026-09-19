import os
import sys
import tempfile
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

from src.api_app import app

# Export app for Vercel Serverless Function
app = app
