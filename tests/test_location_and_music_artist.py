"""
Tests for imported locations from locasion.txt and MusicArtistClassifierService.
"""

from src.repositories.locations import LocationRepository
from src.services.location import LocationService
from src.services.music_artist_classifier import MusicArtistClassifierService

def test_imported_locations():
    repo = LocationRepository()
    locations = repo.get_all_locations()
    assert len(locations) >= 35, f"Expected at least 35 locations, got {len(locations)}"

    # Check known locations from locasion.txt
    names = [loc["name"] for loc in locations]
    assert "AM Studios" in names
    assert "Mehboob Studio" in names
    assert "Sound Ideaz" in names
    assert "20db Sound Studios" in names
    assert "Annapurna Studios" in names
    assert "Tharangini Studio" in names

def test_location_map_builder():
    service = LocationService()
    map_obj = service.build_map()
    assert map_obj is not None
    tile_layers = [c for c in map_obj._children.values() if hasattr(c, "tile_name")]
    assert len(tile_layers) > 0
    assert tile_layers[0].tile_name == "cartodbpositron"
    assert "dark_matter" not in tile_layers[0].tile_name

def test_music_artist_classifier():
    service = MusicArtistClassifierService()
    samples = service.get_sample_artists()
    assert len(samples) >= 5

    # Test prediction on Arijit Singh
    if "Arijit Singh" in samples:
        res = service.predict(samples["Arijit Singh"])
        assert res["status"] == "matched"
        assert res["top_artist"] == "Arijit Singh"
        assert res["top_confidence"] > 80.0
        assert len(res["predictions"]) > 0
        assert len(res["top_songs"]) > 0
