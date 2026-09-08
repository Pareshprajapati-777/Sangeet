"""
Script to download authentic music artist reference portraits and index their face encodings in Sangeet.db.
"""

import json
import sqlite3
import urllib.request
from pathlib import Path
from PIL import Image
import face_recognition

ROOT_DIR = Path(__file__).resolve().parent.parent
GALLERY_DIR = ROOT_DIR / "assets" / "artist_gallery"
DB_PATH = ROOT_DIR / "Sangeet.db"

GALLERY_DIR.mkdir(parents=True, exist_ok=True)

ARTIST_SOURCES = [
    {
        "artist_id": "art_arijit",
        "name": "Arijit Singh",
        "file_name": "arijit_singh.jpg",
        "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b7/Arijit_Singh_performance_at_Chandigarh_2025.jpg/500px-Arijit_Singh_performance_at_Chandigarh_2025.jpg?utm_source=en.wikipedia.org&utm_campaign=api&utm_content=thumbnail"
    },
    {
        "artist_id": "art_shreya",
        "name": "Shreya Ghoshal",
        "file_name": "shreya_ghoshal.jpg",
        "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a0/Shreya_Ghoshal_Behindwoods_Gold_Icons_Awards_2023_%28cropped%29.jpg/500px-Shreya_Ghoshal_Behindwoods_Gold_Icons_Awards_2023_%28cropped%29.jpg?utm_source=en.wikipedia.org&utm_campaign=api&utm_content=thumbnail"
    },
    {
        "artist_id": "art_ar_rahman",
        "name": "A. R. Rahman",
        "file_name": "ar_rahman.jpg",
        "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/1/10/AR_Rahman_at_Premier_Futsal_Press_Meet_%28cropped%29.jpg/500px-AR_Rahman_at_Premier_Futsal_Press_Meet_%28cropped%29.jpg?utm_source=en.wikipedia.org&utm_campaign=api&utm_content=thumbnail"
    },
    {
        "artist_id": "art_diljit",
        "name": "Diljit Dosanjh",
        "file_name": "diljit_dosanjh.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e2/Diljit_Dosanjh.jpg?utm_source=en.wikipedia.org&utm_campaign=api&utm_content=thumbnail_unscaled"
    },
    {
        "artist_id": "art_kishore",
        "name": "Kishore Kumar",
        "file_name": "kishore_kumar.jpg",
        "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c2/Kishore_Kumar_2016_postcard_of_India_%28cropped%29.jpg/500px-Kishore_Kumar_2016_postcard_of_India_%28cropped%29.jpg?utm_source=en.wikipedia.org&utm_campaign=api&utm_content=thumbnail"
    },
    {
        "artist_id": "art_lata",
        "name": "Lata Mangeshkar",
        "file_name": "lata_mangeshkar.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/2/2f/LataMangeshkar10.jpg?utm_source=en.wikipedia.org&utm_campaign=api&utm_content=thumbnail_unscaled"
    },
    {
        "artist_id": "art_sonu",
        "name": "Sonu Nigam",
        "file_name": "sonu_nigam.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/76/Sonu_Nigam123.jpg?utm_source=en.wikipedia.org&utm_campaign=api&utm_content=thumbnail_unscaled"
    }
]

def setup_artist_gallery():
    headers = {"User-Agent": "SangeetMusicPlatform/2.0 (music@sangeet.org)"}
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for item in ARTIST_SOURCES:
        filepath = GALLERY_DIR / item["file_name"]
        print(f"Processing {item['name']}...")
        if not filepath.exists() or filepath.stat().st_size < 1000:
            try:
                req = urllib.request.Request(item["url"], headers=headers)
                with urllib.request.urlopen(req, timeout=12) as resp:
                    data = resp.read()
                with open(filepath, "wb") as f:
                    f.write(data)
                print(f"  Downloaded {item['file_name']} ({len(data)} bytes)")
            except Exception as e:
                print(f"  Download failed for {item['name']}: {e}")
                continue

        try:
            img = face_recognition.load_image_file(str(filepath))
            locs = face_recognition.face_locations(img)
            encs = face_recognition.face_encodings(img, locs)
            if encs:
                encoding = encs[0].tolist()
                rel_path = f"assets/artist_gallery/{item['file_name']}"
                
                # Update or insert in artist_faces
                cursor.execute("SELECT id FROM artist_faces WHERE artist_id = ? OR image_path = ?", (item["artist_id"], rel_path))
                row = cursor.fetchone()
                if row:
                    cursor.execute("""
                        UPDATE artist_faces
                        SET artist_name = ?, image_path = ?, encoding_json = ?
                        WHERE id = ?
                    """, (item["name"], rel_path, json.dumps(encoding), row[0]))
                    print(f"  Updated face encoding in DB for {item['name']}")
                else:
                    cursor.execute("""
                        INSERT INTO artist_faces (artist_id, artist_name, image_path, encoding_json)
                        VALUES (?, ?, ?, ?)
                    """, (item["artist_id"], item["name"], rel_path, json.dumps(encoding)))
                    print(f"  Inserted face encoding in DB for {item['name']}")
            else:
                print(f"  Warning: No face found in {item['file_name']}")
        except Exception as e:
            print(f"  Face encoding extraction failed for {item['name']}: {e}")

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM artist_faces")
    total_faces = cursor.fetchone()[0]
    conn.close()
    print(f"Done! Total face references in DB: {total_faces}")

if __name__ == "__main__":
    setup_artist_gallery()
