"""
2. Analytics Page for Sangeet.
"""

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.utils.theme import apply_sangeet_theme
from src.views.analytics import render_analytics

apply_sangeet_theme("📈 2. Analytics — Sangeet", "📈")
render_analytics()
