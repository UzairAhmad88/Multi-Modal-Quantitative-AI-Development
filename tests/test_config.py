from src.utils.config import get_config, Config

def test_config_loading():
    cfg = get_config()
    assert cfg.get("project.name") == "multi_modal_quant_ai"
    assert "AAPL" in cfg.get("data.universe")
    assert cfg.get("portfolio.max_position") == 0.25
    assert cfg.get("risk.max_drawdown") == 0.20

def test_config_dict():
    cfg = Config()
    d = cfg.to_dict()
    assert isinstance(d, dict)
    assert "project" in d
