"""
Automated Test Suite for Sangeet: Music Intelligence Platform.
Validates database schema, repositories, recommendation vectors,
ML pipelines, PyTorch DL networks, and search services.
"""

import sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import pytest
from src.db import get_connection
from src.repositories.songs import SongRepository
from src.repositories.artists import ArtistRepository
from src.repositories.locations import LocationRepository
from src.repositories.playlists import PlaylistRepository
from src.services.search import SearchService
from src.services.recommender import RecommenderService
from src.services.analytics import AnalyticsService
from src.services.ml import MLService
from src.services.dl import DLService

def test_database_connection_and_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r["name"] for r in cursor.fetchall()]
    conn.close()
    
    assert "songs" in tables
    assert "artists" in tables
    assert "albums" in tables
    assert "locations" in tables
    assert "song_audio_features" in tables
    assert "playlists" in tables
    assert "artist_faces" in tables

def test_song_repository():
    repo = SongRepository()
    songs = repo.get_top_songs(limit=5)
    assert len(songs) > 0
    assert "title" in songs[0]
    assert "artist_name" in songs[0]

    # Test search
    res = repo.search(query="Tum Hi Ho", limit=5)
    assert len(res) > 0
    assert "Tum Hi Ho" in res[0]["title"]

def test_artist_repository():
    repo = ArtistRepository()
    arijit = repo.get_by_name("Arijit Singh")
    assert arijit is not None
    assert "Arijit Singh" in arijit["name"]
    
    # Test face encodings
    encs = repo.get_all_face_encodings()
    assert len(encs) > 0
    assert len(encs[0]["encoding"]) == 128

def test_location_repository():
    repo = LocationRepository()
    locs = repo.get_all_locations()
    assert len(locs) > 0
    names = [l["name"] for l in locs]
    assert any("Film City" in n for n in names)

def test_search_service():
    service = SearchService()
    res = service.search_catalog(query="Kun Faya", limit=5)
    assert res.status == "success"
    assert res.count >= 1
    assert "Kun Faya" in res.summary_text

def test_recommender_service():
    recommender = RecommenderService()
    song_repo = SongRepository()
    top = song_repo.get_top_songs(limit=1)[0]
    
    recos = recommender.get_recommendations(target_song_id=top["id"], top_n=3)
    assert len(recos) > 0
    assert "similarity_score" in recos[0]
    assert recos[0]["similarity_score"] <= 100.0
    assert "explanation" in recos[0]

def test_analytics_service():
    service = AnalyticsService()
    kpis = service.get_overview_kpis()
    assert kpis["total_songs"] > 0
    assert kpis["total_artists"] > 0
    
    genres = service.get_genre_distribution(limit=5)
    assert len(genres) > 0

def test_ml_service():
    ml = MLService()
    results = ml.train_models(test_size=0.2)
    assert "models" in results
    assert "Random Forest" in results["models"]
    assert "Gradient Boosting" in results["models"]
    assert "accuracy" in results["models"]["Random Forest"]
    
    # Test live prediction
    pred = ml.predict_hit_probability({
        "danceability": 0.8,
        "energy": 0.85,
        "loudness": -5.0,
        "valence": 0.7,
        "tempo": 120.0
    })
    assert "hit_probability" in pred
    assert 0.0 <= pred["hit_probability"] <= 100.0

def test_dl_service():
    dl = DLService()
    results = dl.train_neural_network(epochs=5, hidden_dim=32)
    assert "history" in results
    assert len(results["history"]["epoch"]) == 5
    assert results["final_val_acc"] >= 0.0

    pred = dl.predict({"danceability": 0.7, "energy": 0.7, "tempo": 110.0})
    assert "dl_hit_probability" in pred

def test_artist_classifier_service():
    from src.services.artist_classifier import ArtistClassifierService
    classifier = ArtistClassifierService()
    result = classifier.predict_artist("Cause the players gonna play, and haters gonna hate", top_k=3)
    assert "top_artist" in result
    assert "top_confidence" in result
    assert len(result["predictions"]) == 3
    assert result["top_confidence"] > 0.0

def test_music_generation_service():
    from src.services.music_generation import MusicGenerationService
    gen_service = MusicGenerationService()
    res = gen_service.synthesize_harmonic_music("80s retro synthwave", duration=4, bpm=120)
    assert "audio_bytes" in res
    assert len(res["audio_bytes"]) > 10000
    assert res["bpm"] == 120
    assert len(res["waveform"]) > 0

def test_image_artist_classifier_service():
    from src.services.image_artist_classifier import ImageArtistClassifierService
    from PIL import Image
    import numpy as np

    service = ImageArtistClassifierService()
    img = Image.fromarray(np.uint8(np.random.rand(128, 128, 3) * 255))
    res = service.predict(img, top_k=3)
    assert "top_artist" in res
    assert "top_confidence" in res
    assert len(res["predictions"]) == 3
    assert res["gradcam_image"] is not None


