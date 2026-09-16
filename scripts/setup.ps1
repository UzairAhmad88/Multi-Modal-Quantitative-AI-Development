# Multi-Modal Quant AI Environment Setup Script for Windows PowerShell (Phase 30)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  MULTI-MODAL QUANT AI — SETUP & DEPENDENCY INSTALLATION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if (-not (Test-Path ".venv")) {
    Write-Host "[+] Creating Virtual Environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
}

Write-Host "[+] Activating Virtual Environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

Write-Host "[+] Upgrading Pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host "[+] Installing Core Dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "[SUCCESS] Setup complete! Run .\scripts\health_check.ps1 to verify environment." -ForegroundColor Green
