# Run Development Experiment Pipeline Script for Windows PowerShell (Phase 30)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  MULTI-MODAL QUANT AI — RUN DEVELOPMENT PIPELINE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

python orchestration/cli/run.py --config orchestration/configs/development.yaml --symbols AAPL MSFT --experiment-id EXP-DEV-PROD-001
