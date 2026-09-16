"""
Lightweight Vector Embedding Provider using TF-IDF & Cosine Similarity.
"""

import math
import re
from typing import List, Dict, Any, Tuple


class EmbeddingProvider:
    """
    Lightweight, self-contained TF-IDF vectorizer and cosine similarity engine.
    Requires no external cloud APIs or heavy packages.
    """

    @staticmethod
    def tokenize(text: str) -> List[str]:
        return re.findall(r"\b\w+\b", text.lower())

    def compute_similarity(self, query: str, documents: List[str]) -> List[float]:
        if not documents:
            return []

        all_docs = [query] + documents
        tokenized_docs = [self.tokenize(d) for d in all_docs]

        # Build vocabulary
        vocab = sorted(list(set(w for doc in tokenized_docs for w in doc)))
        if not vocab:
            return [0.0] * len(documents)

        vocab_idx = {w: i for i, w in enumerate(vocab)}
        N = len(all_docs)

        # Compute Document Frequency (DF)
        df = {}
        for doc in tokenized_docs:
            unique_words = set(doc)
            for w in unique_words:
                df[w] = df.get(w, 0) + 1

        # Compute TF-IDF vectors
        vectors = []
        for doc in tokenized_docs:
            vec = [0.0] * len(vocab)
            tf = {}
            for w in doc:
                tf[w] = tf.get(w, 0) + 1
            for w, count in tf.items():
                if w in vocab_idx:
                    idf = math.log((N + 1) / (df[w] + 1)) + 1
                    vec[vocab_idx[w]] = (count / len(doc)) * idf
            vectors.append(vec)

        query_vec = vectors[0]
        doc_vectors = vectors[1:]

        scores = []
        for d_vec in doc_vectors:
            dot = sum(q * d for q, d in zip(query_vec, d_vec))
            norm_q = math.sqrt(sum(q * q for q in query_vec))
            norm_d = math.sqrt(sum(d * d for d in d_vec))

            if norm_q > 0 and norm_d > 0:
                similarity = dot / (norm_q * norm_d)
            else:
                similarity = 0.0
            scores.append(round(similarity, 4))

        return scores
