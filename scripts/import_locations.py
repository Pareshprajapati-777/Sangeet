"""
Import script to parse locasion.txt and populate Sangeet database locations.
"""

import os
import re
import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "Sangeet.db"
TXT_PATH = ROOT_DIR / "locasion.txt"

def parse_coords(coord_str):
    m = re.search(r'([0-9.]+)\s*°?\s*([NS]),\s*([0-9.]+)\s*°?\s*([EW])', coord_str, re.IGNORECASE)
    if m:
        lat = float(m.group(1))
        if m.group(2).upper() == 'S':
            lat = -lat
        lon = float(m.group(3))
        if m.group(4).upper() == 'W':
            lon = -lon
        return lat, lon
    return None, None

def parse_locations_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'"([^"]+)"\s*:\s*\{([^}]+)\}'
    matches = re.findall(pattern, content)
    records = []

    for key, block in matches:
        name = key.replace('_', ' ').strip()
        loc_match = re.search(r'"location"\s*:\s*"([^"]+)"', block)
        coord_match = re.search(r'"coordinates"\s*:\s*"([^"]+)"', block)
        type_match = re.search(r'"type"\s*:\s*"([^"]+)"', block)
        desc_match = re.search(r'"description"\s*:\s*"([^"]+)"', block)

        location_val = loc_match.group(1) if loc_match else ""
        coord_val = coord_match.group(1) if coord_match else ""
        type_val = type_match.group(1) if type_match else "Recording Studio"
        desc_val = desc_match.group(1) if desc_match else ""

        lat, lon = parse_coords(coord_val)
        parts = [p.strip() for p in location_val.split(',')]
        city = parts[0] if parts else ""
        state = parts[1] if len(parts) > 1 else ""

        loc_id = f"loc_{key.lower()}"

        records.append({
            "id": loc_id,
            "name": name,
            "location_type": type_val,
            "latitude": lat,
            "longitude": lon,
            "city": f"{city}, {state}".strip(", "),
            "country": "India",
            "description": desc_val,
            "raw_key": key
        })
    return records

def import_into_db():
    records = parse_locations_file(TXT_PATH)
    print(f"Parsed {len(records)} locations from {TXT_PATH.name}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    inserted = 0
    updated = 0
    for r in records:
        cursor.execute("SELECT id FROM locations WHERE id = ? OR name = ?", (r["id"], r["name"]))
        row = cursor.fetchone()
        if row:
            cursor.execute("""
                UPDATE locations
                SET name = ?, location_type = ?, latitude = ?, longitude = ?, city = ?, country = ?, description = ?
                WHERE id = ?
            """, (r["name"], r["location_type"], r["latitude"], r["longitude"], r["city"], r["country"], r["description"], row[0]))
            updated += 1
        else:
            cursor.execute("""
                INSERT INTO locations (id, name, location_type, latitude, longitude, city, country, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (r["id"], r["name"], r["location_type"], r["latitude"], r["longitude"], r["city"], r["country"], r["description"]))
            inserted += 1

    conn.commit()

    # Link iconic studios to songs/artists
    # E.g., AM Studios -> A.R. Rahman songs
    cursor.execute("SELECT id FROM songs WHERE artist_id = 'art_ar_rahman' LIMIT 3")
    ar_songs = cursor.fetchall()
    for s in ar_songs:
        cursor.execute("""
            INSERT OR IGNORE INTO song_locations (song_id, location_id, context_type, scene_notes)
            VALUES (?, ?, 'studio', 'Orchestral scoring & Dolby Atmos mixing by A.R. Rahman at AM Studios')
        """, (s[0], "loc_am_studios"))

    # Mehboob Studio -> Arijit / Lata / Kishore songs
    cursor.execute("SELECT id FROM songs WHERE artist_id IN ('art_arijit', 'art_lata', 'art_kishore') LIMIT 4")
    bollywood_songs = cursor.fetchall()
    for s in bollywood_songs:
        cursor.execute("""
            INSERT OR IGNORE INTO song_locations (song_id, location_id, context_type, scene_notes)
            VALUES (?, ?, 'filming_location', 'Filmed & recorded at legendary Mehboob Studio Bandra')
        """, (s[0], "loc_mehboob_studio"))

    # Tharangini Studio -> K.J. Yesudas or classic Malayalam tracks
    cursor.execute("SELECT s.id FROM songs s JOIN artists a ON s.artist_id = a.id WHERE a.name LIKE '%Yesudas%' LIMIT 2")
    yesudas_songs = cursor.fetchall()
    if not yesudas_songs:
        cursor.execute("SELECT s.id FROM songs s WHERE s.genre LIKE '%Classical%' OR s.genre LIKE '%Devotional%' LIMIT 2")
        yesudas_songs = cursor.fetchall()
    for s in yesudas_songs:
        cursor.execute("""
            INSERT OR IGNORE INTO song_locations (song_id, location_id, context_type, scene_notes)
            VALUES (?, ?, 'studio', 'Mastered and recorded at Tharangini Studio, Kochi')
        """, (s[0], "loc_tharangini_studio"))

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM locations")
    total_locs = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM song_locations")
    total_links = cursor.fetchone()[0]

    conn.close()
    print(f"Import complete! Inserted: {inserted}, Updated: {updated}. Total locations in DB: {total_locs}, Total song links: {total_links}")

if __name__ == "__main__":
    import_into_db()
