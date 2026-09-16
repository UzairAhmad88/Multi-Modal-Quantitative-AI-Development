# Deterministic Historical Replay Engine

The `ReplaySessionEngine` (`src/realtime/replay/replay_engine.py`) streams historical daily/intraday data bars sequentially through the real-time feature, signal, risk, and paper execution engine.

---

## 1. Replay Workflow

```text
Historical DataFrame
         │
         ▼
   Replay Session Loop
         │
         ├── Bar 1: Process Features -> Generate Signal -> Pre-Trade Risk -> Execute Paper Order -> Record Snapshot
         ├── Bar 2: Process Features -> Generate Signal -> Pre-Trade Risk -> Execute Paper Order -> Record Snapshot
         └── ...
         │
         ▼
   Final Replay Report (Orders, Fills, P&L, Equity Curve)
```
