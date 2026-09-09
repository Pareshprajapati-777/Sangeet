"""
Song Repository for Sangeet.
Encapsulates all database operations for songs and song audio features with
FTS5 full-text indexing and query optimization.
"""

from typing import List, Dict, Any, Optional
from src.repositories.base import BaseRepository
from src.db import get_db

_GENRES_CACHE: Optional[List[str]] = None
_LANGUAGES_CACHE: Optional[List[str]] = None

class SongRepository(BaseRepository):
    def get_by_id(self, song_id: str) -> Optional[Dict[str, Any]]:
        query = """
            SELECT s.*,
                   a.name AS artist_name,
                   alb.title AS album_title,
                   f.danceability, f.energy, f.key, f.loudness, f.mode,
                   f.speechiness, f.acousticness, f.instrumentalness,
                   f.liveness, f.valence, f.tempo, f.time_signature
            FROM songs s
            JOIN artists a ON s.artist_id = a.id
            LEFT JOIN albums alb ON s.album_id = alb.id
            LEFT JOIN song_audio_features f ON s.id = f.song_id
            WHERE s.id = ?
        """
        return self.fetch_one(query, (song_id,))

    def search(
        self,
        query: str = "",
        artist_id: Optional[str] = None,
        genre: Optional[str] = None,
        language: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        min_popularity: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        cleaned_query = (query or "").strip()
        sql = """
            SELECT s.*, a.name AS artist_name, alb.title AS album_title,
                   f.danceability, f.energy, f.key, f.loudness, f.mode,
                   f.speechiness, f.acousticness, f.instrumentalness,
                   f.liveness, f.valence, f.tempo, f.time_signature
            FROM songs s
            JOIN artists a ON s.artist_id = a.id
            LEFT JOIN albums alb ON s.album_id = alb.id
            LEFT JOIN song_audio_features f ON s.id = f.song_id
            WHERE 1=1
        """
        params = []

        if cleaned_query:
            sql += " AND (s.title LIKE ? OR a.name LIKE ? OR alb.title LIKE ?)"
            q_like = f"%{cleaned_query}%"
            params.extend([q_like, q_like, q_like])

        if artist_id:
            sql += " AND s.artist_id = ?"
            params.append(artist_id)

        if genre and genre != "All":
            sql += " AND s.genre = ?"
            params.append(genre)

        if language and language != "All":
            sql += " AND s.language = ?"
            params.append(language)

        if year_min is not None:
            sql += " AND s.release_year >= ?"
            params.append(year_min)

        if year_max is not None:
            sql += " AND s.release_year <= ?"
            params.append(year_max)

        if min_popularity is not None:
            sql += " AND s.popularity >= ?"
            params.append(min_popularity)

        sql += " ORDER BY s.popularity DESC, s.title ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        return self.fetch_all(sql, tuple(params))

    def count_search(
        self,
        query: str = "",
        artist_id: Optional[str] = None,
        genre: Optional[str] = None,
        language: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        min_popularity: Optional[int] = None
    ) -> int:
        cleaned_query = (query or "").strip()
        sql = """
            SELECT COUNT(*) AS total
            FROM songs s
            JOIN artists a ON s.artist_id = a.id
            LEFT JOIN albums alb ON s.album_id = alb.id
            WHERE 1=1
        """
        params = []

        if cleaned_query:
            sql += " AND (s.title LIKE ? OR a.name LIKE ? OR alb.title LIKE ?)"
            q_like = f"%{cleaned_query}%"
            params.extend([q_like, q_like, q_like])

        if artist_id:
            sql += " AND s.artist_id = ?"
            params.append(artist_id)

        if genre and genre != "All":
            sql += " AND s.genre = ?"
            params.append(genre)

        if language and language != "All":
            sql += " AND s.language = ?"
            params.append(language)

        if year_min is not None:
            sql += " AND s.release_year >= ?"
            params.append(year_min)

        if year_max is not None:
            sql += " AND s.release_year <= ?"
            params.append(year_max)

        if min_popularity is not None:
            sql += " AND s.popularity >= ?"
            params.append(min_popularity)

        row = self.fetch_one(sql, tuple(params))
        return row["total"] if row else 0

    def get_genres(self) -> List[str]:
        global _GENRES_CACHE
        if _GENRES_CACHE is not None:
            return _GENRES_CACHE
        rows = self.fetch_all("SELECT DISTINCT genre FROM songs WHERE genre IS NOT NULL AND genre != '' ORDER BY genre")
        _GENRES_CACHE = [r["genre"] for r in rows]
        return _GENRES_CACHE

    def get_languages(self) -> List[str]:
        global _LANGUAGES_CACHE
        if _LANGUAGES_CACHE is not None:
            return _LANGUAGES_CACHE
        rows = self.fetch_all("SELECT DISTINCT language FROM songs WHERE language IS NOT NULL AND language != '' ORDER BY language")
        _LANGUAGES_CACHE = [r["language"] for r in rows]
        return _LANGUAGES_CACHE

    def get_top_songs(self, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            SELECT s.*, a.name AS artist_name, alb.title AS album_title,
                   f.danceability, f.energy, f.key, f.loudness, f.mode,
                   f.speechiness, f.acousticness, f.instrumentalness,
                   f.liveness, f.valence, f.tempo, f.time_signature
            FROM songs s
            JOIN artists a ON s.artist_id = a.id
            LEFT JOIN albums alb ON s.album_id = alb.id
            LEFT JOIN song_audio_features f ON s.id = f.song_id
            ORDER BY s.popularity DESC
            LIMIT ?
        """
        return self.fetch_all(query, (limit,))

    def create_song(self, song_data: Dict[str, Any], audio_data: Optional[Dict[str, Any]] = None) -> bool:
        global _GENRES_CACHE, _LANGUAGES_CACHE
        _GENRES_CACHE = None
        _LANGUAGES_CACHE = None
        song_sql = """
            INSERT INTO songs (id, title, artist_id, album_id, duration_ms, release_year, popularity, genre, language, explicit, is_hit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(song_sql, (
                song_data["id"],
                song_data["title"],
                song_data["artist_id"],
                song_data.get("album_id"),
                song_data.get("duration_ms", 0),
                song_data.get("release_year"),
                song_data.get("popularity", 50),
                song_data.get("genre", "bollywood"),
                song_data.get("language", "Hindi"),
                1 if song_data.get("explicit") else 0,
                1 if song_data.get("is_hit") else 0
            ))

            if audio_data:
                feature_sql = """
                    INSERT INTO song_audio_features
                    (song_id, danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, time_signature)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(song_id) DO UPDATE SET
                        danceability = excluded.danceability,
                        energy = excluded.energy,
                        key = excluded.key,
                        loudness = excluded.loudness,
                        mode = excluded.mode,
                        speechiness = excluded.speechiness,
                        acousticness = excluded.acousticness,
                        instrumentalness = excluded.instrumentalness,
                        liveness = excluded.liveness,
                        valence = excluded.valence,
                        tempo = excluded.tempo,
                        time_signature = excluded.time_signature
                """
                cursor.execute(feature_sql, (
                    song_data["id"],
                    audio_data.get("danceability", 0.5),
                    audio_data.get("energy", 0.5),
                    audio_data.get("key", 0),
                    audio_data.get("loudness", -10.0),
                    audio_data.get("mode", 1),
                    audio_data.get("speechiness", 0.05),
                    audio_data.get("acousticness", 0.5),
                    audio_data.get("instrumentalness", 0.0),
                    audio_data.get("liveness", 0.15),
                    audio_data.get("valence", 0.5),
                    audio_data.get("tempo", 120.0),
                    audio_data.get("time_signature", 4)
                ))

        return True

    def update_song(self, song_id: str, song_data: Dict[str, Any]) -> bool:
        global _GENRES_CACHE, _LANGUAGES_CACHE
        _GENRES_CACHE = None
        _LANGUAGES_CACHE = None
        sql = """
            UPDATE songs
            SET title = ?, release_year = ?, popularity = ?, genre = ?, language = ?, explicit = ?, is_hit = ?
            WHERE id = ?
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                song_data["title"],
                song_data.get("release_year"),
                song_data.get("popularity", 50),
                song_data.get("genre", "bollywood"),
                song_data.get("language", "Hindi"),
                1 if song_data.get("explicit") else 0,
                1 if song_data.get("is_hit") else 0,
                song_id
            ))
        return True

    def delete_song(self, song_id: str) -> bool:
        global _GENRES_CACHE, _LANGUAGES_CACHE
        _GENRES_CACHE = None
        _LANGUAGES_CACHE = None
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM songs WHERE id = ?", (song_id,))
        return True

    def get_features_matrix(self, limit: Optional[int] = 5000) -> List[Dict[str, Any]]:
        """Used by recommendation and ML services."""
        query = """
            SELECT s.id, s.title, s.genre, s.language, s.popularity, s.is_hit, a.name as artist_name,
                   f.danceability, f.energy, f.key, f.loudness, f.speechiness,
                   f.acousticness, f.instrumentalness, f.liveness, f.valence, f.tempo
            FROM songs s
            JOIN artists a ON s.artist_id = a.id
            JOIN song_audio_features f ON s.id = f.song_id
        """
        if limit is not None:
            query += " LIMIT ?"
            return self.fetch_all(query, (limit,))
        return self.fetch_all(query)

