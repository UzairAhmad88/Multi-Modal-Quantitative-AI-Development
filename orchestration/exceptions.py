"""
Domain Exceptions for End-to-End Research Orchestration OS.
"""


class OrchestrationError(Exception):
    """Base exception for all orchestration errors."""
    pass


class DataValidationError(OrchestrationError):
    """Raised when data stage validation fails."""
    pass


class FeatureValidationError(OrchestrationError):
    """Raised when feature stage validation fails."""
    pass


class LeakageGateError(OrchestrationError):
    """Raised when data leakage audit fails on strict gate."""
    pass


class ModelTrainingError(OrchestrationError):
    """Raised when model fitting fails."""
    pass


class PredictionStageError(OrchestrationError):
    """Raised when out-of-sample prediction generation fails."""
    pass


class AlphaStageError(OrchestrationError):
    """Raised when alpha signal calculation fails."""
    pass


class PortfolioStageError(OrchestrationError):
    """Raised when portfolio optimization fails."""
    pass


class ExecutionStageError(OrchestrationError):
    """Raised when execution simulation fails."""
    pass


class BacktestStageError(OrchestrationError):
    """Raised when backtest calculation fails."""
    pass


class RiskGateError(OrchestrationError):
    """Raised when risk metrics or limits fail validation."""
    pass


class StatisticalValidationError(OrchestrationError):
    """Raised when statistical significance checks fail."""
    pass


class MonitoringGateError(OrchestrationError):
    """Raised when model monitoring health score fails validation."""
    pass


class CheckpointError(OrchestrationError):
    """Raised when state persistence or checkpoint recovery fails."""
    pass
