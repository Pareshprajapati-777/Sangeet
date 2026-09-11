"""
Data Manager view module for Sangeet.
"""

import streamlit as st
import uuid
from src.repositories.songs import SongRepository
from src.repositories.artists import ArtistRepository
from src.repositories.albums import AlbumRepository
from src.utils.theme import render_hero_banner

def render_data_manager():
    render_hero_banner(
        "database",
        "Catalog Management & Live CRUD Operations",
        "Add, update, or remove songs, artists, and albums with real-time telemetry updates across the Sangeet database."
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
    album_repo = AlbumRepository()

    entity_tab = st.radio(
        "Select Catalog Entity to Manage",
        ["🎵 Songs", "🎤 Artists", "💿 Albums"],
        horizontal=True,
        key="dm_entity_tab"
    )

    # ==================== 1. SONGS MANAGEMENT ====================
    if entity_tab == "🎵 Songs":
        st.subheader("Manage Track Catalog (Live Updates: Total Songs & 114K Processed)")
        crud_mode = st.radio("Action", ["➕ Add New Song", "✏️ Edit Existing Song", "🗑️ Delete Song"], horizontal=True, key="dm_song_crud_mode")

        if crud_mode == "➕ Add New Song":
            with st.form("dm_add_song_form"):
                s_title = st.text_input("Song Title *", placeholder="e.g. Kesariya")
                s_artist = st.text_input("Artist Name *", placeholder="e.g. Arijit Singh")
                s_album = st.text_input("Album Title", placeholder="e.g. Brahmastra")
                s_genre = st.selectbox("Genre", ["bollywood", "pop", "classical", "sufi", "bhangra", "rock", "lo-fi"])
                s_year = st.number_input("Release Year", min_value=1940, max_value=2026, value=2024)
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
                        # Auto-link or auto-create artist
                        art_record = artist_repo.get_by_name(s_artist)
                        if not art_record:
                            art_id = f"art_{uuid.uuid4().hex[:8]}"
                            artist_repo.create_artist({"id": art_id, "name": s_artist, "country": "India"})
                        else:
                            art_id = art_record["id"]

                        # Auto-link or auto-create album
                        alb_id = None
                        if s_album and s_album.strip():
                            alb_title = s_album.strip()
                            alb_record = album_repo.get_by_title_and_artist(alb_title, art_id)
                            if not alb_record:
                                alb_id = f"alb_{uuid.uuid4().hex[:8]}"
                                album_repo.create_album({
                                    "id": alb_id,
                                    "title": alb_title,
                                    "artist_id": art_id,
                                    "release_year": int(s_year),
                                    "total_tracks": 1
                                })
                            else:
                                alb_id = alb_record["id"]

                        new_song_id = f"sng_{uuid.uuid4().hex[:8]}"
                        song_repo.create_song(
                            song_data={
                                "id": new_song_id,
                                "title": s_title,
                                "artist_id": art_id,
                                "album_id": alb_id,
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
                            f"🎉 Song '{s_title}' created! Total Songs, Artists, Albums, and 114K metric updated live on Dashboard."
                        )
                        st.rerun()

        elif crud_mode == "✏️ Edit Existing Song":
            search_edit = st.text_input("Find Song to Edit", placeholder="Enter song title or pick from recent below...", key="dm_search_edit")
            matches = song_repo.search(query=search_edit, limit=10) if search_edit else song_repo.get_top_songs(limit=5)
            if matches:
                song_choice = st.selectbox("Select Song", matches, format_func=lambda x: f"{x['title']} — {x['artist_name']} ({x['id']})", key="dm_edit_select")
                with st.form("dm_edit_form"):
                    e_title = st.text_input("Title", value=song_choice["title"])
                    e_year = st.number_input("Year", value=song_choice["release_year"] or 2024)
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
                            f"✏️ Song '{e_title}' updated successfully! Dashboard metrics and charts updated live."
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
                        f"🗑️ Song '{del_choice['title']}' permanently removed! Live Catalog and Total Songs decremented on Dashboard."
                    )
                    st.rerun()
            else:
                st.info("No songs found to delete.")

    # ==================== 2. ARTISTS MANAGEMENT ====================
    elif entity_tab == "🎤 Artists":
        st.subheader("Manage Artists Catalog (Live Updates: Artists Metric)")
        art_mode = st.radio("Artist Action", ["➕ Add New Artist", "✏️ Edit Artist", "🗑️ Delete Artist"], horizontal=True, key="dm_art_crud_mode")

        if art_mode == "➕ Add New Artist":
            with st.form("dm_add_artist_form"):
                a_name = st.text_input("Artist Name *", placeholder="e.g. Diljit Dosanjh")
                a_country = st.text_input("Country", value="India")
                a_birthplace = st.text_input("Birthplace / Region", placeholder="e.g. Punjab, India")
                a_debut = st.number_input("Debut Year", min_value=1940, max_value=2026, value=2010)
                a_bio = st.text_area("Biography", placeholder="Brief artist bio...")

                submitted_art = st.form_submit_button("Create Artist")
                if submitted_art:
                    if not a_name or not a_name.strip():
                        st.error("Artist Name is required.")
                    else:
                        clean_name = a_name.strip()
                        existing_art = artist_repo.get_by_name(clean_name)
                        if existing_art:
                            st.warning(f"Artist '{clean_name}' already exists in database (ID: {existing_art['id']}).")
                        else:
                            new_art_id = f"art_{uuid.uuid4().hex[:8]}"
                            artist_repo.create_artist({
                                "id": new_art_id,
                                "name": clean_name,
                                "country": a_country or "India",
                                "birthplace": a_birthplace,
                                "debut_year": int(a_debut),
                                "bio": a_bio
                            })
                            st.session_state["dm_feedback"] = (
                                "success",
                                f"🎤 Artist '{clean_name}' added! Dashboard Artists count updated live (+1 Live)."
                            )
                            st.rerun()

        elif art_mode == "✏️ Edit Artist":
            art_search = st.text_input("Find Artist to Edit", placeholder="Enter artist name...", key="dm_art_search_edit")
            art_matches = artist_repo.search_artists(art_search, limit=10) if art_search else artist_repo.get_top_artists(limit=5)
            if art_matches:
                art_choice = st.selectbox("Select Artist", art_matches, format_func=lambda x: f"{x['name']} ({x['id']})", key="dm_art_edit_select")
                with st.form("dm_edit_artist_form"):
                    ea_name = st.text_input("Name", value=art_choice["name"])
                    ea_country = st.text_input("Country", value=art_choice.get("country") or "India")
                    ea_birthplace = st.text_input("Birthplace", value=art_choice.get("birthplace") or "")
                    ea_debut = st.number_input("Debut Year", min_value=1940, max_value=2026, value=int(art_choice.get("debut_year") or 2010))

                    ea_save = st.form_submit_button("Update Artist")
                    if ea_save:
                        artist_repo.update_artist(art_choice["id"], {
                            "name": ea_name,
                            "country": ea_country,
                            "birthplace": ea_birthplace,
                            "debut_year": int(ea_debut)
                        })
                        st.session_state["dm_feedback"] = ("success", f"✏️ Artist '{ea_name}' updated successfully! Live telemetry updated.")
                        st.rerun()
            else:
                st.info("No matching artists found.")

        elif art_mode == "🗑️ Delete Artist":
            art_del_search = st.text_input("Find Artist to Delete", placeholder="Enter artist name...", key="dm_art_del_search")
            art_del_matches = artist_repo.search_artists(art_del_search, limit=10) if art_del_search else artist_repo.get_top_artists(limit=5)
            if art_del_matches:
                art_del_choice = st.selectbox("Select Artist to Delete", art_del_matches, format_func=lambda x: f"{x['name']} ({x['id']})", key="dm_art_del_select")
                st.warning(f"Are you sure you want to permanently delete '{art_del_choice['name']}'?")
                if st.button("Confirm Delete Artist", type="primary", key="dm_art_del_confirm"):
                    artist_repo.delete_artist(art_del_choice["id"])
                    st.session_state["dm_feedback"] = (
                        "success",
                        f"🗑️ Artist '{art_del_choice['name']}' deleted! Dashboard Artists count decremented live."
                    )
                    st.rerun()
            else:
                st.info("No artists found to delete.")

    # ==================== 3. ALBUMS MANAGEMENT ====================
    elif entity_tab == "💿 Albums":
        st.subheader("Manage Albums Catalog (Live Updates: Albums Metric)")
        alb_mode = st.radio("Album Action", ["➕ Add New Album", "✏️ Edit Album", "🗑️ Delete Album"], horizontal=True, key="dm_alb_crud_mode")

        if alb_mode == "➕ Add New Album":
            with st.form("dm_add_album_form"):
                alb_title_input = st.text_input("Album Title *", placeholder="e.g. Rockstar")
                alb_artist_input = st.text_input("Artist Name", placeholder="e.g. A.R. Rahman")
                alb_year_input = st.number_input("Release Year", min_value=1940, max_value=2026, value=2011)
                alb_tracks_input = st.number_input("Total Tracks", min_value=1, max_value=100, value=14)

                submitted_alb = st.form_submit_button("Create Album")
                if submitted_alb:
                    if not alb_title_input or not alb_title_input.strip():
                        st.error("Album Title is required.")
                    else:
                        clean_alb_title = alb_title_input.strip()
                        target_art_id = None
                        if alb_artist_input and alb_artist_input.strip():
                            found_art = artist_repo.get_by_name(alb_artist_input.strip())
                            if found_art:
                                target_art_id = found_art["id"]
                            else:
                                target_art_id = f"art_{uuid.uuid4().hex[:8]}"
                                artist_repo.create_artist({"id": target_art_id, "name": alb_artist_input.strip(), "country": "India"})

                        new_alb_id = f"alb_{uuid.uuid4().hex[:8]}"
                        album_repo.create_album({
                            "id": new_alb_id,
                            "title": clean_alb_title,
                            "artist_id": target_art_id,
                            "release_year": int(alb_year_input),
                            "total_tracks": int(alb_tracks_input)
                        })
                        st.session_state["dm_feedback"] = (
                            "success",
                            f"💿 Album '{clean_alb_title}' created! Dashboard Albums count updated live (+1 Live)."
                        )
                        st.rerun()

        elif alb_mode == "✏️ Edit Album":
            alb_search = st.text_input("Find Album to Edit", placeholder="Enter album title...", key="dm_alb_search_edit")
            alb_matches = album_repo.search_albums(alb_search, limit=10) if alb_search else album_repo.get_all_albums(limit=5)
            if alb_matches:
                alb_choice = st.selectbox("Select Album", alb_matches, format_func=lambda x: f"{x['title']} — {x.get('artist_name') or 'N/A'} ({x['id']})", key="dm_alb_edit_select")
                with st.form("dm_edit_album_form"):
                    ea_title = st.text_input("Album Title", value=alb_choice["title"])
                    ea_year = st.number_input("Release Year", min_value=1940, max_value=2026, value=int(alb_choice.get("release_year") or 2020))
                    ea_tracks = st.number_input("Total Tracks", min_value=1, max_value=100, value=int(alb_choice.get("total_tracks") or 1))

                    ea_save = st.form_submit_button("Update Album")
                    if ea_save:
                        album_repo.update_album(alb_choice["id"], {
                            "title": ea_title,
                            "artist_id": alb_choice.get("artist_id"),
                            "release_year": int(ea_year),
                            "total_tracks": int(ea_tracks)
                        })
                        st.session_state["dm_feedback"] = ("success", f"✏️ Album '{ea_title}' updated successfully! Live telemetry updated.")
                        st.rerun()
            else:
                st.info("No matching albums found.")

        elif alb_mode == "🗑️ Delete Album":
            alb_del_search = st.text_input("Find Album to Delete", placeholder="Enter album title...", key="dm_alb_del_search")
            alb_del_matches = album_repo.search_albums(alb_del_search, limit=10) if alb_del_search else album_repo.get_all_albums(limit=5)
            if alb_del_matches:
                alb_del_choice = st.selectbox("Select Album to Delete", alb_del_matches, format_func=lambda x: f"{x['title']} — {x.get('artist_name') or 'N/A'} ({x['id']})", key="dm_alb_del_select")
                st.warning(f"Are you sure you want to permanently delete '{alb_del_choice['title']}'?")
                if st.button("Confirm Delete Album", type="primary", key="dm_alb_del_confirm"):
                    album_repo.delete_album(alb_del_choice["id"])
                    st.session_state["dm_feedback"] = (
                        "success",
                        f"🗑️ Album '{alb_del_choice['title']}' deleted! Dashboard Albums count decremented live."
                    )
                    st.rerun()
            else:
                st.info("No albums found to delete.")
