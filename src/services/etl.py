"""
ETL Service for Sangeet.
Automates dataset acquisition (Kaggle API / CSV upload / chunked batch loops), validation,
cleaning, normalization, entity mapping, and data quality reporting.
"""

import os
import re
import json
import uuid
import logging
from typing import Dict, Any, Tuple, Optional, Callable
import pandas as pd
from pathlib import Path
from src.config import RAW_DATA_DIR, KAGGLE_USERNAME, KAGGLE_KEY
from src.db import get_db
from src.domain.entities import DataQualityReport
from src.services.analytics import invalidate_analytics_cache

logger = logging.getLogger("sangeet.etl")


def _text_value(value: Any, default: str = "", limit: Optional[int] = None) -> str:
    if value is None or pd.isna(value):
        return default
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return default
    return text[:limit] if limit else text


def _number_value(value: Any, default: float, integer: bool = False) -> Any:
    try:
        number = pd.to_numeric(value, errors="coerce")
        if pd.isna(number):
            number = default
        return int(number) if integer else float(number)
    except (TypeError, ValueError):
        return int(default) if integer else float(default)


def _stable_song_id(artist: str, album: str, title: str) -> str:
    identity = "|".join(value.casefold() for value in (artist, album, title))
    return f"sng_{uuid.uuid5(uuid.NAMESPACE_URL, identity).hex[:12]}"


def _release_year_value(row: Any) -> Optional[int]:
    for column in ("release_year", "year", "album_release_year", "release_date"):
        if column not in row.index:
            continue
        match = re.search(r"(?:19|20)\d{2}", _text_value(row[column]))
        if match:
            return int(match.group(0))
    return None

class ETLService:
    def download_kaggle_dataset(self, dataset_name: str = "saichaitanyareddyai/spotify-tracks-dataset-audio-features") -> str:
        """Downloads and extracts the dataset from Kaggle into data/raw/."""
        if not KAGGLE_USERNAME or not KAGGLE_KEY:
            raise ValueError("Kaggle credentials (KAGGLE_USERNAME and KAGGLE_KEY) are not configured in .env.")
        
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        
        dest = RAW_DATA_DIR / "kaggle_spotify"
        dest.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Downloading Kaggle dataset '{dataset_name}' to {dest}...")
        api.dataset_download_files(dataset_name, path=str(dest), unzip=True)
        
        csv_files = list(dest.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError("No CSV file found in downloaded Kaggle archive.")
        
        return str(csv_files[0])

    def get_default_dataset_path(self) -> Optional[Path]:
        """Returns the path to the canonical local dataset CSV if present."""
        dest = RAW_DATA_DIR / "kaggle_spotify"
        csv_files = list(dest.glob("*.csv"))
        if csv_files:
            return csv_files[0]
        return None

    def ingest_full_dataset_in_chunks(
        self,
        file_path_or_buffer = None,
        source_name: str = "Full Spotify 114K Loop",
        chunk_size: int = 10000,
        progress_callback: Optional[Callable[[int, int, int], None]] = None
    ) -> DataQualityReport:
        """
        Loops through the entire dataset in memory-efficient chunk batches,
        performing high-speed SQLite transactions with bulk executemany inserts.
        """
        if file_path_or_buffer is None:
            default_path = self.get_default_dataset_path()
            if not default_path or not default_path.exists():
                raise FileNotFoundError("No dataset found in data/raw/kaggle_spotify. Please download via Kaggle or upload a CSV.")
            file_path = str(default_path)
        else:
            file_path = file_path_or_buffer

        logger.info(f"Starting chunked batch loop ingestion from: {file_path}")

        # Estimate total rows
        total_estimated = 114000
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                total_estimated = max(1, sum(1 for _ in f) - 1)
        except Exception:
            pass

        total_processed = 0
        total_inserted = 0
        total_duplicates = 0
        total_rejected = 0
        chunk_index = 0

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA synchronous = NORMAL")
            cursor.execute("PRAGMA journal_mode = WAL")

            # Pre-cache existing artist names
            cursor.execute("SELECT id, name FROM artists")
            artist_lookup = {r["name"].lower(): r["id"] for r in cursor.fetchall()}

            # Pre-cache existing album titles
            cursor.execute("SELECT id, title, artist_id FROM albums")
            album_lookup = {(r["title"].lower(), r["artist_id"]): r["id"] for r in cursor.fetchall()}
            cursor.execute("SELECT id FROM songs")
            existing_song_ids = {r["id"] for r in cursor.fetchall()}
            seen_song_ids = set()

            reader = pd.read_csv(file_path, chunksize=chunk_size)
            for chunk_df in reader:
                chunk_index += 1
                init_len = len(chunk_df)
                total_processed += init_len

                # Deduplication within chunk
                subset_cols = [c for c in ["track_id", "track_name", "artists"] if c in chunk_df.columns]
                if subset_cols:
                    chunk_df = chunk_df.drop_duplicates(subset=subset_cols)
                dup_count = init_len - len(chunk_df)
                total_duplicates += dup_count

                new_artists = []
                new_albums = []
                songs_batch = []
                features_batch = []

                for _, row in chunk_df.iterrows():
                    try:
                        raw_artist = _text_value(row.get("artists", row.get("artist_name")), "Unknown Artist")
                        primary_art = re.split(r"[;,]", raw_artist)[0].strip() or "Unknown Artist"
                        art_key = primary_art.lower()

                        if art_key not in artist_lookup:
                            art_id = f"art_{uuid.uuid4().hex[:8]}"
                            artist_lookup[art_key] = art_id
                            genre_str = str(row.get("track_genre", row.get("genre", ""))).lower()
                            country = "India" if any(k in genre_str for k in ["bollywood", "indian", "hindi", "punjabi"]) else "International"
                            new_artists.append((art_id, primary_art, country))
                        else:
                            art_id = artist_lookup[art_key]

                        alb_title = _text_value(row.get("album_name", row.get("album_title")), "Single")
                        alb_key = (alb_title.lower(), art_id)

                        if alb_key not in album_lookup:
                            alb_id = f"alb_{uuid.uuid4().hex[:8]}"
                            album_lookup[alb_key] = alb_id
                            new_albums.append((alb_id, alb_title, art_id))
                        else:
                            alb_id = album_lookup[alb_key]

                        s_id = _text_value(row.get("track_id", row.get("song_id")), "")
                        title = _text_value(row.get("track_name", row.get("title")), "Unknown Track", 200)
                        if not s_id:
                            s_id = _stable_song_id(primary_art, alb_title, title)
                        if s_id in seen_song_ids:
                            total_duplicates += 1
                            continue

                        duration_ms = _number_value(row.get("duration_ms"), 180000, integer=True)
                        popularity = max(0, min(100, _number_value(row.get("popularity"), 50, integer=True)))
                        genre = _text_value(row.get("track_genre", row.get("genre")), "pop").lower()
                        lang = "Hindi" if any(k in genre for k in ["bollywood", "indian", "hindi", "punjabi"]) else "English"
                        explicit = 1 if _text_value(row.get("explicit"), "").lower() in ["true", "1"] else 0
                        is_hit = 1 if popularity >= 70 else 0
                        release_year = _release_year_value(row)

                        songs_batch.append((
                            s_id, title, art_id, alb_id,
                            duration_ms, release_year, popularity, genre, lang, explicit, is_hit
                        ))

                        dance = max(0.0, min(1.0, _number_value(row.get("danceability"), 0.5)))
                        energy = max(0.0, min(1.0, _number_value(row.get("energy"), 0.5)))
                        key_val = max(0, min(11, _number_value(row.get("key"), 0, integer=True)))
                        loudness = _number_value(row.get("loudness"), -10.0)
                        mode_val = max(0, min(1, _number_value(row.get("mode"), 1, integer=True)))
                        speech = max(0.0, min(1.0, _number_value(row.get("speechiness"), 0.05)))
                        acoust = max(0.0, min(1.0, _number_value(row.get("acousticness"), 0.5)))
                        instr = max(0.0, min(1.0, _number_value(row.get("instrumentalness"), 0.0)))
                        live = max(0.0, min(1.0, _number_value(row.get("liveness"), 0.15)))
                        val = max(0.0, min(1.0, _number_value(row.get("valence"), 0.5)))
                        tempo = max(1.0, _number_value(row.get("tempo"), 120.0))
                        time_sig = max(1, _number_value(row.get("time_signature"), 4, integer=True))

                        features_batch.append((
                            s_id, dance, energy, key_val, loudness, mode_val,
                            speech, acoust, instr, live, val, tempo, time_sig
                        ))
                        seen_song_ids.add(s_id)
                        if s_id not in existing_song_ids:
                            total_inserted += 1
                            existing_song_ids.add(s_id)
                    except Exception as row_ex:
                        total_rejected += 1

                # Execute batch inserts for this chunk
                if new_artists:
                    cursor.executemany("INSERT OR IGNORE INTO artists (id, name, country) VALUES (?, ?, ?)", new_artists)
                if new_albums:
                    cursor.executemany("INSERT OR IGNORE INTO albums (id, title, artist_id) VALUES (?, ?, ?)", new_albums)
                if songs_batch:
                    cursor.executemany("""
                        INSERT INTO songs
                        (id, title, artist_id, album_id, duration_ms, release_year, popularity, genre, language, explicit, is_hit)
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
                    """, songs_batch)
                if features_batch:
                    cursor.executemany("""
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
                    """, features_batch)

                conn.commit()

                if progress_callback:
                    progress_callback(min(total_processed, total_estimated), total_estimated, chunk_index)

            # Record Ingestion Audit Run
            cursor.execute("""
                INSERT INTO data_quality_runs
                (source_name, total_rows, inserted_rows, duplicate_rows, rejected_rows, missing_values_json, status_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                source_name, total_processed, total_inserted, total_duplicates, total_rejected,
                json.dumps({"chunks_processed": chunk_index}),
                f"Full loop completed: {total_inserted} songs inserted across {chunk_index} batch loops."
            ))
            conn.commit()
            invalidate_analytics_cache()

        report = DataQualityReport(
            source_name=source_name,
            total_rows=total_processed,
            inserted_rows=total_inserted,
            duplicate_rows=total_duplicates,
            rejected_rows=total_rejected,
            missing_values={"chunks_processed": chunk_index},
            status_message=f"Loop complete! Ingested {total_inserted:,} songs in {chunk_index} batch chunks."
        )
        return report

    def process_and_ingest(self, file_path_or_buffer, source_name: str = "Kaggle Spotify 114K", max_rows: Optional[int] = None) -> DataQualityReport:
        """Cleans, normalizes, and loads tabular music data into SQLite database."""
        if isinstance(file_path_or_buffer, (str, Path)) and max_rows is None:
            return self.ingest_full_dataset_in_chunks(file_path_or_buffer, source_name=source_name)

        if isinstance(file_path_or_buffer, (str, Path)):
            df = pd.read_csv(file_path_or_buffer, nrows=max_rows)
        else:
            df = pd.read_csv(file_path_or_buffer, nrows=max_rows)
            
        total_rows = len(df)
        missing_counts = df.isnull().sum().to_dict()

        # Deduplication
        subset_cols = [c for c in ["track_id", "track_name", "artists"] if c in df.columns]
        if subset_cols:
            initial_count = len(df)
            df = df.drop_duplicates(subset=subset_cols)
            duplicate_rows = initial_count - len(df)
        else:
            duplicate_rows = 0

        # Column standard mapping
        col_map = {
            "track_id": "song_id",
            "track_name": "title",
            "name": "title",
            "artists": "artist_name",
            "artist": "artist_name",
            "album_name": "album_title",
            "track_genre": "genre"
        }
        for old_col, new_col in col_map.items():
            if old_col in df.columns and new_col not in df.columns:
                df[new_col] = df[old_col]

        if "title" not in df.columns:
            raise ValueError("CSV missing required title/track_name column.")
        
        if "artist_name" not in df.columns:
            raise ValueError("CSV missing required artists/artist column.")

        for column, default in (("title", "Unknown Track"), ("artist_name", "Unknown Artist"), ("album_title", "Single"), ("genre", "bollywood")):
            if column not in df.columns:
                df[column] = default
            df[column] = df[column].fillna(default).astype(str).replace({"nan": default, "None": default}).str.strip()

        df["primary_artist"] = df["artist_name"].apply(lambda x: re.split(r"[;,]", x)[0].strip() if x else "Unknown Artist")
        df["duration_ms"] = pd.to_numeric(df.get("duration_ms", pd.Series(180000, index=df.index)), errors="coerce").fillna(180000).astype(int)
        df["popularity"] = pd.to_numeric(df.get("popularity", pd.Series(50, index=df.index)), errors="coerce").fillna(50).clip(0, 100).astype(int)
        release_column = next((column for column in ("release_year", "year", "album_release_year", "release_date") if column in df.columns), None)
        if release_column:
            df["release_year"] = pd.to_numeric(
                df[release_column].astype(str).str.extract(r"((?:19|20)\d{2})")[0],
                errors="coerce",
            ).astype("Int64")
        else:
            df["release_year"] = pd.Series(pd.array([None] * len(df), dtype="Int64"), index=df.index)
        
        if "explicit" in df.columns:
            df["explicit"] = df["explicit"].apply(lambda x: 1 if str(x).lower() in ("true", "1") else 0)
        else:
            df["explicit"] = 0

        df["is_hit"] = df["popularity"].apply(lambda p: 1 if p >= 70 else 0)

        audio_defaults = {
            "danceability": 0.5,
            "energy": 0.5,
            "key": 0,
            "loudness": -10.0,
            "mode": 1,
            "speechiness": 0.05,
            "acousticness": 0.5,
            "instrumentalness": 0.0,
            "liveness": 0.15,
            "valence": 0.5,
            "tempo": 120.0,
            "time_signature": 4,
        }
        for ac, default in audio_defaults.items():
            if ac in df.columns:
                df[ac] = pd.to_numeric(df[ac], errors="coerce").fillna(default)
            else:
                df[ac] = pd.Series(default, index=df.index)
        for column in ("danceability", "energy", "speechiness", "acousticness", "instrumentalness", "liveness", "valence"):
            df[column] = df[column].clip(0.0, 1.0)
        df["key"] = df["key"].clip(0, 11).round().astype(int)
        df["mode"] = df["mode"].clip(0, 1).round().astype(int)
        df["tempo"] = df["tempo"].clip(lower=1.0)
        df["time_signature"] = df["time_signature"].clip(lower=1).round().astype(int)

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA synchronous = NORMAL")
            cursor.execute("PRAGMA journal_mode = WAL")

            cursor.execute("SELECT id, name FROM artists")
            artist_lookup = {r["name"].lower(): r["id"] for r in cursor.fetchall()}

            cursor.execute("SELECT id, title, artist_id FROM albums")
            album_lookup = {(r["title"].lower(), r["artist_id"]): r["id"] for r in cursor.fetchall()}
            cursor.execute("SELECT id FROM songs")
            existing_song_ids = {r["id"] for r in cursor.fetchall()}
            seen_song_ids = set()

            new_artists = []
            new_albums = []
            songs_batch = []
            features_batch = []
            rejected_count = 0

            for _, row in df.iterrows():
                try:
                    art_name = row["primary_artist"]
                    art_key = art_name.lower()
                    
                    if art_key not in artist_lookup:
                        art_id = f"art_{uuid.uuid4().hex[:8]}"
                        artist_lookup[art_key] = art_id
                        new_artists.append((art_id, art_name, "India" if "bollywood" in row["genre"].lower() or "hindi" in row["genre"].lower() else "International"))
                    else:
                        art_id = artist_lookup[art_key]

                    alb_title = row["album_title"]
                    alb_key = (alb_title.lower(), art_id)
                    if alb_key not in album_lookup:
                        alb_id = f"alb_{uuid.uuid4().hex[:8]}"
                        album_lookup[alb_key] = alb_id
                        new_albums.append((alb_id, alb_title, art_id))
                    else:
                        alb_id = album_lookup[alb_key]

                    title = _text_value(row["title"], "Unknown Track", 200)
                    s_id = _text_value(row.get("song_id"), "")
                    if not s_id:
                        s_id = _stable_song_id(art_name, alb_title, title)
                    if s_id in seen_song_ids:
                        duplicate_rows += 1
                        continue

                    genre_val = str(row["genre"]).lower()
                    lang_val = "Hindi" if "bollywood" in genre_val or "indian" in genre_val or "hindi" in genre_val else "English"

                    songs_batch.append((
                        s_id, title, art_id, alb_id,
                        int(row["duration_ms"]), _release_year_value(row),
                        int(row["popularity"]), row["genre"],
                        lang_val, int(row["explicit"]), int(row["is_hit"])
                    ))

                    features_batch.append((
                        s_id, float(row["danceability"]), float(row["energy"]),
                        int(row["key"]), float(row["loudness"]), int(row["mode"]),
                        float(row["speechiness"]), float(row["acousticness"]),
                        float(row["instrumentalness"]), float(row["liveness"]),
                        float(row["valence"]), float(row["tempo"]), int(row["time_signature"])
                    ))
                    seen_song_ids.add(s_id)
                except Exception:
                    rejected_count += 1

            if new_artists:
                cursor.executemany("INSERT OR IGNORE INTO artists (id, name, country) VALUES (?, ?, ?)", new_artists)
            if new_albums:
                cursor.executemany("INSERT OR IGNORE INTO albums (id, title, artist_id) VALUES (?, ?, ?)", new_albums)
            if songs_batch:
                cursor.executemany("""
                    INSERT INTO songs
                    (id, title, artist_id, album_id, duration_ms, release_year, popularity, genre, language, explicit, is_hit)
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
                """, songs_batch)
            if features_batch:
                cursor.executemany("""
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
                """, features_batch)

            conn.commit()
            inserted_count = sum(1 for song in songs_batch if song[0] not in existing_song_ids)

            # Record Ingestion Audit Run
            cursor.execute("""
                INSERT INTO data_quality_runs
                (source_name, total_rows, inserted_rows, duplicate_rows, rejected_rows, missing_values_json, status_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                source_name, total_rows, inserted_count, duplicate_rows, rejected_count,
                json.dumps({k: int(v) for k, v in missing_counts.items()}),
                f"Successfully ingested {inserted_count} songs with {rejected_count} rejections."
            ))
            conn.commit()
            invalidate_analytics_cache()

        report = DataQualityReport(
            source_name=source_name,
            total_rows=total_rows,
            inserted_rows=inserted_count,
            duplicate_rows=duplicate_rows,
            rejected_rows=rejected_count,
            missing_values={k: int(v) for k, v in missing_counts.items()},
            status_message=f"Ingestion complete: {inserted_count} inserted, {duplicate_rows} duplicate, {rejected_count} rejected."
        )
        return report

    def get_latest_quality_report(self) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM data_quality_runs ORDER BY run_at DESC LIMIT 1")
            row = cursor.fetchone()
            return dict(row) if row else None
