"""Content-based recommendation view."""

import streamlit as st

from src.repositories.songs import SongRepository
from src.services.recommender import RecommenderService
from src.utils.audio_mock import render_audio_preview_player
from src.utils.theme import render_hero_banner


def render_recommendations():
    render_hero_banner(
        "recommend",
        "Song Recommendations",
        "Find tracks with a similar acoustic profile, see why each result was selected, and score hit potential.",
    )

    song_repo = SongRepository()
    recommender = RecommenderService()
    query = st.text_input(
        "Find a source song",
        placeholder="Search by title, artist, or album",
        key="recommendation_query",
    )
    songs = song_repo.search(query=query, limit=100) if query.strip() else song_repo.get_top_songs(limit=100)
    if not songs:
        st.info("No songs match that search.")
        return None, []

    song_options = {f"{song['title']} — {song['artist_name']} ({song['id']})": song for song in songs}
    selected_label = st.selectbox("Source song", list(song_options), key="recommendation_source")
    selected_song = song_options[selected_label]
    genres = ["All"] + sorted({song["genre"] for song in songs if song.get("genre")})
    genre_filter = st.selectbox("Optional genre filter", genres, key="recommendation_genre")

    recommendations = recommender.get_recommendations(
        selected_song["id"],
        top_n=8,
        genre_filter=genre_filter,
    )
    if not recommendations:
        st.info("This song does not have enough audio-feature data for recommendations yet.")
        return selected_song, []

    st.markdown(f"**Recommendations for {selected_song['title']}**")
    for recommendation in recommendations:
        col_info, col_audio = st.columns([3, 2])
        with col_info:
            st.markdown(
                f"**{recommendation['title']}**  \n"
                f"{recommendation['artist_name']} · {recommendation['genre']} · "
                f"{recommendation['similarity_score']:.1f}% acoustic similarity"
            )
            st.caption(f"Why: {recommendation['explanation']}")
        with col_audio:
            render_audio_preview_player(
                song_id=f"recommendation_{recommendation['song_id']}",
                title=recommendation["title"],
                artist=recommendation["artist_name"],
                tempo=recommendation.get("tempo", 120.0),
                energy=recommendation.get("energy", 0.5),
                key=recommendation.get("key", 0),
            )

    return selected_song, recommendations
