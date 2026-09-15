from __future__ import annotations
import re
from typing import Dict, List, Tuple
import numpy as np

# Financial lexicon keywords for lightweight, deterministic laptop-friendly sentiment scoring
FINANCIAL_LEXICON = {
    "positive": [
        "beat", "surpassed", "outperformed", "growth", "record", "profit", "bullish", "upgrade",
        "gain", "rallied", "strong", "approval", "expanded", "dividend", "revenue", "partnership"
    ],
    "negative": [
        "missed", "fell", "dropped", "decline", "loss", "bearish", "downgrade", "scrutiny",
        "investigation", "cut", "warning", "lawsuit", "slump", "debt", "risk", "pressure"
    ]
}


def score_text_sentiment(text: str) -> Tuple[float, float, float, float]:
    """Score sentiment for a single text using financial lexicon matching and softmax probability mapping.

    Returns:
        (sentiment_score [-1, +1], prob_pos, prob_neg, prob_neu)
    """
    clean = re.sub(r"[^\w\s]", "", str(text).lower())
    words = clean.split()
    if not words:
        return 0.0, 0.333, 0.333, 0.334

    pos_count = sum(1 for w in words if w in FINANCIAL_LEXICON["positive"])
    neg_count = sum(1 for w in words if w in FINANCIAL_LEXICON["negative"])

    net_score = pos_count - neg_count
    total_matches = pos_count + neg_count

    if total_matches == 0:
        return 0.0, 0.20, 0.20, 0.60

    # Map net score to [-1, 1] using tanh scaling
    sentiment_score = float(np.tanh(net_score / 2.0))

    # Calculate probabilities
    p_pos = float(pos_count / (total_matches + 2))
    p_neg = float(neg_count / (total_matches + 2))
    p_neu = float(1.0 - p_pos - p_neg)

    return sentiment_score, p_pos, p_neg, p_neu


def score_sentiment(texts: List[str]) -> List[float]:
    """Score a list of text strings returning sentiment scores in [-1.0, 1.0]."""
    return [score_text_sentiment(t)[0] for t in texts]


def score_sentiment_full(texts: List[str]) -> Tuple[List[float], List[float], List[float], List[float]]:
    """Return lists of (scores, prob_pos, prob_neg, prob_neu)."""
    scores, pos, neg, neu = [], [], [], []
    for t in texts:
        s, p_pos, p_neg, p_neu = score_text_sentiment(t)
        scores.append(s)
        pos.append(p_pos)
        neg.append(p_neg)
        neu.append(p_neu)
    return scores, pos, neg, neu
