import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_frontend_files_exist():
    html_path = ROOT / "frontend" / "index.html"
    css_path = ROOT / "frontend" / "css" / "style.css"
    api_js_path = ROOT / "frontend" / "js" / "api.js"
    app_js_path = ROOT / "frontend" / "js" / "app.js"

    assert html_path.exists()
    assert css_path.exists()
    assert api_js_path.exists()
    assert app_js_path.exists()

def test_streamlit_dashboard_pages_exist():
    pages_dir = ROOT / "dashboard" / "pages"
    assert pages_dir.exists()
    pages = list(pages_dir.glob("*.py"))
    assert len(pages) >= 12
