def rank_models(results, metric="sharpe"):
    return sorted(results, key=lambda x: x.get(metric, float("-inf")), reverse=True)
