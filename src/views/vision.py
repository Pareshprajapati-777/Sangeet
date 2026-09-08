"""Artist image intelligence view."""

import streamlit as st

from src.config import MAX_UPLOAD_SIZE_MB
from src.repositories.artists import ArtistRepository
from src.services.vision import VisionService
from src.utils.audio_mock import render_audio_preview_player
from src.utils.theme import render_hero_banner


def render_vision(show_hero: bool = True):
    if show_hero:
        render_hero_banner(
            "robot",
            "Image Intelligence",
            "Match a clear artist portrait against real gallery references, then browse every linked song and album.",
        )

    vision_service = VisionService()
    artist_repo = ArtistRepository()
    image_file = st.file_uploader(
        f"Upload a portrait (maximum {MAX_UPLOAD_SIZE_MB} MB)",
        type=["jpg", "jpeg", "png", "webp"],
        key="vision_match_upload",
    )
    if image_file:
        if image_file.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            st.error(f"The image is larger than the {MAX_UPLOAD_SIZE_MB} MB limit.")
        else:
            result = vision_service.match_artist_from_image(image_file.getvalue())
            if result["status"] == "matched":
                artist = result["artist"] or {}
                st.success(result["message"])
                st.metric("Verification confidence", f"{result['confidence']:.1f}%")
                st.subheader(artist.get("name", "Matched artist"))
                st.write(artist.get("bio") or "No biography is available.")
                all_songs = result.get("all_songs", result.get("top_songs", []))
                albums = result.get("albums", [])
                with st.expander("All songs & albums", expanded=True):
                    if albums:
                        st.markdown(f"**Albums ({len(albums):,})**")
                        st.dataframe(
                            [
                                {
                                    "Album": album["title"],
                                    "Release year": str(album.get("release_year") or "N/A"),
                                    "Songs": int(album.get("song_count", 0)),
                                }
                                for album in albums
                            ],
                            hide_index=True,
                            use_container_width=True,
                        )
                    if all_songs:
                        st.markdown(f"**Songs ({len(all_songs):,})**")
                        st.dataframe(
                            [
                                {
                                    "Title": song["title"],
                                    "Album": song.get("album_title") or "Single",
                                    "Genre": song.get("genre") or "Unknown",
                                    "Release year": str(song.get("release_year") or "N/A"),
                                    "Popularity": int(song.get("popularity", 0)),
                                }
                                for song in all_songs
                            ],
                            hide_index=True,
                            use_container_width=True,
                        )
                    else:
                        st.info("No songs are linked to this artist yet.")
                st.markdown("**Top tracks — listenable previews**")
                for song in result["top_songs"]:
                    render_audio_preview_player(
                        song_id=f"vision_{song['id']}",
                        title=song["title"],
                        artist=song["artist_name"],
                        tempo=song.get("tempo", 120.0),
                        energy=song.get("energy", 0.5),
                        key=song.get("key", 0),
                    )
            elif result["status"] == "gallery_empty":
                st.warning(result["message"])
            else:
                st.error(result["message"])

    with st.expander("Add a real gallery reference"):
        artists = artist_repo.get_all_artists(limit=5000)
        if not artists:
            st.info("Add an artist before creating a gallery reference.")
        else:
            artist_options = {f"{artist['name']} ({artist['id']})": artist for artist in artists}
            selected_label = st.selectbox("Artist", list(artist_options), key="vision_gallery_artist")
            reference_file = st.file_uploader(
                "Reference portrait",
                type=["jpg", "jpeg", "png", "webp"],
                key="vision_gallery_upload",
            )
            if st.button("Index reference image", key="vision_index_reference"):
                if not reference_file:
                    st.error("Choose a reference image first.")
                elif reference_file.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
                    st.error(f"The image is larger than the {MAX_UPLOAD_SIZE_MB} MB limit.")
                else:
                    artist = artist_options[selected_label]
                    try:
                        indexed = vision_service.add_gallery_reference(
                            artist["id"],
                            artist["name"],
                            reference_file.getvalue(),
                            reference_file.name,
                        )
                        st.success(f"Indexed a real reference for {indexed['artist_name']}.")
                    except Exception as exc:
                        st.error(str(exc))

    gallery = vision_service.get_gallery_artists()
    st.caption(f"Indexed real gallery references: {len(gallery)}")
