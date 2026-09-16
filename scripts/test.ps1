# Master Test Runner Script for Windows PowerShell (Phase 30)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  MULTI-MODAL QUANT AI — MASTER TEST SUITE RUNNER" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

python -m pytest tests/orchestration/test_full_pipeline.py tests/monitoring/test_monitoring_engine.py tests/validation/test_walk_forward_engine.py tests/risk/test_risk_engine.py tests/portfolio/test_portfolio_engine.py tests/e2e/test_complete_quant_pipeline.py -v
