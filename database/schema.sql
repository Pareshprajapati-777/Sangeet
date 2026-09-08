-- Sangeet: Music Intelligence Platform Database Schema
-- Canonical SQLite source of truth

PRAGMA foreign_keys = ON;

-- Artists Table
CREATE TABLE IF NOT EXISTS artists (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    bio TEXT,
    birthplace TEXT,
    country TEXT DEFAULT 'India',
    debut_year INTEGER,
    image_url TEXT,
    mb_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Albums Table
CREATE TABLE IF NOT EXISTS albums (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    artist_id TEXT REFERENCES artists(id) ON DELETE SET NULL,
    release_year INTEGER,
    total_tracks INTEGER DEFAULT 1,
    cover_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Songs Table
CREATE TABLE IF NOT EXISTS songs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    artist_id TEXT REFERENCES artists(id) ON DELETE CASCADE,
    album_id TEXT REFERENCES albums(id) ON DELETE SET NULL,
    duration_ms INTEGER DEFAULT 0,
    release_year INTEGER,
    popularity INTEGER DEFAULT 50,
    genre TEXT DEFAULT 'bollywood',
    language TEXT DEFAULT 'Hindi',
    explicit INTEGER DEFAULT 0,
    is_hit INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Song Audio Features Table (1:1 with songs)
CREATE TABLE IF NOT EXISTS song_audio_features (
    song_id TEXT PRIMARY KEY REFERENCES songs(id) ON DELETE CASCADE,
    danceability REAL DEFAULT 0.5,
    energy REAL DEFAULT 0.5,
    key INTEGER DEFAULT 0,
    loudness REAL DEFAULT -10.0,
    mode INTEGER DEFAULT 1,
    speechiness REAL DEFAULT 0.05,
    acousticness REAL DEFAULT 0.5,
    instrumentalness REAL DEFAULT 0.0,
    liveness REAL DEFAULT 0.15,
    valence REAL DEFAULT 0.5,
    tempo REAL DEFAULT 120.0,
    time_signature INTEGER DEFAULT 4
);

-- Public Locations Table (Birthplaces, studios, iconic filming locations)
CREATE TABLE IF NOT EXISTS locations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    location_type TEXT NOT NULL, -- 'birthplace', 'studio', 'filming_location', 'concert_venue'
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    city TEXT,
    country TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Song & Location relationships
CREATE TABLE IF NOT EXISTS song_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id TEXT REFERENCES songs(id) ON DELETE CASCADE,
    location_id TEXT REFERENCES locations(id) ON DELETE CASCADE,
    context_type TEXT DEFAULT 'filming_location', -- 'filming_location', 'studio', 'artist_origin'
    scene_notes TEXT,
    UNIQUE(song_id, location_id, context_type)
);

-- Playlists Table
CREATE TABLE IF NOT EXISTS playlists (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    cover_emoji TEXT DEFAULT '🎵',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Playlist Songs junction
CREATE TABLE IF NOT EXISTS playlist_songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    playlist_id TEXT REFERENCES playlists(id) ON DELETE CASCADE,
    song_id TEXT REFERENCES songs(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(playlist_id, song_id)
);

-- User Favorites (Songs or Artists)
CREATE TABLE IF NOT EXISTS user_favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_type TEXT NOT NULL, -- 'song', 'artist', 'album'
    item_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(item_type, item_id)
);

-- Search History for smart suggestions
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text TEXT NOT NULL,
    result_count INTEGER DEFAULT 0,
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Artist Face Gallery & Encodings for Vision Intelligence
CREATE TABLE IF NOT EXISTS artist_faces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artist_id TEXT REFERENCES artists(id) ON DELETE CASCADE,
    artist_name TEXT NOT NULL,
    image_path TEXT NOT NULL,
    encoding_json TEXT NOT NULL, -- JSON array of 128 floats
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data Quality & Ingestion Runs Report
CREATE TABLE IF NOT EXISTS data_quality_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_name TEXT NOT NULL,
    total_rows INTEGER DEFAULT 0,
    inserted_rows INTEGER DEFAULT 0,
    duplicate_rows INTEGER DEFAULT 0,
    rejected_rows INTEGER DEFAULT 0,
    missing_values_json TEXT,
    status_message TEXT
);

-- Indexes for lightning fast lookups
CREATE INDEX IF NOT EXISTS idx_songs_title ON songs(title);
CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs(artist_id);
CREATE INDEX IF NOT EXISTS idx_songs_genre ON songs(genre);
CREATE INDEX IF NOT EXISTS idx_songs_popularity ON songs(popularity DESC);
CREATE INDEX IF NOT EXISTS idx_songs_genre_pop ON songs(genre, popularity DESC);
CREATE INDEX IF NOT EXISTS idx_songs_year_pop ON songs(release_year, popularity DESC);
CREATE INDEX IF NOT EXISTS idx_songs_lang_pop ON songs(language, popularity DESC);
CREATE INDEX IF NOT EXISTS idx_artists_name ON artists(name);
CREATE INDEX IF NOT EXISTS idx_albums_artist ON albums(artist_id);
CREATE INDEX IF NOT EXISTS idx_locations_type ON locations(location_type);
CREATE INDEX IF NOT EXISTS idx_artist_faces_aid ON artist_faces(artist_id);
CREATE INDEX IF NOT EXISTS idx_artist_faces_name ON artist_faces(artist_name);
CREATE INDEX IF NOT EXISTS idx_song_loc_song ON song_locations(song_id);
CREATE INDEX IF NOT EXISTS idx_song_loc_loc ON song_locations(location_id);
CREATE INDEX IF NOT EXISTS idx_playlist_songs_rel ON playlist_songs(playlist_id, song_id);
CREATE INDEX IF NOT EXISTS idx_user_favorites_type_id ON user_favorites(item_type, item_id);

-- FTS5 Full Text Search index for instantaneous multi-keyword search
CREATE VIRTUAL TABLE IF NOT EXISTS songs_fts USING fts5(
    song_id UNINDEXED,
    title,
    artist_name,
    album_title,
    genre,
    tokenize = 'porter unicode61'
);
