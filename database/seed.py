"""
Comprehensive Database Seeder for Sangeet: Music Intelligence Platform.
Populates canonical artists, albums, songs, audio features, geographical points of interest,
and artist facial embeddings for local-first execution.
"""

import os
import sys
import uuid
import json
import logging
from pathlib import Path

# Set project root in path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.db import init_db, get_db
from src.services.etl import ETLService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sangeet.seed")

CURATED_ARTISTS = [
    {
        "id": "art_arijit",
        "name": "Arijit Singh",
        "bio": "Renowned Indian playback singer and music composer, often cited as one of the defining voices of modern Bollywood romantic and soulful melodies.",
        "birthplace": "Jiaganj, Murshidabad, West Bengal",
        "country": "India",
        "debut_year": 2011,
        "image_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=400"
    },
    {
        "id": "art_shreya",
        "name": "Shreya Ghoshal",
        "bio": "Four-time National Film Award-winning Indian playback singer known for her wide vocal range and versatility across Indian cinema.",
        "birthplace": "Murshidabad, West Bengal",
        "country": "India",
        "debut_year": 2002,
        "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400"
    },
    {
        "id": "art_ar_rahman",
        "name": "A. R. Rahman",
        "bio": "Two-time Academy Award and Grammy Award-winning composer, record producer and singer who revolutionized modern Indian film music.",
        "birthplace": "Chennai, Tamil Nadu",
        "country": "India",
        "debut_year": 1992,
        "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"
    },
    {
        "id": "art_kishore",
        "name": "Kishore Kumar",
        "bio": "Legendary Indian playback singer, actor, and composer known for his unmatched yodeling, soulful renditions, and vibrant comic timing.",
        "birthplace": "Khandwa, Central Provinces (Madhya Pradesh)",
        "country": "India",
        "debut_year": 1946,
        "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400"
    },
    {
        "id": "art_lata",
        "name": "Lata Mangeshkar",
        "bio": "The Nightingale of India, widely regarded as one of the greatest and most influential playback singers in Indian cultural history.",
        "birthplace": "Indore, Central India Agency",
        "country": "India",
        "debut_year": 1942,
        "image_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400"
    },
    {
        "id": "art_atif",
        "name": "Atif Aslam",
        "bio": "Celebrated Pakistani playback singer and songwriter renowned for his vocal belting technique and chart-topping Bollywood romantic hits.",
        "birthplace": "Wazirabad, Punjab, Pakistan",
        "country": "Pakistan",
        "debut_year": 2004,
        "image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400"
    },
    {
        "id": "art_diljit",
        "name": "Diljit Dosanjh",
        "bio": "International Punjabi superstar, singer, and actor who brought Punjabi music to global stadium tours including Coachella.",
        "birthplace": "Dosanjh Kalan, Jalandhar, Punjab",
        "country": "India",
        "debut_year": 2004,
        "image_url": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=400"
    },
    {
        "id": "art_sonu",
        "name": "Sonu Nigam",
        "bio": "One of India's most technically accomplished and beloved playback singers, dubbed the Lord of Chords.",
        "birthplace": "Faridabad, Haryana",
        "country": "India",
        "debut_year": 1993,
        "image_url": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=400"
    },
    {
        "id": "art_coldplay",
        "name": "Coldplay",
        "bio": "Iconic British rock band formed in London in 1997, celebrated for stadium anthems and melodic pop-rock.",
        "birthplace": "London, United Kingdom",
        "country": "United Kingdom",
        "debut_year": 1997,
        "image_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=400"
    },
    {
        "id": "art_weekend",
        "name": "The Weeknd",
        "bio": "Canadian singer, songwriter and record producer known for his sonic versatility and dark synth-pop lyricism.",
        "birthplace": "Toronto, Ontario, Canada",
        "country": "Canada",
        "debut_year": 2010,
        "image_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=400"
    }
]

CURATED_ALBUMS = [
    {"id": "alb_ashiqui2", "title": "Aashiqui 2", "artist_id": "art_arijit", "release_year": 2013},
    {"id": "alb_rockstar", "title": "Rockstar", "artist_id": "art_ar_rahman", "release_year": 2011},
    {"id": "alb_kabir", "title": "Kabir Singh", "artist_id": "art_arijit", "release_year": 2019},
    {"id": "alb_devdas", "title": "Devdas", "artist_id": "art_shreya", "release_year": 2002},
    {"id": "alb_aradhana", "title": "Aradhana", "artist_id": "art_kishore", "release_year": 1969},
    {"id": "alb_veer_zaara", "title": "Veer-Zaara", "artist_id": "art_lata", "release_year": 2004},
    {"id": "alb_race", "title": "Race", "artist_id": "art_atif", "release_year": 2008},
    {"id": "alb_goat", "title": "G.O.A.T.", "artist_id": "art_diljit", "release_year": 2020},
    {"id": "alb_kalho", "title": "Kal Ho Naa Ho", "artist_id": "art_sonu", "release_year": 2003},
    {"id": "alb_parachutes", "title": "Parachutes", "artist_id": "art_coldplay", "release_year": 2000},
    {"id": "alb_afterhours", "title": "After Hours", "artist_id": "art_weekend", "release_year": 2020}
]

CURATED_SONGS = [
    {
        "id": "sng_tum_hi_ho",
        "title": "Tum Hi Ho",
        "artist_id": "art_arijit",
        "album_id": "alb_ashiqui2",
        "duration_ms": 262000,
        "release_year": 2013,
        "popularity": 92,
        "genre": "bollywood",
        "language": "Hindi",
        "explicit": 0,
        "is_hit": 1,
        "audio": {"danceability": 0.42, "energy": 0.58, "key": 4, "loudness": -7.2, "mode": 0, "speechiness": 0.038, "acousticness": 0.65, "instrumentalness": 0.0, "liveness": 0.12, "valence": 0.38, "tempo": 84.0}
    },
    {
        "id": "sng_kun_faya",
        "title": "Kun Faya Kun",
        "artist_id": "art_ar_rahman",
        "album_id": "alb_rockstar",
        "duration_ms": 473000,
        "release_year": 2011,
        "popularity": 95,
        "genre": "sufi",
        "language": "Hindi",
        "explicit": 0,
        "is_hit": 1,
        "audio": {"danceability": 0.38, "energy": 0.45, "key": 2, "loudness": -8.5, "mode": 1, "speechiness": 0.045, "acousticness": 0.78, "instrumentalness": 0.02, "liveness": 0.35, "valence": 0.42, "tempo": 78.0}
    },
    {
        "id": "sng_channa_mereya",
        "title": "Channa Mereya",
        "artist_id": "art_arijit",
        "album_id": "alb_kabir",
        "duration_ms": 289000,
        "release_year": 2016,
        "popularity": 93,
        "genre": "bollywood",
        "language": "Hindi",
        "explicit": 0,
        "is_hit": 1,
        "audio": {"danceability": 0.44, "energy": 0.62, "key": 7, "loudness": -6.8, "mode": 1, "speechiness": 0.041, "acousticness": 0.52, "instrumentalness": 0.0, "liveness": 0.16, "valence": 0.31, "tempo": 90.0}
    },
    {
        "id": "sng_deewani_mastani",
        "title": "Deewani Mastani",
        "artist_id": "art_shreya",
        "album_id": "alb_devdas",
        "duration_ms": 340000,
        "release_year": 2015,
        "popularity": 89,
        "genre": "classical",
        "language": "Hindi",
        "explicit": 0,
        "is_hit": 1,
        "audio": {"danceability": 0.58, "energy": 0.71, "key": 9, "loudness": -5.9, "mode": 1, "speechiness": 0.062, "acousticness": 0.38, "instrumentalness": 0.01, "liveness": 0.22, "valence": 0.65, "tempo": 118.0}
    },
    {
        "id": "sng_mere_sapno_ki_rani",
        "title": "Mere Sapno Ki Rani",
        "artist_id": "art_kishore",
        "album_id": "alb_aradhana",
        "duration_ms": 300000,
        "release_year": 1969,
        "popularity": 88,
        "genre": "classic_bollywood",
        "language": "Hindi",
        "explicit": 0,
        "is_hit": 1,
        "audio": {"danceability": 0.68, "energy": 0.55, "key": 0, "loudness": -9.1, "mode": 1, "speechiness": 0.051, "acousticness": 0.81, "instrumentalness": 0.005, "liveness": 0.18, "valence": 0.88, "tempo": 126.0}
    },
    {
        "id": "sng_tere_liye",
        "title": "Tere Liye",
        "artist_id": "art_lata",
        "album_id": "alb_veer_zaara",
        "duration_ms": 334000,
        "release_year": 2004,
        "popularity": 90,
        "genre": "bollywood",
        "language": "Hindi",
        "explicit": 0,
        "is_hit": 1,
        "audio": {"danceability": 0.45, "energy": 0.48, "key": 5, "loudness": -8.9, "mode": 1, "speechiness": 0.035, "acousticness": 0.72, "instrumentalness": 0.0, "liveness": 0.14, "valence": 0.36, "tempo": 82.0}
    },
    {
        "id": "sng_pehli_nazar",
        "title": "Pehli Nazar Mein",
        "artist_id": "art_atif",
        "album_id": "alb_race",
        "duration_ms": 314000,
        "release_year": 2008,
        "popularity": 91,
        "genre": "pop",
        "language": "Hindi",
        "explicit": 0,
        "is_hit": 1,
        "audio": {"danceability": 0.62, "energy": 0.68, "key": 6, "loudness": -6.4, "mode": 0, "speechiness": 0.039, "acousticness": 0.41, "instrumentalness": 0.0, "liveness": 0.11, "valence": 0.54, "tempo": 98.0}
    },
    {
        "id": "sng_goat",
        "title": "G.O.A.T.",
        "artist_id": "art_diljit",
        "album_id": "alb_goat",
        "duration_ms": 223000,
        "release_year": 2020,
        "popularity": 94,
        "genre": "bhangra",
        "language": "Punjabi",
        "explicit": 0,
        "is_hit": 1,
        "audio": {"danceability": 0.85, "energy": 0.88, "key": 1, "loudness": -4.2, "mode": 1, "speechiness": 0.12, "acousticness": 0.15, "instrumentalness": 0.0, "liveness": 0.19, "valence": 0.79, "tempo": 104.0}
    },
    {
        "id": "sng_kal_ho_naa_ho",
        "title": "Kal Ho Naa Ho (Heartbeat)",
        "artist_id": "art_sonu",
        "album_id": "alb_kalho",
        "duration_ms": 321000,
        "release_year": 2003,
        "popularity": 94,
        "genre": "bollywood",
        "language": "Hindi",
        "explicit": 0,
        "is_hit": 1,
        "audio": {"danceability": 0.49, "energy": 0.52, "key": 8, "loudness": -7.6, "mode": 1, "speechiness": 0.037, "acousticness": 0.68, "instrumentalness": 0.001, "liveness": 0.15, "valence": 0.41, "tempo": 80.0}
    },
    {
        "id": "sng_yellow",
        "title": "Yellow",
        "artist_id": "art_coldplay",
        "album_id": "alb_parachutes",
        "duration_ms": 269000,
        "release_year": 2000,
        "popularity": 91,
        "genre": "rock",
        "language": "English",
        "explicit": 0,
        "is_hit": 1,
        "audio": {"danceability": 0.43, "energy": 0.70, "key": 11, "loudness": -7.3, "mode": 1, "speechiness": 0.028, "acousticness": 0.003, "instrumentalness": 0.0001, "liveness": 0.23, "valence": 0.28, "tempo": 173.0}
    },
    {
        "id": "sng_blinding_lights",
        "title": "Blinding Lights",
        "artist_id": "art_weekend",
        "album_id": "alb_afterhours",
        "duration_ms": 200000,
        "release_year": 2020,
        "popularity": 96,
        "genre": "synthpop",
        "language": "English",
        "explicit": 0,
        "is_hit": 1,
        "audio": {"danceability": 0.51, "energy": 0.73, "key": 1, "loudness": -5.9, "mode": 1, "speechiness": 0.06, "acousticness": 0.001, "instrumentalness": 0.00009, "liveness": 0.09, "valence": 0.33, "tempo": 171.0}
    }
]

CURATED_LOCATIONS = [
    {
        "id": "loc_film_city",
        "name": "Dadasaheb Phalke Chitranagari (Film City)",
        "location_type": "filming_location",
        "latitude": 19.1623,
        "longitude": 72.8833,
        "city": "Mumbai",
        "country": "India",
        "description": "The epicentre of Bollywood cinema, covering over 520 acres with temples, courts, lakes, and soundstages."
    },
    {
        "id": "loc_mehboob",
        "name": "Mehboob Studios",
        "location_type": "studio",
        "latitude": 19.0528,
        "longitude": 72.8258,
        "city": "Mumbai (Bandra)",
        "country": "India",
        "description": "Historic film and recording studio founded by director Mehboob Khan in 1954, site of legendary soundtrack recordings."
    },
    {
        "id": "loc_nizamuddin",
        "name": "Hazrat Nizamuddin Dargah",
        "location_type": "filming_location",
        "latitude": 28.5916,
        "longitude": 77.2435,
        "city": "New Delhi",
        "country": "India",
        "description": "World-famous Sufi shrine where 'Kun Faya Kun' (Rockstar) was filmed and where Qawwali tradition lives for 700 years."
    },
    {
        "id": "loc_betaab",
        "name": "Betaab Valley",
        "location_type": "filming_location",
        "latitude": 34.0270,
        "longitude": 75.3407,
        "city": "Pahalgam, Kashmir",
        "country": "India",
        "description": "Iconic Himalayan valley featured in countless romantic song sequences across 5 decades of Indian cinema."
    },
    {
        "id": "loc_interlaken",
        "name": "Interlaken & Saanen (Yash Chopra Lake)",
        "location_type": "filming_location",
        "latitude": 46.6863,
        "longitude": 7.8632,
        "city": "Interlaken",
        "country": "Switzerland",
        "description": "The cinematic home of Yash Raj Films romantic songs, where Lake Lauenen is unofficially named 'Lake Chopra'."
    },
    {
        "id": "loc_abbey_road",
        "name": "Abbey Road Studios",
        "location_type": "studio",
        "latitude": 51.5320,
        "longitude": -0.1778,
        "city": "London",
        "country": "United Kingdom",
        "description": "Legendary music recording studio where The Beatles recorded and A.R. Rahman produced international symphonic compositions."
    },
    {
        "id": "loc_marine_drive",
        "name": "Marine Drive (Queen's Necklace)",
        "location_type": "filming_location",
        "latitude": 18.9432,
        "longitude": 72.8230,
        "city": "Mumbai",
        "country": "India",
        "description": "Iconic seafront promenade featured in Mumbai night songs and romantic cinema sequences."
    }
]

SONG_LOCATION_LINKS = [
    ("sng_kun_faya", "loc_nizamuddin", "filming_location", "Shot inside Nizamuddin Dargah during live evening Sufi Qawwali."),
    ("sng_tum_hi_ho", "loc_film_city", "filming_location", "The iconic rain-soaked jacket sequence was filmed at Film City stages."),
    ("sng_channa_mereya", "loc_mehboob", "studio", "Soundtrack recorded and orchestrated at Mehboob Studio soundstage."),
    ("sng_mere_sapno_ki_rani", "loc_mehboob", "studio", "Classic RD Burman / Kishore Kumar studio session."),
    ("sng_tere_liye", "loc_interlaken", "filming_location", "Yash Chopra's cinematic romance scenic Swiss location."),
    ("sng_yellow", "loc_abbey_road", "studio", "String arrangements and mixing sessions in London."),
    ("sng_kal_ho_naa_ho", "loc_marine_drive", "filming_location", "Romantic Mumbai skyline and promenade context.")
]

def seed_database():
    logger.info("Initializing database schema...")
    init_db()

    with get_db() as conn:
        cursor = conn.cursor()

        # Insert Curated Artists
        for art in CURATED_ARTISTS:
            cursor.execute("""
                INSERT INTO artists (id, name, bio, birthplace, country, debut_year, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    bio = excluded.bio,
                    birthplace = excluded.birthplace,
                    country = excluded.country,
                    debut_year = excluded.debut_year,
                    image_url = excluded.image_url
            """, (art["id"], art["name"], art["bio"], art["birthplace"], art["country"], art["debut_year"], art["image_url"]))

        # Insert Curated Albums
        for alb in CURATED_ALBUMS:
            cursor.execute("""
                INSERT INTO albums (id, title, artist_id, release_year)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    artist_id = excluded.artist_id,
                    release_year = excluded.release_year
            """, (alb["id"], alb["title"], alb["artist_id"], alb["release_year"]))

        # Insert Curated Songs & Audio Features
        for s in CURATED_SONGS:
            cursor.execute("""
                INSERT INTO songs (id, title, artist_id, album_id, duration_ms, release_year, popularity, genre, language, explicit, is_hit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    artist_id = excluded.artist_id,
                    album_id = excluded.album_id,
                    duration_ms = excluded.duration_ms,
                    release_year = excluded.release_year,
                    popularity = excluded.popularity,
                    genre = excluded.genre,
                    language = excluded.language,
                    explicit = excluded.explicit,
                    is_hit = excluded.is_hit
            """, (s["id"], s["title"], s["artist_id"], s["album_id"], s["duration_ms"], s["release_year"], s["popularity"], s["genre"], s["language"], s["explicit"], s["is_hit"]))

            af = s["audio"]
            cursor.execute("""
                INSERT INTO song_audio_features
                (song_id, danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, time_signature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(song_id) DO UPDATE SET
                    danceability = excluded.danceability,
                    energy = excluded.energy,
                    key = excluded.key,
                    loudness = excluded.loudness,
                    mode = excluded.mode,
                    speechiness = excluded.speechiness,
                    acousticness = excluded.acousticness,
                    instrumentalness = excluded.instrumentalness,
                    liveness = excluded.liveness,
                    valence = excluded.valence,
                    tempo = excluded.tempo,
                    time_signature = excluded.time_signature
            """, (
                s["id"], af["danceability"], af["energy"], af["key"], af["loudness"],
                af["mode"], af["speechiness"], af["acousticness"], af["instrumentalness"],
                af["liveness"], af["valence"], af["tempo"], 4
            ))

        # Insert Locations
        for loc in CURATED_LOCATIONS:
            cursor.execute("""
                INSERT INTO locations (id, name, location_type, latitude, longitude, city, country, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    location_type = excluded.location_type,
                    latitude = excluded.latitude,
                    longitude = excluded.longitude,
                    city = excluded.city,
                    country = excluded.country,
                    description = excluded.description
            """, (loc["id"], loc["name"], loc["location_type"], loc["latitude"], loc["longitude"], loc["city"], loc["country"], loc["description"]))

        # Insert Song Locations
        for s_id, loc_id, ctype, notes in SONG_LOCATION_LINKS:
            cursor.execute("""
                INSERT OR IGNORE INTO song_locations (song_id, location_id, context_type, scene_notes)
                VALUES (?, ?, ?, ?)
            """, (s_id, loc_id, ctype, notes))

        # Create default playlists
        cursor.execute("INSERT OR IGNORE INTO playlists (id, name, description, cover_emoji) VALUES ('p_bollywood_hits', 'Bollywood Essentials', 'Top chartbusters of Indian Cinema', '✨')")
        cursor.execute("INSERT OR IGNORE INTO playlists (id, name, description, cover_emoji) VALUES ('p_sufi_soul', 'Sufi & Soulful Melodies', 'Devotional and tranquil musical journeys', '🕊️')")
        cursor.execute("INSERT OR IGNORE INTO playlists (id, name, description, cover_emoji) VALUES ('p_workout_bhangra', 'High-Octane Beats', 'Pumping beats and Punjabi rhythms for energy', '🔥')")

        for s_id in ["sng_tum_hi_ho", "sng_channa_mereya", "sng_pehli_nazar", "sng_kal_ho_naa_ho"]:
            cursor.execute("INSERT OR IGNORE INTO playlist_songs (playlist_id, song_id) VALUES ('p_bollywood_hits', ?)", (s_id,))
        
        cursor.execute("INSERT OR IGNORE INTO playlist_songs (playlist_id, song_id) VALUES ('p_sufi_soul', 'sng_kun_faya')")
        cursor.execute("INSERT OR IGNORE INTO playlist_songs (playlist_id, song_id) VALUES ('p_sufi_soul', 'sng_tere_liye')")
        cursor.execute("INSERT OR IGNORE INTO playlist_songs (playlist_id, song_id) VALUES ('p_workout_bhangra', 'sng_goat')")

    logger.info("Curated catalog successfully seeded.")

    # Try downloading and enriching from Kaggle dataset if possible
    try:
        etl = ETLService()
        logger.info("Checking Kaggle dataset download for large-scale catalog...")
        csv_file = etl.download_kaggle_dataset()
        logger.info(f"Ingesting 3,000 tracks from Kaggle: {csv_file}")
        report = etl.process_and_ingest(csv_file, source_name="Kaggle Spotify 114K", max_rows=3000)
        logger.info(f"Kaggle ingestion report: {report.status_message}")
    except Exception as e:
        logger.warning(f"Kaggle download skipped or encountered notice: {e}. Curated catalog remains active.")

    # Setup Gallery Face Encodings
    setup_gallery_faces()

def setup_gallery_faces():
    """Registers real face encodings for gallery images that are present."""
    from src.repositories.artists import ArtistRepository
    from src.services.vision import VisionService

    artist_repo = ArtistRepository()
    artists_to_embed = [
        ("art_arijit", "Arijit Singh", "assets/artist_gallery/arijit_singh.jpg"),
        ("art_shreya", "Shreya Ghoshal", "assets/artist_gallery/shreya_ghoshal.jpg"),
        ("art_ar_rahman", "A. R. Rahman", "assets/artist_gallery/ar_rahman.jpg"),
        ("art_kishore", "Kishore Kumar", "assets/artist_gallery/kishore_kumar.jpg"),
        ("art_diljit", "Diljit Dosanjh", "assets/artist_gallery/diljit_dosanjh.jpg")
    ]

    existing_artist_ids = {item["artist_id"] for item in artist_repo.get_all_face_encodings()}
    vision_service = VisionService()
    registered = 0
    for art_id, name, relative_path in artists_to_embed:
        image_path = ROOT_DIR / relative_path
        if not image_path.exists() or art_id in existing_artist_ids:
            continue
        try:
            vision_service.add_gallery_reference(art_id, name, image_path.read_bytes(), image_path.name)
            existing_artist_ids.add(art_id)
            registered += 1
        except Exception as exc:
            logger.warning("Skipping gallery image %s: %s", image_path, exc)

    if registered:
        logger.info("Registered %s real artist face encodings.", registered)
    elif not existing_artist_ids:
        logger.warning("No real artist gallery images found; add references from Image Intelligence.")

if __name__ == "__main__":
    seed_database()
    print("Sangeet database seeded successfully!")
