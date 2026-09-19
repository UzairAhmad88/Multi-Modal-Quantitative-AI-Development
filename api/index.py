import os
import sys
import tempfile
from pathlib import Path

# Force all user/cache directories to writable /tmp for AWS Lambda / Vercel
os.environ["HOME"] = "/tmp"
os.environ["XDG_CACHE_HOME"] = "/tmp/.cache"
os.environ["XDG_CONFIG_HOME"] = "/tmp/.config"
os.environ["XDG_DATA_HOME"] = "/tmp/.data"
os.environ["TMPDIR"] = "/tmp"
os.environ["YFINANCE_CACHE_DIR"] = "/tmp/yfinance"
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"
os.environ["NUMBA_CACHE_DIR"] = "/tmp/numba"

# Add project root directory to sys.path so modules like `src` can be imported
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.api_app import app

# Export app for Vercel Serverless Function
app = app
