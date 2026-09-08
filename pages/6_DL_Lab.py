"""
6. Deep Learning Lab Page for Sangeet.
"""

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.utils.theme import apply_sangeet_theme
from src.views.dl_lab import render_dl_lab

apply_sangeet_theme("🧠 6. Deep Learning Lab — Sangeet", "🧠")
render_dl_lab()
