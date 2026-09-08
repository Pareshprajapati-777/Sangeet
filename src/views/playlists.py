"""
Playlists view module for Sangeet.
"""

import html
import streamlit as st
from src.repositories.playlists import PlaylistRepository
from src.utils.audio_mock import render_audio_preview_player
from src.utils.theme import render_hero_banner

def render_playlists():
    render_hero_banner(
        "playlist",
        "Playlists & User Personalization",
        "Organize custom collections, explore curated sets, and audition saved favorite tracks with seamless looping."
    )

    playlist_repo = PlaylistRepository()

    tab_playlists, tab_favs, tab_create = st.tabs(["📚 Catalog Playlists", "❤️ My Favorites", "➕ Create Playlist"])

    with tab_playlists:
        playlists = playlist_repo.get_all_playlists()
        if not playlists:
            st.info("No playlists found.")
        else:
            col_list, col_content = st.columns([1, 2])
            with col_list:
                st.subheader("Playlists")
                selected_p = st.radio(
                    "Select Playlist",
                    playlists,
                    format_func=lambda p: f"{p.get('cover_emoji', '🎵')} {p['name']} ({p.get('song_count', 0)})",
                    label_visibility="collapsed",
                    key="pl_select_radio"
                )

            with col_content:
                if selected_p:
                    st.subheader(f"{selected_p.get('cover_emoji', '🎵')} {selected_p['name']}")
                    st.caption(selected_p.get("description", ""))

                    p_songs = playlist_repo.get_playlist_songs(selected_p["id"])
                    if not p_songs:
                        st.info("This playlist is currently empty.")
                    else:
                        for s in p_songs:
                            st.markdown(f"""
                            <div style="margin-bottom: 6px;">
                                <strong style="color: #0f172a; font-size: 15px;">{html.escape(str(s['title']))}</strong> — <span style="color: #4f46e5; font-weight: 600;">{html.escape(str(s['artist_name']))}</span>
                                <span class="badge badge-genre">{html.escape(str(s['genre']))}</span>
                            </div>
                            """, unsafe_allow_html=True)
                            render_audio_preview_player(
                                song_id=f"pl_{s['id']}",
                                title=s["title"],
                                artist=s["artist_name"],
                                tempo=s.get("tempo", 120.0),
                                energy=s.get("energy", 0.7),
                                key=s.get("key", 0),
                            )
                            st.markdown("<hr style='border-color: rgba(203, 213, 225, 0.4); margin: 8px 0;'/>", unsafe_allow_html=True)

    with tab_favs:
        st.subheader("Your Favorited Tracks")
        fav_songs = playlist_repo.get_favorite_songs()
        if not fav_songs:
            st.info("You haven't favorited any songs yet. Use the 🤍 button in Search to save favorites!")
        else:
            st.markdown(f"Found **{len(fav_songs)} favorited tracks**:")
            for s in fav_songs:
                st.markdown(f"🎵 <strong style='color: #0f172a;'>{html.escape(str(s['title']))}</strong> by <span style='color: #4f46e5; font-weight: 600;'>{html.escape(str(s['artist_name']))}</span> ({html.escape(str(s['genre']).title())})", unsafe_allow_html=True)
                render_audio_preview_player(
                    song_id=f"fav_{s['id']}",
                    title=s["title"],
                    artist=s["artist_name"],
                    tempo=s.get("tempo", 120.0),
                    energy=s.get("energy", 0.7),
                    key=s.get("key", 0),
                )
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    with tab_create:
        st.subheader("Create a New Playlist")
        with st.form("view_new_playlist_form"):
            p_name = st.text_input("Playlist Name *", placeholder="e.g. Late Night Acoustic Vibes")
            p_desc = st.text_area("Description", placeholder="Calming unplugged acoustic tunes for evening focus...")
            p_emoji = st.selectbox("Cover Emoji", ["🎵", "✨", "🌙", "🔥", "☕", "🚀", "🎸", "🌊", "🎧"])
            
            submitted = st.form_submit_button("Create Playlist")
            if submitted:
                if not p_name:
                    st.error("Please enter a playlist name.")
                else:
                    p_id = playlist_repo.create_playlist(p_name, p_desc, p_emoji)
                    st.success(f"Playlist '{p_name}' created successfully!")
                    st.rerun()
