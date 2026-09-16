"""
CLI Command for Walk-Forward & OOS Research OS.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from validation.services.walk_forward_service import WalkForwardService


def main():
    parser = argparse.ArgumentParser(description="Run Walk-Forward & Out-of-Sample Validation OS.")
    parser.add_argument("--experiment", type=str, default="EXP-001", help="Experiment ID")
    parser.add_argument("--method", type=str, default="EXPANDING", choices=["EXPANDING", "ROLLING", "ANCHORED", "PURGED_CV"], help="Validation method")
    parser.add_argument("--train-period", type=int, default=250, help="Train window size")
    parser.add_argument("--val-period", type=int, default=50, help="Validation window size")
    parser.add_argument("--test-period", type=int, default=50, help="Test window size")
    parser.add_argument("--purge", type=int, default=5, help="Purge window steps")
    parser.add_argument("--embargo", type=int, default=5, help="Embargo window steps")
    parser.add_argument("--lock-test", action="store_true", help="Lock test set after run")

    args = parser.parse_args()
    service = WalkForwardService()

    print(f"🚀 Running Walk-Forward OS ({args.method}) for {args.experiment}...")
    res = service.run_walk_forward(
        experiment_id=args.experiment,
        method=args.method,
        train_window_size=args.train_period,
        val_window_size=args.val_period,
        test_window_size=args.test_period,
        purge_period=args.purge,
        embargo_period=args.embargo,
        lock_test_set=args.lock_test,
    )

    print("\n✅ Walk-Forward Execution Complete:")
    print(f"Validation ID: {res['validation_id']}")
    print(f"Status:        {res['status']}")
    print(f"Config Hash:   {res['config_hash']}")
    print(f"Total Folds:   {len(res['windows'])}")
    print(f"Mean OOS Sharpe: {res['oos_metrics'].get('mean_out_of_sample_sharpe', 0.0)}")
    print(f"Leakage Status:  {res['leakage_audit'].get('status')}")


if __name__ == "__main__":
    main()
