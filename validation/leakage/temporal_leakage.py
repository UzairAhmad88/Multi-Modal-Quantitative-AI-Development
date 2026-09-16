"""
Train/Test Index & Split Bounds Leakage Auditor for Walk-Forward OS.
Verifies zero sample overlap between training, validation, and test fold index sets.
"""

from typing import Dict, Any, List, Set


class TemporalLeakageAuditor:
    """Audits train, validation, and test fold index sets for overlap leakage."""

    @staticmethod
    def audit_index_overlap(
        train_indices: List[int],
        val_indices: List[int],
        test_indices: List[int],
    ) -> Dict[str, Any]:
        set_train = set(train_indices)
        set_val = set(val_indices)
        set_test = set(test_indices)

        overlap_train_val = set_train.intersection(set_val)
        overlap_train_test = set_train.intersection(set_test)
        overlap_val_test = set_val.intersection(set_test)

        issues = []
        if overlap_train_val:
            issues.append(f"INDEX_OVERLAP: Found {len(overlap_train_val)} overlapping samples between train and val sets.")
        if overlap_train_test:
            issues.append(f"INDEX_OVERLAP: Found {len(overlap_train_test)} overlapping samples between train and test sets.")
        if overlap_val_test:
            issues.append(f"INDEX_OVERLAP: Found {len(overlap_val_test)} overlapping samples between val and test sets.")

        has_leakage = len(issues) > 0
        return {
            "status": "FAILED" if has_leakage else "PASSED",
            "has_index_overlap": has_leakage,
            "train_val_overlap_count": len(overlap_train_val),
            "train_test_overlap_count": len(overlap_train_test),
            "val_test_overlap_count": len(overlap_val_test),
            "issues": issues,
        }
