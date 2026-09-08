"""
Location Repository for Sangeet.
Stores geographical points of interest (birthplaces, studios, filming locations) and song links.
"""

from typing import List, Dict, Any, Optional
from src.repositories.base import BaseRepository

class LocationRepository(BaseRepository):
    def get_all_locations(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM locations ORDER BY name ASC"
        return self.fetch_all(query)

    def get_locations_with_songs(self) -> List[Dict[str, Any]]:
        query = """
            SELECT loc.id AS location_id, loc.name AS location_name, loc.location_type,
                   loc.latitude, loc.longitude, loc.city, loc.country, loc.description,
                   sl.context_type, sl.scene_notes,
                   s.id AS song_id, s.title AS song_title, s.genre, s.release_year,
                   a.id AS artist_id, a.name AS artist_name
            FROM locations loc
            LEFT JOIN song_locations sl ON loc.id = sl.location_id
            LEFT JOIN songs s ON sl.song_id = s.id
            LEFT JOIN artists a ON s.artist_id = a.id
            ORDER BY loc.name ASC
        """
        return self.fetch_all(query)

    def create_location(self, loc: Dict[str, Any]) -> bool:
        sql = """
            INSERT INTO locations (id, name, location_type, latitude, longitude, city, country, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.execute(sql, (
            loc["id"], loc["name"], loc["location_type"],
            loc["latitude"], loc["longitude"],
            loc.get("city"), loc.get("country", "India"), loc.get("description")
        ))
        return True

    def link_song_location(self, song_id: str, location_id: str, context_type: str = "filming_location", notes: str = "") -> bool:
        sql = """
            INSERT OR IGNORE INTO song_locations (song_id, location_id, context_type, scene_notes)
            VALUES (?, ?, ?, ?)
        """
        self.execute(sql, (song_id, location_id, context_type, notes))
        return True
