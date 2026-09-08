"""
Image intelligence service for real artist face embeddings.
"""

from typing import Any, Dict, List
import io
from pathlib import Path
import uuid

import numpy as np
from PIL import Image

from src.config import GALLERY_DIR, ROOT_DIR
from src.repositories.artists import ArtistRepository


def _face_recognition_module():
    try:
        import face_recognition
    except ImportError as exc:
        raise RuntimeError(
            "The face-recognition dependency is unavailable. Install requirements.txt to enable image intelligence."
        ) from exc
    return face_recognition


class VisionService:
    def __init__(self, confidence_threshold: float = 0.55):
        self.artist_repo = ArtistRepository()
        self.confidence_threshold = confidence_threshold

    @staticmethod
    def _read_image(image_bytes_or_file) -> Image.Image:
        if isinstance(image_bytes_or_file, bytes):
            return Image.open(io.BytesIO(image_bytes_or_file)).convert("RGB")
        return Image.open(image_bytes_or_file).convert("RGB")

    def _extract_encoding(self, image_bytes_or_file):
        face_recognition = _face_recognition_module()
        pil_image = self._read_image(image_bytes_or_file)
        image_array = np.array(pil_image)
        face_locations = face_recognition.face_locations(image_array)
        encodings = face_recognition.face_encodings(image_array, face_locations)
        return pil_image, face_locations, encodings

    @staticmethod
    def _gallery_image_exists(item: Dict[str, Any]) -> bool:
        image_path = Path(str(item.get("image_path") or ""))
        if not image_path.is_absolute():
            image_path = ROOT_DIR / image_path
        return image_path.is_file()

    def add_gallery_reference(
        self,
        artist_id: str,
        artist_name: str,
        image_bytes_or_file,
        original_name: str = "reference.jpg",
    ) -> Dict[str, Any]:
        """Validates, normalizes, stores, and indexes one real reference image."""
        pil_image, face_locations, encodings = self._extract_encoding(image_bytes_or_file)
        if not face_locations or not encodings:
            raise ValueError("No face was found in the reference image.")

        output_path = GALLERY_DIR / f"{artist_id}_{uuid.uuid4().hex[:10]}.jpg"
        pil_image.save(output_path, format="JPEG", quality=92, optimize=True)
        relative_path = output_path.relative_to(ROOT_DIR).as_posix()
        self.artist_repo.save_face_encoding(
            artist_id,
            artist_name,
            relative_path,
            encodings[0].tolist(),
        )
        return {
            "artist_id": artist_id,
            "artist_name": artist_name,
            "image_path": relative_path,
            "source_name": Path(original_name).name,
        }

    def match_artist_from_image(self, image_bytes_or_file) -> Dict[str, Any]:
        """Finds the nearest indexed artist and rejects low-confidence matches."""
        try:
            _, face_locations, uploaded_encodings = self._extract_encoding(image_bytes_or_file)
            if not face_locations:
                return {
                    "status": "no_face_detected",
                    "message": "No face detected. Upload a clear, front-facing portrait.",
                    "match": None,
                }
            if not uploaded_encodings:
                return {
                    "status": "no_encoding",
                    "message": "A face was detected, but its features could not be extracted.",
                    "match": None,
                }

            gallery_items = [
                item
                for item in self.artist_repo.get_all_face_encodings()
                if self._gallery_image_exists(item)
            ]
            if not gallery_items:
                return {
                    "status": "gallery_empty",
                    "message": "The artist gallery is empty. Add at least one real reference image below.",
                    "match": None,
                }

            target_encoding = np.asarray(uploaded_encodings[0], dtype=float)
            gallery_records = []
            gallery_encodings = []
            for item in gallery_items:
                known_encoding = np.asarray(item.get("encoding"), dtype=float)
                if known_encoding.shape != target_encoding.shape or not np.isfinite(known_encoding).all():
                    continue
                gallery_records.append(item)
                gallery_encodings.append(known_encoding)

            if not gallery_records:
                return {
                    "status": "gallery_empty",
                    "message": "No valid real face references are available. Add a reference image below.",
                    "match": None,
                }

            distances = np.linalg.norm(np.vstack(gallery_encodings) - target_encoding, axis=1)
            best_index = int(np.argmin(distances))
            best_match = gallery_records[best_index]
            highest_confidence = max(0.0, min(1.0, 1.0 - (float(distances[best_index]) / 1.2)))

            if best_match is None or highest_confidence < self.confidence_threshold:
                return {
                    "status": "unknown_face",
                    "message": "Face detected, but confidence is below the verification threshold. Unknown artist.",
                    "confidence": round(highest_confidence * 100, 1),
                    "match": None,
                }

            artist_id = best_match["artist_id"]
            artist_profile = self.artist_repo.get_by_id(artist_id)
            all_songs = self.artist_repo.get_artist_songs(artist_id, limit=None)
            albums = self.artist_repo.get_artist_albums(artist_id, limit=None)
            return {
                "status": "matched",
                "message": f"Identified {best_match['artist_name']} with {highest_confidence * 100:.1f}% confidence.",
                "confidence": round(highest_confidence * 100, 1),
                "match": best_match,
                "artist": artist_profile,
                "top_songs": all_songs[:6],
                "all_songs": all_songs,
                "albums": albums,
                "face_box": face_locations[0],
            }
        except RuntimeError as exc:
            return {"status": "missing_dependency", "message": str(exc), "match": None}
        except Exception as exc:
            return {"status": "error", "message": f"Image recognition error: {exc}", "match": None}

    def get_gallery_artists(self) -> List[Dict[str, Any]]:
        return [
            item
            for item in self.artist_repo.get_all_face_encodings()
            if self._gallery_image_exists(item)
        ]
