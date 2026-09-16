# Safe Cache Clean Script for Windows PowerShell (Phase 30)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  MULTI-MODAL QUANT AI — SAFE CACHE CLEANUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Get-ChildItem -Path . -Include __pycache__, .pytest_cache -Recurse -Force | Remove-Item -Recurse -Force

Write-Host "[SUCCESS] Pycache and pytest cache cleaned safely! (Research artifacts and datasets preserved)." -ForegroundColor Green
