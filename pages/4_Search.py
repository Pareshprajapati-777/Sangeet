"""
4. Search & Voice Discovery Page for Sangeet.
"""

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.utils.theme import apply_sangeet_theme
from src.views.search import render_search

apply_sangeet_theme("🔍 4. Search & Voice — Sangeet", "🔍")
render_search()
