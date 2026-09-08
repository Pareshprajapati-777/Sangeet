"""
Analytics view module for Sangeet.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.utils.theme import get_glass_plotly_layout, SVG_ICONS, render_hero_banner
from src.services.analytics import AnalyticsService
from src.repositories.songs import SongRepository

def render_analytics():
    render_hero_banner(
        "chart",
        "Music Analytics & Sonic Distributions",
        "Explore multidimensional relationships, feature correlations, and acoustic clustering across songs."
    )

    analytics = AnalyticsService()
    song_repo = SongRepository()

    # 1. Feature Scatter: Energy vs. Danceability
    st.subheader("1. Audio Vibe Mapping (Danceability vs. Energy)")
    matrix_data = song_repo.get_features_matrix(limit=1500)
    if matrix_data:
        df_matrix = pd.DataFrame(matrix_data)
        
        fig_scatter = px.scatter(
            df_matrix,
            x="danceability",
            y="energy",
            color="popularity",
            size="popularity",
            hover_data=["title", "artist_name", "genre"],
            labels={"danceability": "Danceability (Rhythm/Groove)", "energy": "Energy (Intensity)"},
            title="Danceability vs. Energy Colored by Track Popularity",
            color_continuous_scale="Purples",
            template="plotly_white"
        )
        fig_scatter.update_layout(get_glass_plotly_layout("Danceability vs. Energy"))
        st.plotly_chart(fig_scatter)

    st.markdown("---")

    # 2. Correlation Matrix Heatmap
    col_corr, col_hist = st.columns([1, 1])

    with col_corr:
        st.subheader("2. Audio Feature Correlation Heatmap")
        corr_df = analytics.get_correlation_matrix()
        if not corr_df.empty:
            fig_heat = px.imshow(
                corr_df,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="Blues",
                labels=dict(color="Correlation"),
                template="plotly_white"
            )
            fig_heat.update_layout(get_glass_plotly_layout("Audio Feature Correlation"))
            st.plotly_chart(fig_heat)
        else:
            st.info("Insufficient data for correlation analysis.")

    with col_hist:
        st.subheader("3. Valence (Musical Positivity) Distribution")
        if matrix_data:
            fig_hist = px.histogram(
                df_matrix,
                x="valence",
                nbins=30,
                color_discrete_sequence=["#6366f1"],
                title="Distribution of Musical Happiness / Mood (Valence)",
                template="plotly_white"
            )
            fig_hist.update_layout(get_glass_plotly_layout("Musical Happiness (Valence)"))
            st.plotly_chart(fig_hist)

    st.markdown("---")

    # 3. Release Year Trends
    st.subheader("4. Release History & Evolution Over Time")
    year_data = analytics.get_release_year_trends()
    if year_data:
        df_years = pd.DataFrame(year_data)
        fig_years = px.line(
            df_years,
            x="release_year",
            y="song_count",
            markers=True,
            title="Songs Released by Year in Database",
            color_discrete_sequence=["#8b5cf6"],
            template="plotly_white"
        )
        fig_years.update_layout(get_glass_plotly_layout("Catalog Trajectory Across Decades"))
        st.plotly_chart(fig_years)
