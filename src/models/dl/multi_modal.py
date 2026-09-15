from __future__ import annotations
import torch
import torch.nn as nn
from typing import Dict, Any


class MarketEncoder(nn.Module):
    """Encodes temporal market numerical sequence into a dense vector embedding."""

    def __init__(self, input_size: int, hidden_size: int = 64, embed_dim: int = 32):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers=1, batch_first=True)
        self.proj = nn.Linear(hidden_size, embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        return torch.relu(self.proj(out[:, -1, :]))


class NewsEncoder(nn.Module):
    """Encodes news sentiment and NLP vector into a dense vector embedding."""

    def __init__(self, input_dim: int = 10, embed_dim: int = 16):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, embed_dim),
            nn.ReLU()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.mlp(x)


class FundamentalEncoder(nn.Module):
    """Encodes financial ratios and growth metrics into a dense vector embedding."""

    def __init__(self, input_dim: int = 12, embed_dim: int = 16):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, embed_dim),
            nn.ReLU()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.mlp(x)


class LearnedFusionLayer(nn.Module):
    """Fuses modality representations using learned attention weights across embeddings."""

    def __init__(self, embed_dim: int):
        super().__init__()
        self.attn_weights = nn.Parameter(torch.ones(3, 1))

    def forward(self, market_emb: torch.Tensor, news_emb: torch.Tensor, fund_emb: torch.Tensor) -> torch.Tensor:
        weights = torch.softmax(self.attn_weights, dim=0)
        fused = weights[0] * market_emb + weights[1] * news_emb + weights[2] * fund_emb
        return fused


class MultiModalQuantNet(nn.Module):
    """CapStone Multi-Modal Neural Network Architecture fusing Market, News, and Fundamental representations."""

    def __init__(
        self,
        market_input_size: int,
        news_input_dim: int = 10,
        fund_input_dim: int = 12,
        fusion_method: str = "learned",
        embed_dim: int = 32
    ):
        super().__init__()
        self.fusion_method = fusion_method.lower()

        self.market_encoder = MarketEncoder(market_input_size, hidden_size=64, embed_dim=embed_dim)
        self.news_encoder = NewsEncoder(news_input_dim, embed_dim=embed_dim)
        self.fund_encoder = FundamentalEncoder(fund_input_dim, embed_dim=embed_dim)

        if self.fusion_method == "learned":
            self.fusion_layer = LearnedFusionLayer(embed_dim)
            fusion_out_dim = embed_dim
        else:  # Early / Concat fusion
            fusion_out_dim = embed_dim * 3

        self.prediction_head = nn.Sequential(
            nn.Linear(fusion_out_dim, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, 1)
        )

    def forward(self, market_seq: torch.Tensor, news_vec: torch.Tensor, fund_vec: torch.Tensor) -> torch.Tensor:
        m_emb = self.market_encoder(market_seq)
        n_emb = self.news_encoder(news_vec)
        f_emb = self.fund_encoder(fund_vec)

        if self.fusion_method == "learned":
            fused = self.fusion_layer(m_emb, n_emb, f_emb)
        else:
            fused = torch.cat([m_emb, n_emb, f_emb], dim=-1)

        return self.prediction_head(fused).squeeze(-1)
