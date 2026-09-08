"""
Playlist and User Favorites Repository for Sangeet.
"""

from typing import List, Dict, Any, Optional
import uuid
from src.repositories.base import BaseRepository

class PlaylistRepository(BaseRepository):
    def get_all_playlists(self) -> List[Dict[str, Any]]:
        query = """
            SELECT p.*, COUNT(ps.song_id) AS song_count
            FROM playlists p
            LEFT JOIN playlist_songs ps ON p.id = ps.playlist_id
            GROUP BY p.id
            ORDER BY p.created_at DESC
        """
        return self.fetch_all(query)

    def get_playlist_songs(self, playlist_id: str) -> List[Dict[str, Any]]:
        query = """
            SELECT s.*, a.name AS artist_name, alb.title AS album_title, ps.added_at,
                   f.danceability, f.energy, f.key, f.loudness, f.mode,
                   f.speechiness, f.acousticness, f.instrumentalness,
                   f.liveness, f.valence, f.tempo, f.time_signature
            FROM playlist_songs ps
            JOIN songs s ON ps.song_id = s.id
            JOIN artists a ON s.artist_id = a.id
            LEFT JOIN albums alb ON s.album_id = alb.id
            LEFT JOIN song_audio_features f ON s.id = f.song_id
            WHERE ps.playlist_id = ?
            ORDER BY ps.added_at DESC
        """
        return self.fetch_all(query, (playlist_id,))

    def create_playlist(self, name: str, description: str = "", cover_emoji: str = "🎵") -> str:
        p_id = str(uuid.uuid4())[:8]
        sql = "INSERT INTO playlists (id, name, description, cover_emoji) VALUES (?, ?, ?, ?)"
        self.execute(sql, (p_id, name, description, cover_emoji))
        return p_id

    def add_song_to_playlist(self, playlist_id: str, song_id: str) -> bool:
        sql = "INSERT OR IGNORE INTO playlist_songs (playlist_id, song_id) VALUES (?, ?)"
        self.execute(sql, (playlist_id, song_id))
        return True

    def remove_song_from_playlist(self, playlist_id: str, song_id: str) -> bool:
        sql = "DELETE FROM playlist_songs WHERE playlist_id = ? AND song_id = ?"
        self.execute(sql, (playlist_id, song_id))
        return True

    def delete_playlist(self, playlist_id: str) -> bool:
        self.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
        return True

    def toggle_favorite(self, item_type: str, item_id: str) -> bool:
        exists = self.fetch_one("SELECT id FROM user_favorites WHERE item_type = ? AND item_id = ?", (item_type, item_id))
        if exists:
            self.execute("DELETE FROM user_favorites WHERE id = ?", (exists["id"],))
            return False
        else:
            self.execute("INSERT INTO user_favorites (item_type, item_id) VALUES (?, ?)", (item_type, item_id))
            return True

    def is_favorite(self, item_type: str, item_id: str) -> bool:
        exists = self.fetch_one("SELECT id FROM user_favorites WHERE item_type = ? AND item_id = ?", (item_type, item_id))
        return exists is not None

    def get_favorite_songs(self) -> List[Dict[str, Any]]:
        query = """
            SELECT s.*, a.name AS artist_name, alb.title AS album_title, uf.created_at AS favorited_at,
                   f.danceability, f.energy, f.key, f.loudness, f.mode,
                   f.speechiness, f.acousticness, f.instrumentalness,
                   f.liveness, f.valence, f.tempo, f.time_signature
            FROM user_favorites uf
            JOIN songs s ON uf.item_id = s.id
            JOIN artists a ON s.artist_id = a.id
            LEFT JOIN albums alb ON s.album_id = alb.id
            LEFT JOIN song_audio_features f ON s.id = f.song_id
            WHERE uf.item_type = 'song'
            ORDER BY uf.created_at DESC
        """
        return self.fetch_all(query)
