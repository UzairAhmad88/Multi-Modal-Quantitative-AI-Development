import importlib.util
from pathlib import Path

def test_dashboard_pages_syntax():
    pages_dir = Path(__file__).resolve().parents[1] / "dashboard" / "pages"
    for page_path in pages_dir.glob("*.py"):
        spec = importlib.util.spec_from_file_location(page_path.stem, page_path)
        assert spec is not None
        mod = importlib.util.module_from_spec(spec)
        assert mod is not None
