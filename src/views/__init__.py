"""
Views package for Sangeet.

These functions are intentionally imported lazily so the application can start
without importing every optional ML/DL dependency up front.
"""


def render_dashboard():
    from src.views.dashboard import render_dashboard as render
    return render()


def render_analytics():
    from src.views.analytics import render_analytics as render
    return render()


def render_data_manager():
    from src.views.data_manager import render_data_manager as render
    return render()


def render_search():
    from src.views.search import render_search as render
    return render()


def render_ml_lab():
    from src.views.ml_lab import render_ml_lab as render
    return render()


def render_dl_lab():
    from src.views.dl_lab import render_dl_lab as render
    return render()


def render_playlists():
    from src.views.playlists import render_playlists as render
    return render()


def render_assistant():
    from src.views.assistant import render_assistant as render
    return render()


def render_location_map():
    from src.views.location import render_location_map as render
    return render()


def render_vision():
    from src.views.vision import render_vision as render
    return render()


def render_recommendations():
    from src.views.recommendations import render_recommendations as render
    return render()


def render_artist_intelligence():
    from src.views.artist_intelligence import render_artist_intelligence as render
    return render()


def render_recommendation_lab():
    from src.views.recommendation_lab import render_recommendation_lab as render
    return render()


def render_song_prediction_generation():
    from src.views.song_prediction_generation import render_song_prediction_generation as render
    return render()


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

