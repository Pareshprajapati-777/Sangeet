import os
import pickle
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from src.repositories.songs import SongRepository


# Global in-memory cache to ensure zero overhead across Streamlit reruns
_ML_CACHE: Dict[str, Any] = {}
_MODEL_CACHE_FILE = Path(__file__).resolve().parent.parent.parent / "models" / "ml_hit_predictor.pkl"


class MLService:
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
        self.trained_models = {}
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.cached_results = None

        # Auto-restore from memory cache or disk if available
        self._restore_from_cache()

    def _restore_from_cache(self) -> bool:
        global _ML_CACHE
        if _ML_CACHE.get("is_fitted"):
            self.trained_models = _ML_CACHE["trained_models"]
            self.scaler = _ML_CACHE["scaler"]
            self.cached_results = _ML_CACHE.get("results")
            self.is_fitted = True
            return True

        if _MODEL_CACHE_FILE.exists():
            try:
                with open(_MODEL_CACHE_FILE, "rb") as f:
                    data = pickle.load(f)
                self.trained_models = data["trained_models"]
                self.scaler = data["scaler"]
                self.cached_results = data.get("results")
                self.is_fitted = True

                # Populate memory cache
                _ML_CACHE["trained_models"] = self.trained_models
                _ML_CACHE["scaler"] = self.scaler
                _ML_CACHE["results"] = self.cached_results
                _ML_CACHE["is_fitted"] = True
                self._warmup_models()
                return True
            except Exception:
                pass
        return False

    def _warmup_models(self):
        """Pre-warms threadpools so the first user prediction has 0ms latency."""
        try:
            dummy = np.zeros((1, len(self.FEATURE_COLS)), dtype=np.float64)
            for m in self.trained_models.values():
                if hasattr(m, "predict_proba"):
                    m.predict_proba(dummy)
        except Exception:
            pass

    def _persist_cache(self, results: Dict[str, Any]):
        global _ML_CACHE
        _ML_CACHE["trained_models"] = self.trained_models
        _ML_CACHE["scaler"] = self.scaler
        _ML_CACHE["results"] = results
        _ML_CACHE["is_fitted"] = True
        self.cached_results = results

        try:
            _MODEL_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(_MODEL_CACHE_FILE, "wb") as f:
                pickle.dump({
                    "trained_models": self.trained_models,
                    "scaler": self.scaler,
                    "results": results
                }, f)
        except Exception:
            pass

    def prepare_dataset(self) -> Tuple[pd.DataFrame, pd.Series]:
        records = self.song_repo.get_features_matrix(limit=5000)
        if not records:
            raise ValueError("No songs with audio features are available for ML training.")

        df = pd.DataFrame(records)
        if "popularity" not in df.columns:
            raise ValueError("The catalog is missing popularity values required for ML training.")

        feature_frame = df.reindex(columns=self.FEATURE_COLS).apply(pd.to_numeric, errors="coerce")
        feature_frame = feature_frame.fillna(value=self.FEATURE_DEFAULTS)
        target = (pd.to_numeric(df["popularity"], errors="coerce").fillna(50) >= self.HIT_THRESHOLD).astype(int)
        if target.nunique() < 2:
            raise ValueError(
                f"ML training needs both hit and non-hit examples at the {self.HIT_THRESHOLD} popularity threshold."
            )
        return feature_frame, target

    def train_models(self, test_size: float = 0.25, random_state: int = 42, force: bool = False) -> Dict[str, Any]:
        if not force and self.is_fitted and self.cached_results:
            return self.cached_results

        if not 0.1 <= test_size <= 0.5:
            raise ValueError("Test split must be between 0.10 and 0.50.")

        X, y = self.prepare_dataset()
        if len(X) < 10 or y.value_counts().min() < 2:
            raise ValueError("ML training needs at least 10 songs and two examples in each class.")

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=y,
        )

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        self.trained_models.clear()
        self.is_fitted = True

        models = {
            "Logistic Regression": LogisticRegression(max_iter=1000, random_state=random_state),
            "Random Forest": RandomForestClassifier(
                n_estimators=150,
                max_depth=8,
                random_state=random_state,
                n_jobs=-1,
            ),
            "Gradient Boosting": HistGradientBoostingClassifier(
                max_iter=150,
                random_state=random_state,
            ),
        }

        results = {}
        for name, model in models.items():
            model.fit(X_train_scaled, y_train)
            self.trained_models[name] = model
            y_pred = model.predict(X_test_scaled)
            y_prob = model.predict_proba(X_test_scaled)[:, 1]
            results[name] = {
                "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
                "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
                "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
                "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
                "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
                "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            }

        random_forest = self.trained_models["Random Forest"]
        importances = dict(
            zip(
                self.FEATURE_COLS,
                [round(float(value), 4) for value in random_forest.feature_importances_],
            )
        )
        importances = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))
        train_summary = {
            "models": results,
            "feature_importances": importances,
            "train_size": len(X_train),
            "test_size": len(X_test),
            "hit_ratio": round(float(y.mean()), 3),
            "hit_threshold": self.HIT_THRESHOLD,
        }

        self._persist_cache(train_summary)
        return train_summary

    def predict_hit_probability(
        self,
        features: Dict[str, float],
        model_name: str = "Gradient Boosting",
    ) -> Dict[str, Any]:
        if not self.is_fitted or model_name not in self.trained_models:
            # Check cache first before retraining
            if not self._restore_from_cache():
                self.train_models()

        selected_model_name = model_name if model_name in self.trained_models else "Random Forest"
        model = self.trained_models[selected_model_name]
        values = [
            float(features.get(column, self.FEATURE_DEFAULTS[column]) if features.get(column) is not None else self.FEATURE_DEFAULTS[column])
            for column in self.FEATURE_COLS
        ]
        values_frame = pd.DataFrame([values], columns=self.FEATURE_COLS)
        scaled = self.scaler.transform(values_frame)
        probability = float(model.predict_proba(scaled)[0][1])
        is_hit = probability >= 0.5
        return {
            "hit_probability": round(probability * 100, 1),
            "predicted_hit": bool(is_hit),
            "verdict": "🔥 Potential Chartbuster / Hit Track!" if is_hit else "🎧 Niche / Moderate Reach Track",
            "model_used": selected_model_name,
            "hit_threshold": self.HIT_THRESHOLD,
        }

