import pandas as pd
from .preprocessing import clean_text
from .sentiment import score_sentiment

def process_news(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["clean_text"] = out["headline"].map(clean_text)
    out["sentiment_score"] = score_sentiment(out["clean_text"].tolist())
    return out
