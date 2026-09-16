"""
CLI Tool: Run Statistical Validation.
"""

import argparse
import numpy as np
from validation.core.validation_manager import StatisticalValidationManager


def main():
    parser = argparse.ArgumentParser(description="Run Statistical Validation")
    parser.add_argument("--experiment", type=str, required=True, help="Experiment ID")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    mgr = StatisticalValidationManager()
    # Generate synthetic returns for CLI test execution
    np.random.seed(args.seed)
    returns = np.random.normal(loc=0.0008, scale=0.012, size=500)

    val = mgr.run_validation(experiment_id=args.experiment, returns=returns, random_seed=args.seed)
    print(f"Validation completed for '{args.experiment}': {val.validation_id} (Status: {val.validation_status})")


if __name__ == "__main__":
    main()
