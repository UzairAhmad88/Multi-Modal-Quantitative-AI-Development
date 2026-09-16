# QUANT AI System Troubleshooting Guide

## Common Operational Scenarios

### 1. Missing Module or Import Errors
- **Problem**: `ModuleNotFoundError: No module named 'src'`
- **Cause**: Python execution context missing root directory.
- **Solution**: Execute commands from root `D:\Quants\DL\multi_modal_quant_ai` or run `python -m pytest`.

### 2. PyTorch GPU / CUDA Warnings
- **Problem**: CUDA requested but unavailable.
- **Cause**: System running on CPU-only laptop environment.
- **Solution**: Automatic fallback is built into `training.device = auto`. No action required.

### 3. PostgreSQL Database Connection Failure
- **Problem**: `ConnectionRefusedError: [Errno 111]`
- **Cause**: PostgreSQL service not running locally.
- **Solution**: Run `docker compose up postgres -d` or use demo mode (`--demo`).

### 4. FastAPI API Port Conflict
- **Problem**: `[Errno 98] Address already in use (8000)`
- **Cause**: Existing process running on port 8000.
- **Solution**: Terminate existing process or launch with `--port 8001`.
