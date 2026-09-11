"""
Album Repository for Sangeet.
Handles album entities and album tracklists.
"""

from typing import List, Dict, Any, Optional
from src.repositories.base import BaseRepository

class AlbumRepository(BaseRepository):
    def get_by_id(self, album_id: str) -> Optional[Dict[str, Any]]:
        query = """
            SELECT alb.*, a.name AS artist_name, COUNT(s.id) AS song_count
            FROM albums alb
            LEFT JOIN artists a ON alb.artist_id = a.id
            LEFT JOIN songs s ON alb.id = s.album_id
            WHERE alb.id = ?
            GROUP BY alb.id
        """
        return self.fetch_one(query, (album_id,))

    def get_by_artist(self, artist_id: str) -> List[Dict[str, Any]]:
        query = "SELECT * FROM albums WHERE artist_id = ? ORDER BY release_year DESC"
        return self.fetch_all(query, (artist_id,))

    def get_by_title_and_artist(self, title: str, artist_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if artist_id:
            query = "SELECT * FROM albums WHERE LOWER(title) = LOWER(?) AND artist_id = ? LIMIT 1"
            return self.fetch_one(query, (title.strip(), artist_id))
        query = "SELECT * FROM albums WHERE LOWER(title) = LOWER(?) LIMIT 1"
        return self.fetch_one(query, (title.strip(),))

    def search_albums(self, query: str = "", limit: int = 15) -> List[Dict[str, Any]]:
        sql = """
            SELECT alb.*, a.name AS artist_name, COUNT(s.id) AS song_count
            FROM albums alb
            LEFT JOIN artists a ON alb.artist_id = a.id
            LEFT JOIN songs s ON alb.id = s.album_id
            WHERE alb.title LIKE ? OR a.name LIKE ?
            GROUP BY alb.id
            ORDER BY alb.title ASC
            LIMIT ?
        """
        q = f"%{query.strip()}%"
        return self.fetch_all(sql, (q, q, limit))

    def get_all_albums(self, limit: int = 50) -> List[Dict[str, Any]]:
        sql = """
            SELECT alb.*, a.name AS artist_name, COUNT(s.id) AS song_count
            FROM albums alb
            LEFT JOIN artists a ON alb.artist_id = a.id
            LEFT JOIN songs s ON alb.id = s.album_id
            GROUP BY alb.id
            ORDER BY alb.title ASC
            LIMIT ?
        """
        return self.fetch_all(sql, (limit,))

    def create_album(self, album_data: Dict[str, Any]) -> bool:
        sql = """
            INSERT INTO albums (id, title, artist_id, release_year, total_tracks, cover_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.execute(sql, (
            album_data["id"],
            album_data["title"],
            album_data.get("artist_id"),
            album_data.get("release_year"),
            album_data.get("total_tracks", 1),
            album_data.get("cover_url")
        ))
        try:
            from src.services.analytics import invalidate_analytics_cache
            invalidate_analytics_cache()
        except Exception:
            pass
        return True

    def update_album(self, album_id: str, album_data: Dict[str, Any]) -> bool:
        sql = """
            UPDATE albums
            SET title = ?, artist_id = ?, release_year = ?, total_tracks = ?
            WHERE id = ?
        """
        self.execute(sql, (
            album_data["title"],
            album_data.get("artist_id"),
            album_data.get("release_year"),
            album_data.get("total_tracks", 1),
            album_id
        ))
        try:
            from src.services.analytics import invalidate_analytics_cache
            invalidate_analytics_cache()
        except Exception:
            pass
        return True

    def delete_album(self, album_id: str) -> bool:
        # Nullify reference in songs first so foreign key constraints are clean
        self.execute("UPDATE songs SET album_id = NULL WHERE album_id = ?", (album_id,))
        self.execute("DELETE FROM albums WHERE id = ?", (album_id,))
        try:
            from src.services.analytics import invalidate_analytics_cache
            invalidate_analytics_cache()
        except Exception:
            pass
        return True
