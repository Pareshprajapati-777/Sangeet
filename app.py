"""
Sangeet — Music Intelligence Platform.
Unified 9-tab Application in White Glass theme:
1. Dashboard
2. Analytics
3. Data Management
4. Search
5. Artist Map
6. Artist Photo + Catalog + DL
7. Recommendations + ML Prediction
8. Playlists
9. AI Assistant
"""

import sys
from pathlib import Path

# Ensure project root in python path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from src.db import init_db
from src.utils.theme import apply_sangeet_theme
from src.views import (
    render_dashboard,
    render_analytics,
    render_data_manager,
    render_search,
    render_playlists,
    render_assistant,
    render_location_map,
    render_artist_intelligence,
    render_song_prediction_generation,
)

try:
    init_db()
except Exception as exc:
    st.error(f"Sangeet could not initialize its local database: {exc}")
    st.stop()

# Apply Universal White Glass Theme
apply_sangeet_theme("Sangeet — Music Intelligence Platform", "🎵")

# Sidebar Navigation
modules = {
    "📊 1. Dashboard": render_dashboard,
    "📈 2. Analytics": render_analytics,
    "📥 3. Data Management": render_data_manager,
    "🔍 4. Search": render_search,
    "🗺️ 5. Artist Map": render_location_map,
    "📸 6. Artist Photo + Catalog + DL": render_artist_intelligence,
    "🎵 7. Song Prediction / Generation": render_song_prediction_generation,
    "🎧 8. Playlists": render_playlists,
    "🤖 9. AI Assistant": render_assistant,
}


with st.sidebar:
    st.markdown("""
        <div class="sidebar-modules-header">
            <span style="font-size: 11px; font-weight: 800; letter-spacing: 0.12em; color: #4338ca; text-transform: uppercase;">🧭 Platform Modules</span>
            <span class="modules-live-tag">LIVE</span>
        </div>
    """, unsafe_allow_html=True)
    for mod in modules.keys():
        st.markdown(
            f"""
            <div class="sidebar-nav-pill">
                <span class="nav-pill-text">{mod}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# Main Application Tabs Navigation
tabs = st.tabs(list(modules.keys()))
for tab, render_fn in zip(tabs, modules.values()):
    with tab:
        render_fn()
