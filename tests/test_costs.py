from src.backtesting.costs import transaction_cost

def test_transaction_cost():
    assert transaction_cost(10000, 10) == 10
