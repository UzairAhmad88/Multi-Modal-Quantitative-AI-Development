#!/usr/bin/env python3
"""
QUANT AI: Modality Ablation Study CSV Report Generator
"""
from pathlib import Path
import sys
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.market_loader import load_market_data
from src.data.news_loader import load_news_data
from src.data.fundamental_loader import load_fundamentals
from src.backtesting.ablation import AblationStudyEngine
from src.utils.paths import REPORTS_DIR

def main():
    market_df = load_market_data("AAPL")
    news_df = load_news_data()
    fund_df = load_fundamentals()

    ablator = AblationStudyEngine()
    results = ablator.run_ablation(market_df, news_df, fund_df)

    rows = []
    for exp_name, metrics in results.items():
        row = {"experiment": exp_name}
        row.update(metrics)
        rows.append(row)

    df = pd.DataFrame(rows)
    out_dir = Path(REPORTS_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "ablation_results.csv"
    df.to_csv(csv_path, index=False)
    print(f"Generated Ablation Study Results CSV at: {csv_path}")

if __name__ == "__main__":
    main()
