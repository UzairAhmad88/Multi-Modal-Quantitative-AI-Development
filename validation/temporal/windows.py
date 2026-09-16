"""
Validation Window Definition & Bound Diagnostics for Walk-Forward OS.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ValidationWindow:
    """Represents a single temporal fold containing train, validation, and test boundaries."""

    window_id: str
    fold_index: int
    train_start: str
    train_end: str
    validation_start: Optional[str] = None
    validation_end: Optional[str] = None
    test_start: Optional[str] = None
    test_end: Optional[str] = None
    purge_period: int = 0
    embargo_period: int = 0
    train_samples: int = 0
    val_samples: int = 0
    test_samples: int = 0
    purged_samples: int = 0
    embargoed_samples: int = 0
    status: str = "VALID"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def validate_temporal_ordering(self) -> Dict[str, Any]:
        """Validates strict non-overlapping chronological bounds."""
        errors = []
        
        # Check train < validation
        if self.validation_start and self.train_end:
            if str(self.train_end) >= str(self.validation_start):
                errors.append(f"Train end ({self.train_end}) overlaps validation start ({self.validation_start})")

        # Check validation < test
        if self.validation_end and self.test_start:
            if str(self.validation_end) >= str(self.test_start):
                errors.append(f"Validation end ({self.validation_end}) overlaps test start ({self.test_start})")

        # Check train < test (if no validation)
        if not self.validation_start and self.train_end and self.test_start:
            if str(self.train_end) >= str(self.test_start):
                errors.append(f"Train end ({self.train_end}) overlaps test start ({self.test_start})")

        is_valid = len(errors) == 0
        return {
            "is_valid": is_valid,
            "errors": errors,
            "status": "VALID" if is_valid else "INVALID_BOUNDS",
        }
