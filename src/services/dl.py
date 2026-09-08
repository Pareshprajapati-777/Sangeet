"""PyTorch service for reproducible song hit classification."""

from copy import deepcopy
from typing import Any, Dict

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset

from src.repositories.songs import SongRepository


class SongClassifierNN(nn.Module):
    """Feed-forward classifier with normalization and dropout."""

    def __init__(self, input_dim: int = 9, hidden_dim: int = 64, dropout_rate: float = 0.25):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.BatchNorm1d(hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim // 2, 1),
        )

    def forward(self, features):
        return self.net(features)


class DLService:
    FEATURE_COLS = [
        "danceability",
        "energy",
        "loudness",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
    ]
    FEATURE_DEFAULTS = {
        "danceability": 0.5,
        "energy": 0.5,
        "loudness": -10.0,
        "speechiness": 0.05,
        "acousticness": 0.5,
        "instrumentalness": 0.0,
        "liveness": 0.15,
        "valence": 0.5,
        "tempo": 120.0,
    }
    HIT_THRESHOLD = 70

    def __init__(self):
        self.song_repo = SongRepository()
        self.scaler = StandardScaler()
        self.model = None

    def _prepare_dataset(self):
        records = self.song_repo.get_features_matrix(limit=5000)
        if not records:
            raise ValueError("No songs with audio features are available for DL training.")

        df = pd.DataFrame(records)
        if "popularity" not in df.columns:
            raise ValueError("The catalog is missing popularity values required for DL training.")
        features = df.reindex(columns=self.FEATURE_COLS).apply(pd.to_numeric, errors="coerce")
        features = features.fillna(value=self.FEATURE_DEFAULTS)
        target = (pd.to_numeric(df["popularity"], errors="coerce").fillna(50) >= self.HIT_THRESHOLD).astype(float)
        if target.nunique() < 2:
            raise ValueError(
                f"DL training needs both hit and non-hit examples at the {self.HIT_THRESHOLD} popularity threshold."
            )
        return features.values, target.values

    def train_neural_network(
        self,
        epochs: int = 35,
        batch_size: int = 64,
        learning_rate: float = 0.005,
        hidden_dim: int = 64,
        dropout_rate: float = 0.25,
    ) -> Dict[str, Any]:
        if epochs < 1 or batch_size < 2 or learning_rate <= 0:
            raise ValueError("Epochs and batch size must be positive; learning rate must be greater than zero.")
        if hidden_dim < 4 or not 0 <= dropout_rate < 1:
            raise ValueError("Hidden units must be at least 4 and dropout must be between 0 and 1.")

        features, target = self._prepare_dataset()
        if len(target) < 10 or np.unique(target).size < 2:
            raise ValueError("DL training needs at least 10 songs and two target classes.")

        torch.manual_seed(42)
        np.random.seed(42)
        x_train, x_val, y_train, y_val = train_test_split(
            features,
            target,
            test_size=0.25,
            random_state=42,
            stratify=target,
        )
        x_train = self.scaler.fit_transform(x_train)
        x_val = self.scaler.transform(x_val)

        train_dataset = TensorDataset(
            torch.as_tensor(x_train, dtype=torch.float32),
            torch.as_tensor(y_train, dtype=torch.float32).unsqueeze(1),
        )
        val_features = torch.as_tensor(x_val, dtype=torch.float32)
        val_target = torch.as_tensor(y_val, dtype=torch.float32).unsqueeze(1)
        drop_last = len(train_dataset) > batch_size and len(train_dataset) % batch_size == 1
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            drop_last=drop_last,
        )

        self.model = SongClassifierNN(
            input_dim=len(self.FEATURE_COLS),
            hidden_dim=hidden_dim,
            dropout_rate=dropout_rate,
        )
        criterion = nn.BCEWithLogitsLoss()
        optimizer = optim.AdamW(self.model.parameters(), lr=learning_rate, weight_decay=1e-4)
        history = {"epoch": [], "train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
        best_state = None
        best_val_loss = float("inf")
        stale_epochs = 0
        patience = min(8, max(3, epochs // 4))

        for epoch in range(1, epochs + 1):
            self.model.train()
            total_loss = 0.0
            correct = 0
            total = 0
            for batch_features, batch_target in train_loader:
                optimizer.zero_grad()
                logits = self.model(batch_features)
                loss = criterion(logits, batch_target)
                loss.backward()
                optimizer.step()
                probabilities = torch.sigmoid(logits)
                total_loss += loss.item() * len(batch_target)
                correct += ((probabilities >= 0.5) == (batch_target >= 0.5)).sum().item()
                total += len(batch_target)

            self.model.eval()
            with torch.no_grad():
                val_logits = self.model(val_features)
                val_loss = criterion(val_logits, val_target).item()
                val_probabilities = torch.sigmoid(val_logits)
                val_accuracy = ((val_probabilities >= 0.5) == (val_target >= 0.5)).float().mean().item()

            train_loss = total_loss / max(total, 1)
            train_accuracy = correct / max(total, 1)
            history["epoch"].append(epoch)
            history["train_loss"].append(round(train_loss, 4))
            history["val_loss"].append(round(val_loss, 4))
            history["train_acc"].append(round(train_accuracy * 100, 2))
            history["val_acc"].append(round(val_accuracy * 100, 2))

            if val_loss < best_val_loss - 1e-5:
                best_val_loss = val_loss
                best_state = deepcopy(self.model.state_dict())
                stale_epochs = 0
            else:
                stale_epochs += 1
                if epochs >= 10 and stale_epochs >= patience:
                    break

        if best_state is not None:
            self.model.load_state_dict(best_state)
        self.model.eval()
        with torch.no_grad():
            final_logits = self.model(val_features)
            final_loss = criterion(final_logits, val_target).item()
            final_probabilities = torch.sigmoid(final_logits)
            final_accuracy = ((final_probabilities >= 0.5) == (val_target >= 0.5)).float().mean().item()

        return {
            "history": history,
            "final_val_acc": round(final_accuracy * 100, 2),
            "final_val_loss": round(final_loss, 4),
            "epochs_run": len(history["epoch"]),
            "total_params": sum(parameter.numel() for parameter in self.model.parameters() if parameter.requires_grad),
            "hit_threshold": self.HIT_THRESHOLD,
        }

    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        if self.model is None:
            self.train_neural_network(epochs=15)

        values = {
            column: features.get(column, default)
            for column, default in self.FEATURE_DEFAULTS.items()
        }
        values_frame = pd.DataFrame([values], columns=self.FEATURE_COLS).apply(
            pd.to_numeric,
            errors="coerce",
        ).fillna(value=self.FEATURE_DEFAULTS)
        scaled = self.scaler.transform(values_frame)
        self.model.eval()
        with torch.no_grad():
            probability = torch.sigmoid(self.model(torch.as_tensor(scaled, dtype=torch.float32))).item()
        return {
            "dl_hit_probability": round(float(probability) * 100, 1),
            "predicted_hit": probability >= 0.5,
            "network_architecture": "3-Layer MLP (BatchNorm + Dropout)",
            "hit_threshold": self.HIT_THRESHOLD,
        }
