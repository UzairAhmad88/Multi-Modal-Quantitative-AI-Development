"""
Automated Environment & Dependency Audit Script for Multi-Modal Quant AI Platform (Phase 30).
"""

import sys
import importlib

def check_environment():
    print("=" * 60)
    print("  MULTI-MODAL QUANT AI — ENVIRONMENT & DEPENDENCY CHECK")
    print("=" * 60)
    
    print(f"[+] Python Version: {sys.version.split()[0]} ({sys.platform})")
    assert sys.version_info >= (3, 10), "Python 3.10+ required!"

    dependencies = [
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("scipy", "SciPy"),
        ("sklearn", "Scikit-Learn"),
        ("torch", "PyTorch"),
        ("xgboost", "XGBoost"),
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("streamlit", "Streamlit"),
        ("plotly", "Plotly"),
        ("pytest", "Pytest"),
    ]

    all_passed = True
    for module_name, display_name in dependencies:
        try:
            mod = importlib.import_module(module_name)
            ver = getattr(mod, "__version__", "installed")
            print(f"  [OK]   {display_name:<20}: {ver}")
        except ImportError:
            print(f"  [FAIL] {display_name:<20}: NOT INSTALLED")
            all_passed = False

    print("-" * 60)
    import torch
    cuda_avail = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda_avail else "CPU Mode (Verified Laptop-First)"
    print(f"[+] PyTorch Execution Device: {device_name}")

    print("-" * 60)
    if all_passed:
        print("[SUCCESS] Environment check passed. All core packages ready!")
        return 0
    else:
        print("[ERROR] Missing required dependencies!")
        return 1

if __name__ == "__main__":
    sys.exit(check_environment())
