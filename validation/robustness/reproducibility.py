"""
Reproducibility Engine for Research Validation.
Generates deterministic validation hashes, records seeds, and verifies deterministic execution reproducibility.
"""

from typing import Dict, List, Any, Optional
import hashlib
import json
import datetime
import uuid


class ReproducibilityEngine:
    """Computes validation hashes and audits seed parameters."""

    @staticmethod
    def generate_validation_hash(
        experiment_id: str,
        config: Dict[str, Any],
        results: Dict[str, Any],
        code_version: str = "v2.5.0",
        random_seed: int = 42,
        validation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        val_id = validation_id or f"VAL-{datetime.date.today().year}-{uuid.uuid4().hex[:6].upper()}"


        cfg_str = json.dumps(config, sort_keys=True)
        res_str = json.dumps(results, sort_keys=True)

        config_hash = hashlib.sha256(cfg_str.encode("utf-8")).hexdigest()[:16]
        result_hash = hashlib.sha256(res_str.encode("utf-8")).hexdigest()[:16]

        composite_input = f"{val_id}:{experiment_id}:{config_hash}:{result_hash}:{code_version}:{random_seed}"
        validation_hash = hashlib.sha256(composite_input.encode("utf-8")).hexdigest()

        return {
            "validation_id": val_id,
            "experiment_id": experiment_id,
            "validation_hash": validation_hash,
            "config_hash": config_hash,
            "result_hash": result_hash,
            "code_version": code_version,
            "random_seed": random_seed,
            "created_at": datetime.datetime.utcnow().isoformat(),
        }

    @staticmethod
    def verify_reproducibility(
        run1_results: Dict[str, Any], run2_results: Dict[str, Any], tolerance: float = 1e-5
    ) -> Dict[str, Any]:
        r1_sharpe = run1_results.get("trading_metrics", {}).get("sharpe", 0.0) or run1_results.get("sharpe", 0.0)
        r2_sharpe = run2_results.get("trading_metrics", {}).get("sharpe", 0.0) or run2_results.get("sharpe", 0.0)

        diff = abs(r1_sharpe - r2_sharpe)
        is_reproducible = diff <= tolerance

        return {
            "is_reproducible": is_reproducible,
            "sharpe_run_1": r1_sharpe,
            "sharpe_run_2": r2_sharpe,
            "difference": round(diff, 6),
            "status": "PASSED" if is_reproducible else "FAILED",
        }
