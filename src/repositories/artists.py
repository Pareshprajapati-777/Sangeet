"""
Artist Repository for Sangeet.
Handles artist catalog records, biographies, statistics, and face encodings.
"""

from typing import List, Dict, Any, Optional
import json
from src.repositories.base import BaseRepository

class ArtistRepository(BaseRepository):
    def get_all_artists(self, limit: int = 10000) -> List[Dict[str, Any]]:
        query = """
            SELECT a.*, COUNT(s.id) AS song_count
            FROM artists a
            LEFT JOIN songs s ON a.id = s.artist_id
            GROUP BY a.id
            ORDER BY a.name ASC
            LIMIT ?
        """
        return self.fetch_all(query, (limit,))

    def get_by_id(self, artist_id: str) -> Optional[Dict[str, Any]]:
        query = """
            SELECT a.*, COUNT(s.id) AS song_count
            FROM artists a
            LEFT JOIN songs s ON a.id = s.artist_id
            WHERE a.id = ?
            GROUP BY a.id
        """
        return self.fetch_one(query, (artist_id,))

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        query = """
            SELECT a.*, COUNT(s.id) AS song_count
            FROM artists a
            LEFT JOIN songs s ON a.id = s.artist_id
            WHERE LOWER(a.name) = LOWER(?)
            GROUP BY a.id
        """
        return self.fetch_one(query, (name.strip(),))

    def search_artists(self, query: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        sql = """
            SELECT a.*, COUNT(s.id) AS song_count
            FROM artists a
            LEFT JOIN songs s ON a.id = s.artist_id
            WHERE a.name LIKE ?
            GROUP BY a.id
            ORDER BY song_count DESC, a.name ASC
            LIMIT ?
        """
        return self.fetch_all(sql, (f"%{query.strip()}%", limit))

    def get_top_artists(self, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            SELECT a.*, COUNT(s.id) AS song_count, AVG(s.popularity) AS avg_popularity
            FROM artists a
            JOIN songs s ON a.id = s.artist_id
            GROUP BY a.id
            ORDER BY song_count DESC, avg_popularity DESC
            LIMIT ?
        """
        return self.fetch_all(query, (limit,))

    def get_artist_songs(self, artist_id: str, limit: Optional[int] = 50) -> List[Dict[str, Any]]:
        query = """
            SELECT s.*, a.name AS artist_name, alb.title AS album_title,
                   f.danceability, f.energy, f.key, f.loudness, f.mode,
                   f.speechiness, f.acousticness, f.instrumentalness,
                   f.liveness, f.valence, f.tempo, f.time_signature
            FROM songs s
            JOIN artists a ON s.artist_id = a.id
            LEFT JOIN albums alb ON s.album_id = alb.id
            LEFT JOIN song_audio_features f ON s.id = f.song_id
            WHERE s.artist_id = ?
            ORDER BY s.popularity DESC
        """
        if limit is None:
            return self.fetch_all(query, (artist_id,))
        return self.fetch_all(query + " LIMIT ?", (artist_id, limit))

    def get_artist_albums(self, artist_id: str, limit: Optional[int] = 5000) -> List[Dict[str, Any]]:
        query = """
            SELECT alb.*, COUNT(s.id) AS song_count
            FROM albums alb
            LEFT JOIN songs s ON s.album_id = alb.id
            WHERE alb.artist_id = ?
            GROUP BY alb.id
            ORDER BY alb.release_year DESC, alb.title ASC
        """
        if limit is None:
            return self.fetch_all(query, (artist_id,))
        return self.fetch_all(query + " LIMIT ?", (artist_id, limit))

    def create_artist(self, artist_data: Dict[str, Any]) -> bool:
        sql = """
            INSERT INTO artists (id, name, bio, birthplace, country, debut_year, image_url, mb_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.execute(sql, (
            artist_data["id"],
            artist_data["name"],
            artist_data.get("bio"),
            artist_data.get("birthplace"),
            artist_data.get("country", "India"),
            artist_data.get("debut_year"),
            artist_data.get("image_url"),
            artist_data.get("mb_id")
        ))
        try:
            from src.services.analytics import invalidate_analytics_cache
            invalidate_analytics_cache()
        except Exception:
            pass
        return True

    def save_face_encoding(self, artist_id: str, artist_name: str, image_path: str, encoding: List[float]) -> bool:
        sql = """
            INSERT INTO artist_faces (artist_id, artist_name, image_path, encoding_json)
            VALUES (?, ?, ?, ?)
        """
        self.execute(sql, (artist_id, artist_name, image_path, json.dumps(encoding)))
        return True

    def get_all_face_encodings(self) -> List[Dict[str, Any]]:
        sql = "SELECT id, artist_id, artist_name, image_path, encoding_json FROM artist_faces"
        rows = self.fetch_all(sql)
        for r in rows:
            r["encoding"] = json.loads(r["encoding_json"])
        return rows
