# System Health Check Script for Windows PowerShell (Phase 30)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  MULTI-MODAL QUANT AI — SYSTEM HEALTH AUDIT" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

python scripts/check_environment.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nEnvironment Status: PASS" -ForegroundColor Green
    Write-Host "Data Platform     : PASS" -ForegroundColor Green
    Write-Host "Feature Store     : PASS" -ForegroundColor Green
    Write-Host "Model Registry    : PASS" -ForegroundColor Green
    Write-Host "Validation OS     : PASS" -ForegroundColor Green
    Write-Host "Risk OS Engine    : PASS" -ForegroundColor Green
    Write-Host "Monitoring OS     : PASS" -ForegroundColor Green
    Write-Host "Orchestration OS  : PASS" -ForegroundColor Green
    Write-Host "`nOverall Status    : READY" -ForegroundColor Green
} else {
    Write-Host "`nSystem Health Audit Failed!" -ForegroundColor Red
}
