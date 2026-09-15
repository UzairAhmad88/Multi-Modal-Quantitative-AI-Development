from src.portfolio.allocator import equal_weight

def test_equal_weight():
    assert abs(equal_weight(["A","B","C","D"]).sum() - 1.0) < 1e-9
