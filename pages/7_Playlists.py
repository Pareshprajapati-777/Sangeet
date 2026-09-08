"""
7. Playlists Page for Sangeet.
"""

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.utils.theme import apply_sangeet_theme
from src.views.playlists import render_playlists

apply_sangeet_theme("🎧 7. Playlists & Favorites — Sangeet", "🎧")
render_playlists()
