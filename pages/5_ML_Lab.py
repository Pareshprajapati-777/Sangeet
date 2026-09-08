"""
5. Machine Learning Lab Page for Sangeet.
"""

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.utils.theme import apply_sangeet_theme
from src.views.ml_lab import render_ml_lab

apply_sangeet_theme("🧪 5. Machine Learning Lab — Sangeet", "🧪")
render_ml_lab()
