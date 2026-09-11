"""
Analytics Service for Sangeet.
Calculates catalog aggregates, audio feature distributions, correlations, and trend metrics
with high-speed in-memory caching.
"""

import time
from typing import Dict, Any, List, Optional
import pandas as pd
from src.repositories.songs import SongRepository
from src.repositories.base import BaseRepository

_ANALYTICS_CACHE: Dict[str, Any] = {}
_ANALYTICS_CACHE_TIMESTAMP: float = 0
CACHE_TTL = 30.0  # Fast 30s cache for real-time reactivity

def _get_cached(key: str) -> Optional[Any]:
    global _ANALYTICS_CACHE, _ANALYTICS_CACHE_TIMESTAMP
    if time.time() - _ANALYTICS_CACHE_TIMESTAMP > CACHE_TTL:
        _ANALYTICS_CACHE.clear()
        return None
    return _ANALYTICS_CACHE.get(key)

def _set_cached(key: str, value: Any) -> None:
    global _ANALYTICS_CACHE, _ANALYTICS_CACHE_TIMESTAMP
    _ANALYTICS_CACHE[key] = value
    _ANALYTICS_CACHE_TIMESTAMP = time.time()

def invalidate_analytics_cache():
    global _ANALYTICS_CACHE, _ANALYTICS_CACHE_TIMESTAMP
    _ANALYTICS_CACHE.clear()
    _ANALYTICS_CACHE_TIMESTAMP = 0.0

class AnalyticsService:
    def __init__(self):
        self.song_repo = SongRepository()
        self.base_repo = BaseRepository()

    def get_overview_kpis(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Calculates headline numbers for the Dashboard."""
        if force_refresh:
            invalidate_analytics_cache()
        cached = _get_cached("overview_kpis")
        if cached is not None:
            return cached

        query = """
            SELECT
                (SELECT COUNT(*) FROM songs) as songs_count,
                (SELECT COUNT(*) FROM artists) as artists_count,
                (SELECT COUNT(*) FROM albums) as albums_count,
                (SELECT COUNT(DISTINCT genre) FROM songs) as genres_count,
                (SELECT COUNT(*) FROM locations) as locations_count,
                (SELECT ROUND(AVG(popularity), 1) FROM songs) as avg_pop
        """
        row = self.base_repo.fetch_one(query)
        result = {
            "total_songs": row["songs_count"] if row else 0,
            "total_artists": row["artists_count"] if row else 0,
            "total_albums": row["albums_count"] if row else 0,
            "total_genres": row["genres_count"] if row else 0,
            "total_locations": row["locations_count"] if row else 0,
            "avg_popularity": row["avg_pop"] if (row and row["avg_pop"] is not None) else 0.0
        }
        _set_cached("overview_kpis", result)
        return result

    def get_genre_distribution(self, limit: int = 15) -> List[Dict[str, Any]]:
        cache_key = f"genre_dist_{limit}"
        cached = _get_cached(cache_key)
        if cached is not None:
            return cached

        query = """
            SELECT genre, COUNT(*) AS count, ROUND(AVG(popularity), 1) AS avg_popularity
            FROM songs
            WHERE genre IS NOT NULL AND genre != ''
            GROUP BY genre
            ORDER BY count DESC
            LIMIT ?
        """
        results = self.base_repo.fetch_all(query, (limit,))
        _set_cached(cache_key, results)
        return results

    def get_artist_rankings(self, limit: int = 10) -> List[Dict[str, Any]]:
        cache_key = f"artist_ranks_{limit}"
        cached = _get_cached(cache_key)
        if cached is not None:
            return cached

        query = """
            SELECT a.name, COUNT(s.id) AS song_count, ROUND(AVG(s.popularity), 1) AS avg_popularity
            FROM artists a
            JOIN songs s ON a.id = s.artist_id
            GROUP BY a.id
            ORDER BY song_count DESC, avg_popularity DESC
            LIMIT ?
        """
        results = self.base_repo.fetch_all(query, (limit,))
        _set_cached(cache_key, results)
        return results

    def get_audio_feature_averages(self) -> Dict[str, float]:
        cached = _get_cached("audio_feature_avgs")
        if cached is not None:
            return cached

        query = """
            SELECT
                ROUND(AVG(danceability), 3) AS danceability,
                ROUND(AVG(energy), 3) AS energy,
                ROUND(AVG(speechiness), 3) AS speechiness,
                ROUND(AVG(acousticness), 3) AS acousticness,
                ROUND(AVG(instrumentalness), 3) AS instrumentalness,
                ROUND(AVG(liveness), 3) AS liveness,
                ROUND(AVG(valence), 3) AS valence
            FROM song_audio_features
        """
        row = self.base_repo.fetch_one(query)
        result = dict(row) if row else {}
        _set_cached("audio_feature_avgs", result)
        return result

    def get_correlation_matrix(self) -> pd.DataFrame:
        cached = _get_cached("correlation_matrix")
        if cached is not None:
            return cached

        query = """
            SELECT s.popularity, f.danceability, f.energy, f.loudness,
                   f.speechiness, f.acousticness, f.valence, f.tempo
            FROM songs s
            JOIN song_audio_features f ON s.id = f.song_id
            LIMIT 5000
        """
        rows = self.base_repo.fetch_all(query)
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        corr = df.corr().round(3)
        _set_cached("correlation_matrix", corr)
        return corr

    def get_release_year_trends(self) -> List[Dict[str, Any]]:
        cached = _get_cached("release_year_trends")
        if cached is not None:
            return cached

        query = """
            SELECT release_year, COUNT(*) AS song_count, ROUND(AVG(popularity), 1) AS avg_popularity
            FROM songs
            WHERE release_year IS NOT NULL AND release_year > 1950
            GROUP BY release_year
            ORDER BY release_year ASC
        """
        results = self.base_repo.fetch_all(query)
        _set_cached("release_year_trends", results)
        return results
