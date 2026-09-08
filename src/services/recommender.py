"""
Content-Based Recommendation Engine for Sangeet.
Uses cosine similarity over normalized audio features and genre vectors,
with explainable recommendation justifications.
"""

from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from src.config import DB_PATH
from src.repositories.songs import SongRepository

AUDIO_FEATURES = [
    "danceability", "energy", "loudness", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo"
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


def _database_version() -> int:
    version = 0
    for path in (DB_PATH, Path(f"{DB_PATH}-wal")):
        try:
            version = max(version, path.stat().st_mtime_ns)
        except OSError:
            continue
    return version


@lru_cache(maxsize=2)
def _load_feature_catalog(database_version: int):
    del database_version
    records = SongRepository().get_features_matrix(limit=None)
    df = pd.DataFrame(records)
    if df.empty:
        return df, np.empty((0, len(AUDIO_FEATURES)))

    feature_frame = df.reindex(columns=AUDIO_FEATURES).apply(pd.to_numeric, errors="coerce")
    feature_frame = feature_frame.fillna(value=FEATURE_DEFAULTS)
    scaler = MinMaxScaler()
    return df, scaler.fit_transform(feature_frame)


def _feature_value(record: Any, feature: str) -> float:
    value = record.get(feature)
    if value is None or pd.isna(value):
        return FEATURE_DEFAULTS[feature]
    return float(value)

class RecommenderService:
    def __init__(self):
        self.song_repo = SongRepository()

    def get_recommendations(
        self,
        target_song_id: str,
        top_n: int = 6,
        genre_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Computes cosine similarity against catalog songs and provides explainable results."""
        target_song = self.song_repo.get_by_id(target_song_id)
        if not target_song:
            return []
        top_n = max(1, min(50, int(top_n)))

        # Retrieve feature matrix from repository
        df, scaled_audio = _load_feature_catalog(_database_version())
        if df.empty:
            return []

        # Ensure target song is in df
        if target_song_id not in df["id"].values:
            target_df = pd.DataFrame([target_song])
            df = pd.concat([target_df, df], ignore_index=True)
            feature_frame = df.reindex(columns=AUDIO_FEATURES).apply(pd.to_numeric, errors="coerce")
            feature_frame = feature_frame.fillna(value=FEATURE_DEFAULTS)
            scaled_audio = MinMaxScaler().fit_transform(feature_frame)

        # Build feature matrix: audio similarity (0.80) plus genre and artist bonuses.
        target_matches = df[df["id"] == target_song_id]
        if target_matches.empty:
            return []
        target_idx = target_matches.index[0]
        target_vector = scaled_audio[target_idx].reshape(1, -1)

        # Vectorized cosine similarity over audio features across full catalog
        audio_sims = cosine_similarity(target_vector, scaled_audio)[0]

        target_genre = str(target_song.get("genre", "")).lower()
        target_artist = str(target_song.get("artist_name", "")).lower()

        # Vectorized genre & artist matching masks
        genre_col = df["genre"].fillna("").astype(str).str.lower().to_numpy()
        artist_col = df["artist_name"].fillna("").astype(str).str.lower().to_numpy()

        genre_bonus = np.where(genre_col == target_genre, 0.12, 0.0)
        artist_bonus = np.where(artist_col == target_artist, 0.08, 0.0)

        # Composite score
        total_scores = np.clip(audio_sims * 0.80 + genre_bonus + artist_bonus, 0.0, 0.99)
        total_scores[target_idx] = -1.0  # Exclude target song itself

        # Apply genre filter if specified
        if genre_filter and genre_filter != "All":
            valid_mask = (df["genre"] == genre_filter).to_numpy()
            total_scores = np.where(valid_mask, total_scores, -1.0)

        # Fast Top-K selection
        candidate_count = min(top_n * 4, len(df))
        top_indices = np.argsort(total_scores)[::-1][:candidate_count]

        results = []
        for idx in top_indices:
            score = total_scores[idx]
            if score < 0:
                break
            row = df.iloc[idx]

            # Determine human-readable explanation tags
            reasons = []
            if str(row["genre"]).lower() == target_genre:
                reasons.append(f"Same Genre ({target_song.get('genre')})")
            if str(row["artist_name"]).lower() == target_artist:
                reasons.append(f"Same Artist ({target_song.get('artist_name')})")

            # Check acoustic / energy alignment
            t_energy = _feature_value(target_song, "energy")
            r_energy = _feature_value(row, "energy")
            if abs(t_energy - r_energy) < 0.15:
                reasons.append("Matching Energy & Vibe")

            t_dance = _feature_value(target_song, "danceability")
            r_dance = _feature_value(row, "danceability")
            if abs(t_dance - r_dance) < 0.15:
                reasons.append("Similar Danceability")

            t_val = _feature_value(target_song, "valence")
            r_val = _feature_value(row, "valence")
            if abs(t_val - r_val) < 0.15:
                reasons.append("Harmonic Mood Alignment")

            if not reasons:
                reasons.append("Acoustic Feature Alignment")

            results.append({
                "song_id": row["id"],
                "title": row["title"],
                "artist_name": row["artist_name"],
                "genre": row["genre"],
                "popularity": row["popularity"],
                "similarity_score": round(float(score) * 100, 1),
                "explanation": " • ".join(reasons[:3]),
                "danceability": round(_feature_value(row, "danceability"), 2),
                "energy": round(_feature_value(row, "energy"), 2),
                "loudness": round(_feature_value(row, "loudness"), 2),
                "speechiness": round(_feature_value(row, "speechiness"), 4),
                "acousticness": round(_feature_value(row, "acousticness"), 2),
                "instrumentalness": round(_feature_value(row, "instrumentalness"), 4),
                "liveness": round(_feature_value(row, "liveness"), 2),
                "valence": round(_feature_value(row, "valence"), 2),
                "tempo": round(_feature_value(row, "tempo"), 2),
                "key": int(row.get("key") or 0),
            })
            if len(results) >= top_n:
                break

        return results
