"""
Data Manager view module for Sangeet.
"""

import streamlit as st
import uuid
from src.repositories.songs import SongRepository
from src.repositories.artists import ArtistRepository
from src.utils.theme import render_hero_banner

def render_data_manager():
    render_hero_banner(
        "database",
        "Catalog Management & CRUD Operations",
        "Add new songs to the catalog, update existing track metadata and audio features, or remove records."
    )

    # Flash notification from previous action
    if "dm_feedback" in st.session_state:
        f_type, f_msg = st.session_state.pop("dm_feedback")
        if f_type == "success":
            st.success(f_msg)
        elif f_type == "error":
            st.error(f_msg)
        elif f_type == "info":
            st.info(f_msg)

    song_repo = SongRepository()
    artist_repo = ArtistRepository()

    st.subheader("Add, Update, or Delete Catalog Records")
    crud_mode = st.radio("Action", ["➕ Add New Song", "✏️ Edit Existing Song", "🗑️ Delete Song"], horizontal=True, key="dm_crud_mode")

    if crud_mode == "➕ Add New Song":
        with st.form("dm_add_song_form"):
            s_title = st.text_input("Song Title *", placeholder="e.g. Kesariya")
            s_artist = st.text_input("Artist Name *", placeholder="e.g. Arijit Singh")
            s_album = st.text_input("Album Title", placeholder="e.g. Brahmastra")
            s_genre = st.selectbox("Genre", ["bollywood", "pop", "classical", "sufi", "bhangra", "rock", "lo-fi"])
            s_year = st.number_input("Release Year", min_value=1940, max_value=2026, value=2022)
            s_pop = st.slider("Popularity", 0, 100, 75)
            
            st.markdown("##### Audio Features")
            c_d, c_e, c_v = st.columns(3)
            with c_d:
                dance = st.slider("Danceability", 0.0, 1.0, 0.5)
            with c_e:
                energy = st.slider("Energy", 0.0, 1.0, 0.6)
            with c_v:
                valence = st.slider("Valence (Happiness)", 0.0, 1.0, 0.4)

            submitted = st.form_submit_button("Save Song to Catalog")
            if submitted:
                if not s_title or not s_artist:
                    st.error("Title and Artist Name are required.")
                else:
                    art_record = artist_repo.get_by_name(s_artist)
                    if not art_record:
                        art_id = f"art_{uuid.uuid4().hex[:8]}"
                        artist_repo.create_artist({"id": art_id, "name": s_artist})
                    else:
                        art_id = art_record["id"]

                    new_song_id = f"sng_{uuid.uuid4().hex[:8]}"
                    song_repo.create_song(
                        song_data={
                            "id": new_song_id,
                            "title": s_title,
                            "artist_id": art_id,
                            "release_year": int(s_year),
                            "popularity": int(s_pop),
                            "genre": s_genre,
                            "language": "Hindi",
                            "is_hit": 1 if s_pop >= 70 else 0
                        },
                        audio_data={
                            "danceability": dance,
                            "energy": energy,
                            "valence": valence
                        }
                    )
                    st.session_state["dm_feedback"] = (
                        "success",
                        f"🎉 Song '{s_title}' created successfully! Live Catalog (114K metric) and Total Songs updated live on Dashboard."
                    )
                    st.rerun()

    elif crud_mode == "✏️ Edit Existing Song":
        search_edit = st.text_input("Find Song to Edit", placeholder="Enter song title or pick from recent below...", key="dm_search_edit")
        matches = song_repo.search(query=search_edit, limit=10) if search_edit else song_repo.get_top_songs(limit=5)
        if matches:
            song_choice = st.selectbox("Select Song", matches, format_func=lambda x: f"{x['title']} — {x['artist_name']} ({x['id']})", key="dm_edit_select")
            with st.form("dm_edit_form"):
                e_title = st.text_input("Title", value=song_choice["title"])
                e_year = st.number_input("Year", value=song_choice["release_year"] or 2022)
                e_pop = st.slider("Popularity", 0, 100, int(song_choice.get("popularity", 50)))
                e_genre = st.text_input("Genre", value=song_choice.get("genre", "bollywood"))

                st.markdown("##### Audio DNA Features")
                ed_col1, ed_col2, ed_col3 = st.columns(3)
                with ed_col1:
                    e_dance = st.slider("Danceability", 0.0, 1.0, float(song_choice.get("danceability") or 0.5))
                with ed_col2:
                    e_energy = st.slider("Energy", 0.0, 1.0, float(song_choice.get("energy") or 0.5))
                with ed_col3:
                    e_val = st.slider("Valence", 0.0, 1.0, float(song_choice.get("valence") or 0.5))

                e_save = st.form_submit_button("Update Song")
                if e_save:
                    song_repo.update_song(
                        song_id=song_choice["id"],
                        song_data={
                            "title": e_title,
                            "release_year": int(e_year),
                            "popularity": int(e_pop),
                            "genre": e_genre,
                            "language": song_choice.get("language", "Hindi"),
                            "is_hit": 1 if e_pop >= 70 else 0
                        },
                        audio_data={
                            "danceability": e_dance,
                            "energy": e_energy,
                            "valence": e_val
                        }
                    )
                    st.session_state["dm_feedback"] = (
                        "success",
                        f"✏️ Song '{e_title}' updated successfully! Dashboard metrics, audio DNA, and charts updated live."
                    )
                    st.rerun()
        else:
            st.info("No matching songs found.")

    elif crud_mode == "🗑️ Delete Song":
        del_search = st.text_input("Find Song to Delete", placeholder="Enter song title or pick from recent below...", key="dm_del_search")
        del_matches = song_repo.search(query=del_search, limit=10) if del_search else song_repo.get_top_songs(limit=5)
        if del_matches:
            del_choice = st.selectbox("Select Song to Delete", del_matches, format_func=lambda x: f"{x['title']} — {x['artist_name']} ({x['id']})", key="dm_del_select")
            st.warning(f"Are you sure you want to permanently delete '{del_choice['title']}'?")
            if st.button("Confirm Delete", type="primary", key="dm_del_confirm"):
                song_repo.delete_song(del_choice["id"])
                st.session_state["dm_feedback"] = (
                    "success",
                    f"🗑️ Song '{del_choice['title']}' permanently removed! Live Catalog (114K metric) and Total Songs decremented live on Dashboard."
                )
                st.rerun()
        else:
            st.info("No songs found to delete.")
