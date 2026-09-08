"""
Domain Entities and Data Contracts for Sangeet.
Defines clean dataclasses representing canonical music intelligence entities.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Artist:
    id: str
    name: str
    bio: Optional[str] = None
    birthplace: Optional[str] = None
    country: str = "India"
    debut_year: Optional[int] = None
    image_url: Optional[str] = None
    mb_id: Optional[str] = None
    song_count: int = 0

@dataclass
class Album:
    id: str
    title: str
    artist_id: Optional[str] = None
    artist_name: Optional[str] = None
    release_year: Optional[int] = None
    total_tracks: int = 1
    cover_url: Optional[str] = None

@dataclass
class SongAudioFeatures:
    song_id: str
    danceability: float = 0.5
    energy: float = 0.5
    key: int = 0
    loudness: float = -10.0
    mode: int = 1
    speechiness: float = 0.05
    acousticness: float = 0.5
    instrumentalness: float = 0.0
    liveness: float = 0.15
    valence: float = 0.5
    tempo: float = 120.0
    time_signature: int = 4

@dataclass
class Song:
    id: str
    title: str
    artist_id: str
    artist_name: str
    album_id: Optional[str] = None
    album_title: Optional[str] = None
    duration_ms: int = 0
    release_year: Optional[int] = None
    popularity: int = 50
    genre: str = "bollywood"
    language: str = "Hindi"
    explicit: bool = False
    is_hit: bool = False
    audio_features: Optional[SongAudioFeatures] = None

@dataclass
class Location:
    id: str
    name: str
    location_type: str  # 'birthplace', 'studio', 'filming_location', 'concert_venue'
    latitude: float
    longitude: float
    city: Optional[str] = None
    country: Optional[str] = "India"
    description: Optional[str] = None

@dataclass
class SongLocationMatch:
    song_id: str
    song_title: str
    artist_name: str
    location: Location
    context_type: str
    scene_notes: Optional[str] = None

@dataclass
class Playlist:
    id: str
    name: str
    description: Optional[str] = None
    cover_emoji: str = "🎵"
    song_count: int = 0
    created_at: Optional[str] = None

@dataclass
class SearchResult:
    status: str
    entity_type: str
    count: int
    records: List[Dict[str, Any]]
    summary_text: str
    confidence: float = 1.0

@dataclass
class RecommendationItem:
    song: Song
    similarity_score: float
    explanation: str
    key_features_matched: List[str] = field(default_factory=list)

@dataclass
class DataQualityReport:
    source_name: str
    total_rows: int
    inserted_rows: int
    duplicate_rows: int
    rejected_rows: int
    missing_values: Dict[str, int]
    status_message: str
