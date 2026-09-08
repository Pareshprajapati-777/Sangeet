"""
Search view module for Sangeet.
"""

import html
import streamlit as st
from src.services.search import SearchService
from src.services.voice import VoiceService
from src.repositories.playlists import PlaylistRepository
from src.utils.audio_mock import render_audio_preview_player
from src.utils.export_helpers import to_csv_bytes, to_json_bytes
from src.utils.theme import render_hero_banner

def render_search():
    render_hero_banner(
        "search",
        "Smart Music Search & Voice",
        "Instant multi-criteria music search with voice announcements, continuous loop previews, and playlist curation."
    )

    search_service = SearchService()
    playlist_repo = PlaylistRepository()

    # Filters Row
    filter_options = search_service.get_search_filters()
    recent_queries = search_service.get_recent_searches(limit=6)

    col_search, col_voice_prompt = st.columns([3, 1])
    with col_search:
        query = st.text_input("Enter Song, Artist, or Album Name", placeholder="e.g. Tum Hi Ho, Arijit Singh, Coldplay...", key="view_search_query")
        if recent_queries:
            st.caption("Recent: " + " • ".join([f"`{q}`" for q in recent_queries]))

    with col_voice_prompt:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        st.info("💡 Tip: Search across 114K catalog tracks by genre, artist, or title.")

    with st.expander("⚙️ Advanced Filters (Genre, Language, Year, Popularity)", expanded=False):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        with f_col1:
            sel_genre = st.selectbox("Genre", filter_options["genres"][:50], index=0, key="view_sel_genre")
        with f_col2:
            sel_lang = st.selectbox("Language", filter_options["languages"][:20], index=0, key="view_sel_lang")
        with f_col3:
            filter_year = st.checkbox("Filter by release year", value=False, key="view_filter_year")
            year_range = st.slider(
                "Release Year",
                min_value=1900,
                max_value=2026,
                value=(1970, 2026),
                key="view_year_range",
                disabled=not filter_year,
            )
        with f_col4:
            min_pop = st.slider("Minimum Popularity", min_value=0, max_value=100, value=0, key="view_min_pop")

    # Perform Search
    page_size = 15
    page_num = st.number_input("Page", min_value=1, value=1, step=1, key="view_page_num")
    offset = (page_num - 1) * page_size

    res = search_service.search_catalog(
        query=query,
        genre=sel_genre,
        language=sel_lang,
        year_min=year_range[0] if filter_year else None,
        year_max=year_range[1] if filter_year else None,
        min_popularity=min_pop,
        limit=page_size,
        offset=offset
    )

    # Render Voice Summary Action
    st.markdown("### Search Summary & Voice Announcement")
    
    c_status, c_toggle = st.columns([3, 1])
    with c_toggle:
        auto_speak = st.checkbox("🔊 Auto-speak on search", value=False, key="auto_speak_toggle")
        
    with c_status:
        st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.88); 
                        border: 1px solid rgba(226, 232, 240, 0.95); 
                        border-radius: 12px; 
                        padding: 14px 18px; 
                        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.06); 
                        margin-bottom: 10px;">
                <div style="font-size: 11px; font-weight: 700; color: #4f46e5; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 2px;">
                    SPEECH TELEMETRY STATUS
                </div>
                <div style="font-size: 14.5px; font-weight: 600; color: #0f172a;">
                    {html.escape(res.summary_text)}
                </div>
            </div>
        """, unsafe_allow_html=True)

        VoiceService.render_speech_widget(
            res.summary_text,
            auto_play=auto_speak,
            button_label="Speak Voice Announcement"
        )

    st.markdown("---")

    # Render Search Results
    if res.count == 0:
        st.warning("No songs found matching your search criteria. Try relaxing your filters or checking spelling.")
    else:
        st.markdown(f"**Showing {len(res.records)} of {res.count:,} results (Page {page_num}):**")

        user_playlists = playlist_repo.get_all_playlists()
        playlist_options = {p["name"]: p["id"] for p in user_playlists}

        for song in res.records:
            safe_title = html.escape(str(song.get("title") or "Unknown Track"))
            safe_artist = html.escape(str(song.get("artist_name") or "Unknown Artist"))
            safe_album = html.escape(str(song.get("album_title") or "Single"))
            safe_genre = html.escape(str(song.get("genre") or "Unknown"))
            with st.container():
                col_info, col_audio, col_actions = st.columns([3, 2, 2])
                
                with col_info:
                    st.markdown(f"""
                    <strong style="color: #0f172a; font-size: 16px;">{safe_title}</strong><br/>
                    <span style="color: #4f46e5; font-weight: 600;">{safe_artist}</span>
                    <span style="color: #64748b;"> • {safe_album} ({html.escape(str(song.get('release_year') or 'N/A'))})</span><br/>
                    <span class="badge badge-genre">{safe_genre}</span>
                    <span class="badge badge-hit">★ {song['popularity']} Pop</span>
                    """, unsafe_allow_html=True)

                with col_audio:
                    render_audio_preview_player(
                        song_id=f"srch_{song['id']}",
                        title=song["title"],
                        artist=song["artist_name"],
                        tempo=song.get("tempo", 120.0),
                        energy=song.get("energy", 0.7),
                        key=song.get("key", 0),
                    )

                with col_actions:
                    # Favorite button
                    is_fav = playlist_repo.is_favorite("song", song["id"])
                    fav_label = "❤️ Favorited" if is_fav else "🤍 Favorite"
                    if st.button(fav_label, key=f"view_fav_{song['id']}"):
                        playlist_repo.toggle_favorite("song", song["id"])
                        st.rerun()

                    # Add to playlist
                    if playlist_options:
                        chosen_p = st.selectbox(
                            "Add to Playlist",
                            options=["-- Select --"] + list(playlist_options.keys()),
                            key=f"view_pl_sel_{song['id']}",
                            label_visibility="collapsed"
                        )
                        if chosen_p != "-- Select --":
                            p_id = playlist_options[chosen_p]
                            playlist_repo.add_song_to_playlist(p_id, song["id"])
                            st.success(f"Added to {chosen_p}!")

                st.markdown("<hr style='border-color: rgba(203, 213, 225, 0.4); margin: 12px 0;'/>", unsafe_allow_html=True)

        # Export Helpers
        st.markdown("<br/>", unsafe_allow_html=True)
        c_csv, c_json = st.columns(2)
        with c_csv:
            csv_data = to_csv_bytes(res.records)
            st.download_button("📥 Export Current Results (CSV)", data=csv_data, file_name="sangeet_search.csv", mime="text/csv", key="view_export_csv")
        with c_json:
            json_data = to_json_bytes(res.records)
            st.download_button("📥 Export Current Results (JSON)", data=json_data, file_name="sangeet_search.json", mime="application/json", key="view_export_json")
