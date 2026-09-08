"""
Search Service for Sangeet.
Provides exact and fuzzy search across songs, artists, albums, genres, and languages,
generating structured SearchResult responses with summaries for voice synthesizers.
"""

from typing import List, Dict, Any, Optional
from src.repositories.songs import SongRepository
from src.repositories.artists import ArtistRepository
from src.domain.entities import SearchResult

class SearchService:
    def __init__(self):
        self.song_repo = SongRepository()
        self.artist_repo = ArtistRepository()

    def search_catalog(
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
    ) -> SearchResult:
        """Searches songs and generates a structured SearchResult."""
        songs = self.song_repo.search(
            query=query,
            artist_id=artist_id,
            genre=genre,
            language=language,
            year_min=year_min,
            year_max=year_max,
            min_popularity=min_popularity,
            limit=limit,
            offset=offset
        )
        total_count = self.song_repo.count_search(
            query=query,
            artist_id=artist_id,
            genre=genre,
            language=language,
            year_min=year_min,
            year_max=year_max,
            min_popularity=min_popularity
        )

        # Build voice-friendly summary text
        top_song = songs[0]["title"] if songs else ""
        top_artist = songs[0]["artist_name"] if songs else ""
        from src.services.voice import VoiceService
        summary = VoiceService.format_search_summary(total_count, query=query, top_track=top_song, artist=top_artist)

        # Record search query history if non-empty
        if query.strip():
            self.song_repo.execute(
                "INSERT INTO search_history (query_text, result_count) VALUES (?, ?)",
                (query.strip(), total_count)
            )

        return SearchResult(
            status="success" if total_count > 0 else "empty",
            entity_type="song",
            count=total_count,
            records=songs,
            summary_text=summary,
            confidence=1.0
        )

    def search_artists(self, query: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        return self.artist_repo.search_artists(query, limit)

    def get_search_filters(self) -> Dict[str, List[str]]:
        genres = ["All"] + self.song_repo.get_genres()
        languages = ["All"] + self.song_repo.get_languages()
        return {
            "genres": genres,
            "languages": languages
        }

    def get_recent_searches(self, limit: int = 8) -> List[str]:
        rows = self.song_repo.fetch_all(
            "SELECT DISTINCT query_text FROM search_history ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return [r["query_text"] for r in rows]
