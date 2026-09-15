from __future__ import annotations
import time
from pathlib import Path
from typing import Dict, Any, Tuple
import torch
import torch.nn as nn

from torch.utils.data import DataLoader
from src.utils.logger import get_logger

logger = get_logger("dl_trainer")


def get_device() -> torch.device:
    """Return CUDA device if available, otherwise CPU."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def train_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device
) -> float:
    model.train()
    total_loss = 0.0
    total_samples = 0
    for X, y in loader:
        X, y = X.to(device), y.to(device)
        optimizer.zero_grad()
        preds = model(X)
        loss = criterion(preds, y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * len(X)
        total_samples += len(X)

    return total_loss / max(1, total_samples)


def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device
) -> float:
    model.eval()
    total_loss = 0.0
    total_samples = 0
    with torch.no_grad():
        for X, y in loader:
            X, y = X.to(device), y.to(device)
            preds = model(X)
            loss = criterion(preds, y)
            total_loss += loss.item() * len(X)
            total_samples += len(X)

    return total_loss / max(1, total_samples)


def train_dl_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    epochs: int = 20,
    lr: float = 0.001,
    patience: int = 5,
    checkpoint_path: Path | str | None = None
) -> Dict[str, Any]:
    """Complete PyTorch training framework with validation loss tracking and early stopping."""
    device = get_device()
    model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    best_val_loss = float("inf")
    patience_counter = 0
    history = {"train_loss": [], "val_loss": []}
    start_time = time.time()

    for epoch in range(1, epochs + 1):
        train_loss = train_epoch(model, train_loader, optimizer, criterion, device)
        val_loss = evaluate(model, val_loader, criterion, device) if len(val_loader) > 0 else train_loss

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            if checkpoint_path:
                save_checkpoint(model, checkpoint_path)
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logger.info(f"Early stopping triggered at epoch {epoch}")
                break

    elapsed = time.time() - start_time
    param_count = sum(p.numel() for p in model.parameters() if p.requires_grad)

    return {
        "best_val_loss": round(best_val_loss, 6),
        "training_time": round(elapsed, 2),
        "epochs_trained": len(history["train_loss"]),
        "parameter_count": param_count,
        "history": history
    }


def save_checkpoint(model: nn.Module, path: Path | str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), path)


def load_checkpoint(model: nn.Module, path: Path | str) -> nn.Module:
    device = get_device()
    model.load_state_dict(torch.load(path, map_location=device))
    model.to(device)
    return model
