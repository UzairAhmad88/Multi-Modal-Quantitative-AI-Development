from src.alpha.signal_generator import generate_signal

def test_signal_generation():
    assert generate_signal(0.8) == "BUY"
    assert generate_signal(-0.8) == "SELL"
    assert generate_signal(0.0) == "HOLD"
