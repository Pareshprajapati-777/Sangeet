"""
Views package for Sangeet.
"""

from src.views.dashboard import render_dashboard
from src.views.analytics import render_analytics
from src.views.data_manager import render_data_manager
from src.views.search import render_search
from src.views.ml_lab import render_ml_lab
from src.views.dl_lab import render_dl_lab
from src.views.playlists import render_playlists
from src.views.assistant import render_assistant
from src.views.location import render_location_map
from src.views.vision import render_vision
from src.views.recommendations import render_recommendations
from src.views.artist_intelligence import render_artist_intelligence
from src.views.recommendation_lab import render_recommendation_lab
from src.views.song_prediction_generation import render_song_prediction_generation

__all__ = [
    "render_dashboard",
    "render_analytics",
    "render_data_manager",
    "render_search",
    "render_ml_lab",
    "render_dl_lab",
    "render_playlists",
    "render_assistant",
    "render_location_map",
    "render_vision",
    "render_recommendations",
    "render_artist_intelligence",
    "render_recommendation_lab",
    "render_song_prediction_generation",
]

