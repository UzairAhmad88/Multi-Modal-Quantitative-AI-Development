"""
Experiment Configuration Templates.
"""

from typing import Dict, Any

TEMPLATES: Dict[str, Dict[str, Any]] = {
    "prediction": {
        "dataset_id": "DS-SP500_DAILY",
        "feature_version": "v2.4.1",
        "model_version": "xgboost_alpha",
        "strategy_id": "PREDICTION_ALPHA",
        "portfolio_config": {"method": "mean_variance", "risk_aversion": 2.0},
        "execution_config": {"algorithm": "MARKET", "slippage_bps": 5.0},
        "evaluation_config": {"walk_forward": True, "bootstrap": True}
    },
    "classification": {
        "dataset_id": "DS-SP500_DAILY",
        "feature_version": "v2.4.1",
        "model_version": "rf_regime_classifier",
        "strategy_id": "REGIME_SWITCHING",
        "portfolio_config": {"method": "risk_parity"},
        "execution_config": {"algorithm": "TWAP", "slippage_bps": 3.0},
        "evaluation_config": {"walk_forward": True}
    },
    "multimodal": {
        "dataset_id": "DS-SP500_MULTIMODAL",
        "feature_version": "v2.5.0",
        "model_version": "MultiModalQuantNet",
        "strategy_id": "MULTIMODAL_FUSION_ALPHA",
        "portfolio_config": {"method": "target_volatility", "target_volatility": 0.15},
        "execution_config": {"algorithm": "VWAP", "slippage_bps": 4.0},
        "evaluation_config": {"walk_forward": True, "ablation": True}
    },
    "portfolio": {
        "dataset_id": "DS-SP500_DAILY",
        "feature_version": "v2.4.1",
        "model_version": "ensemble_alpha",
        "strategy_id": "PORTFOLIO_CONSTRUCTION_TEST",
        "portfolio_config": {"method": "min_variance", "long_only": True},
        "execution_config": {"algorithm": "MARKET"},
        "evaluation_config": {"walk_forward": True}
    },
    "execution": {
        "dataset_id": "DS-SP500_DAILY",
        "feature_version": "v2.4.1",
        "model_version": "ensemble_alpha",
        "strategy_id": "EXECUTION_MICROSTRUCTURE_TEST",
        "portfolio_config": {"method": "equal_weight"},
        "execution_config": {"algorithm": "POV", "target_participation_rate": 0.05},
        "evaluation_config": {"walk_forward": False}
    },
    "regime": {
        "dataset_id": "DS-SP500_DAILY",
        "feature_version": "v2.4.1",
        "model_version": "lstm_sequence",
        "strategy_id": "REGIME_STRESS_TEST",
        "portfolio_config": {"method": "inverse_volatility"},
        "execution_config": {"algorithm": "TWAP"},
        "evaluation_config": {"regimes": True}
    },
    "ablation": {
        "dataset_id": "DS-SP500_MULTIMODAL",
        "feature_version": "v2.5.0",
        "model_version": "MultiModalQuantNet",
        "strategy_id": "MODALITY_ABLATION",
        "portfolio_config": {"method": "mean_variance"},
        "execution_config": {"algorithm": "MARKET"},
        "evaluation_config": {"ablation": True}
    }
}


def get_template(template_name: str) -> Dict[str, Any]:
    """Returns requested experiment configuration template."""
    return TEMPLATES.get(template_name.lower(), TEMPLATES["multimodal"]).copy()
