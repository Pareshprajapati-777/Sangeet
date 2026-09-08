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
        return True
