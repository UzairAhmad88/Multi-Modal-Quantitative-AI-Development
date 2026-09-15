from __future__ import annotations
from typing import List
import numpy as np
from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger("embeddings")

_embedding_model = None


def encode_texts(texts: List[str], dimension: int = 64) -> np.ndarray:
    """Encode a list of text strings into dense vector representations.

    Uses lightweight TF-IDF TruncatedSVD embedding in demo mode for instant execution,
    and SentenceTransformers when high-precision Transformer embedding is requested.
    """
    if not texts:
        return np.zeros((0, dimension), dtype=np.float32)

    config = get_config()
    data_mode = config.get("data_mode", "demo")

    if data_mode != "demo":
        global _embedding_model
        try:
            if _embedding_model is None:
                from sentence_transformers import SentenceTransformer
                logger.info("Loading sentence-transformers model (all-MiniLM-L6-v2)")
                _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            embeddings = _embedding_model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
            if embeddings.shape[1] != dimension:
                from sklearn.decomposition import TruncatedSVD
                svd = TruncatedSVD(n_components=min(dimension, embeddings.shape[1]), random_state=42)
                embeddings = svd.fit_transform(embeddings)
            return embeddings.astype(np.float32)
        except Exception as e:
            logger.warning(f"SentenceTransformer fallback: {e}")

    # Lightweight TF-IDF + TruncatedSVD embedding (Fast, offline, laptop-friendly)
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD

    vec = TfidfVectorizer(max_features=500, stop_words="english")
    matrix = vec.fit_transform(texts).toarray()

    n_comp = min(dimension, matrix.shape[1], max(1, len(texts) - 1))
    if n_comp < dimension:
        pad = np.zeros((matrix.shape[0], dimension - n_comp), dtype=np.float32)
        if n_comp > 0:
            svd = TruncatedSVD(n_components=n_comp, random_state=42)
            reduced = svd.fit_transform(matrix)
            return np.hstack([reduced, pad]).astype(np.float32)
        else:
            return np.zeros((len(texts), dimension), dtype=np.float32)
    else:
        svd = TruncatedSVD(n_components=dimension, random_state=42)
        return svd.fit_transform(matrix).astype(np.float32)
