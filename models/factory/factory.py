"""
Central Model Factory for Quantitative AI Models.
Instantiates registered ML, DL, NLP, and Ensemble models using unified interfaces.
"""

from typing import Dict, Any, Optional
import uuid
import datetime

from models.factory.base_interface import BaseQuantModel
from src.models.ml.logistic_model import QuantLinearModel
from src.models.ml.random_forest import QuantRandomForestModel
from src.models.ml.xgboost_model import QuantXGBoostModel
from src.models.dl.lstm import LSTMModel
from src.models.dl.gru import GRUModel
from src.models.dl.transformer import TransformerModel
from src.models.dl.multi_modal import MultiModalQuantNet


class ModelWrapper(BaseQuantModel):
    """Generic wrapper adapting existing underlying model implementations to BaseQuantModel."""

    def __init__(self, model_id: str, name: str, version: str, model_obj: Any, config: Dict[str, Any]):
        super().__init__(model_id=model_id, name=name, version=version, config=config)
        self.model_obj = model_obj

    def fit(self, X: Any, y: Any, **kwargs) -> Any:
        if hasattr(self.model_obj, "fit"):
            return self.model_obj.fit(X, y, **kwargs)
        elif hasattr(self.model_obj, "train"):
            return self.model_obj.train(X, y, **kwargs)
        return self

    def predict(self, X: Any) -> Any:
        if hasattr(self.model_obj, "predict"):
            return self.model_obj.predict(X)
        elif callable(self.model_obj):
            return self.model_obj(X)
        return X

    def save(self, filepath: str) -> str:
        if hasattr(self.model_obj, "save"):
            return self.model_obj.save(filepath)
        import pickle
        with open(filepath, "wb") as f:
            pickle.dump(self.model_obj, f)
        return filepath

    def load(self, filepath: str) -> Any:
        if hasattr(self.model_obj, "load"):
            return self.model_obj.load(filepath)
        import pickle
        with open(filepath, "rb") as f:
            self.model_obj = pickle.load(f)
        return self.model_obj


class ModelFactory:
    """Factory creating quantitative models from configuration dicts."""

    SUPPORTED_TYPES = [
        "logistic_regression",
        "random_forest",
        "xgboost",
        "lstm",
        "gru",
        "transformer",
        "multimodal",
        "ensemble"
    ]

    @classmethod
    def create_model(cls, config: Dict[str, Any], model_id: Optional[str] = None) -> BaseQuantModel:
        """Instantiates model based on config."""
        model_meta = config.get("model", {})
        m_type = model_meta.get("type", "logistic_regression").lower()
        m_name = model_meta.get("name", "quant_model")
        m_version = model_meta.get("version", "1.0.0")
        params = model_meta.get("parameters", {})

        actual_id = model_id or f"MODEL-{datetime.date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

        if m_type == "logistic_regression":
            obj = QuantLinearModel(**params)
        elif m_type == "random_forest":
            obj = QuantRandomForestModel(hyperparams=params)
        elif m_type == "xgboost":
            obj = QuantXGBoostModel(hyperparams=params)
        elif m_type == "lstm":
            obj = LSTMModel(
                input_size=params.get("input_size", 16),
                hidden_size=params.get("hidden_size", 64),
                layers=params.get("num_layers", params.get("layers", 2)),
                dropout=params.get("dropout", 0.2)
            )
        elif m_type == "gru":
            obj = GRUModel(
                input_size=params.get("input_size", 16),
                hidden_size=params.get("hidden_size", 64),
                layers=params.get("num_layers", params.get("layers", 2)),
                dropout=params.get("dropout", 0.2)
            )
        elif m_type == "transformer":
            obj = TransformerModel(
                input_size=params.get("input_size", 16),
                d_model=params.get("d_model", 64),
                nhead=params.get("nhead", 4),
                layers=params.get("num_layers", params.get("layers", 2))
            )
        elif m_type == "multimodal":
            obj = MultiModalQuantNet(
                market_input_size=params.get("market_input_size", params.get("market_dim", 16)),
                news_input_dim=params.get("news_input_dim", params.get("news_dim", 10)),
                fund_input_dim=params.get("fund_input_dim", params.get("fundamental_dim", 12)),
                fusion_method=params.get("fusion_method", "learned"),
                embed_dim=params.get("embed_dim", 32)
            )
        elif m_type == "ensemble":
            from models.ensemble.ensemble_model import EnsembleEngine
            obj = EnsembleEngine()
        else:
            obj = QuantLinearModel()

        return ModelWrapper(model_id=actual_id, name=m_name, version=m_version, model_obj=obj, config=config)
