def transaction_cost(notional: float, basis_points: float) -> float:
    return notional * basis_points / 10000
