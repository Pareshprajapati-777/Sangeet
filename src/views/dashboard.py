"""
Dashboard view module for Sangeet.
"""

import json
import html
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.utils.theme import get_glass_plotly_layout, SVG_ICONS, render_hero_banner
from src.services.analytics import AnalyticsService
from src.services.etl import ETLService
from src.repositories.songs import SongRepository
from src.utils.audio_mock import render_audio_preview_player

def render_dashboard():
    render_hero_banner(
        "dashboard",
        "Music Intelligence Dashboard",
        "Real-time telemetry, catalog distribution, and sonic profile analysis across the Sangeet database."
    )

    analytics = AnalyticsService()
    song_repo = SongRepository()
    etl_service = ETLService()

    top_col_left, top_col_right = st.columns([4, 1])
    with top_col_right:
        if st.button("🔄 Sync Telemetry", key="dash_force_refresh", help="Force instant refresh of all KPIs and live metrics"):
            analytics.get_overview_kpis(force_refresh=True)
            st.rerun()

    kpis = analytics.get_overview_kpis()

    base_songs = 89755
    delta_songs = kpis["total_songs"] - base_songs
    delta_songs_str = f"{delta_songs:+d} Live" if delta_songs != 0 else "Live Sync"

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Songs", f"{kpis['total_songs']:,}", delta=delta_songs_str)
    col2.metric("Artists", f"{kpis['total_artists']:,}")
    col3.metric("Albums", f"{kpis['total_albums']:,}")
    col4.metric("Genres", kpis["total_genres"])
    col5.metric("Avg Popularity", f"{kpis['avg_popularity']} / 100")

    # Ingestion Health & Quality Reports
    report = etl_service.get_latest_quality_report()
    if report:
        base_114k = 114000
        total_proc = int(report.get("total_rows", base_114k) or base_114k)
        delta_114k = total_proc - base_114k
        delta_proc_str = f"{delta_114k:+d} Live CRUD" if delta_114k != 0 else "Live Sync"

        base_inserted = 105095
        inserted = int(report.get("inserted_rows", base_inserted) or base_inserted)
        delta_ins = inserted - base_inserted
        delta_ins_str = f"{delta_ins:+d} Live CRUD" if delta_ins != 0 else "Live Sync"

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Source", report.get("source_name", "N/A"))
        c2.metric("Total Processed", f"{total_proc:,}", delta=delta_proc_str)
        c3.metric("Inserted", f"{inserted:,}", delta=delta_ins_str)
        c4.metric("Duplicates Handled", f"{report.get('duplicate_rows', 0):,}")

        status_msg = report.get("status_message", "Catalog synchronized.")
        run_timestamp = report.get("run_at", "Live")
        st.markdown(
            f"""
            <div style="background: rgba(99, 102, 241, 0.08); border-left: 3px solid #4f46e5; border-radius: 6px; padding: 6px 12px; margin-top: 6px; font-size: 13px; color: #1e293b; display: flex; justify-content: space-between; align-items: center;">
                <span>🟢 <strong>Live Telemetry:</strong> {html.escape(status_msg)}</span>
                <span style="font-size: 11px; color: #64748b; font-weight: 500;">Synced: {html.escape(str(run_timestamp))}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # Row 1: Genre Breakdown & Audio Radar Chart
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Top Genres by Track Volume")
        genre_data = analytics.get_genre_distribution(limit=10)
        if genre_data:
            genres = [g["genre"].title() for g in genre_data]
            counts = [g["count"] for g in genre_data]
            pops = [g["avg_popularity"] for g in genre_data]

            fig_genres = px.bar(
                x=genres, y=counts,
                color=pops,
                labels={"x": "Genre", "y": "Track Count", "color": "Avg Popularity"},
                color_continuous_scale="Purples",
                template="plotly_white"
            )
            layout_dict = get_glass_plotly_layout()
            layout_dict["margin"] = dict(l=20, r=20, t=30, b=20)
            fig_genres.update_layout(layout_dict)
            st.plotly_chart(fig_genres)
        else:
            st.info("No genre data available.")

    with col_right:
        st.subheader("Average Audio DNA (Radar)")
        audio_avgs = analytics.get_audio_feature_averages()
        if audio_avgs:
            radar_categories = ["Danceability", "Energy", "Acousticness", "Valence", "Speechiness", "Liveness"]
            radar_values = [
                audio_avgs.get("danceability", 0.5),
                audio_avgs.get("energy", 0.5),
                audio_avgs.get("acousticness", 0.5),
                audio_avgs.get("valence", 0.5),
                audio_avgs.get("speechiness", 0.5),
                audio_avgs.get("liveness", 0.5)
            ]
            radar_categories.append(radar_categories[0])
            radar_values.append(radar_values[0])

            fig_radar = go.Figure(
                data=go.Scatterpolar(
                    r=radar_values,
                    theta=radar_categories,
                    fill="toself",
                    fillcolor="rgba(99, 102, 241, 0.25)",
                    line=dict(color="#4f46e5", width=2.5)
                )
            )
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 1], showticklabels=False),
                    bgcolor="rgba(255, 255, 255, 0.7)"
                ),
                paper_bgcolor="rgba(255, 255, 255, 0.5)",
                template="plotly_white",
                font=dict(family="Plus Jakarta Sans, sans-serif", color="#1e293b"),
                margin=dict(l=30, r=30, t=30, b=30)
            )
            st.plotly_chart(fig_radar)

    # Row 2: Top Ranked Artists & Curated Chartbusters
    col_art, col_songs = st.columns([1, 1])

    with col_art:
        st.subheader("Leading Artists in Catalog")
        artist_ranks = analytics.get_artist_rankings(limit=8)
        if artist_ranks:
            for a in artist_ranks:
                st.markdown(f"""
                <div class="song-card artist-card">
                    <div class="artist-card-left">
                        <div class="mic-popup-badge">
                            <span class="mic-wave-ring ring-1"></span>
                            <span class="mic-wave-ring ring-2"></span>
                            <span class="mic-popup-icon">🎤</span>
                        </div>
                        <div class="artist-card-details">
                            <strong class="artist-card-title">{html.escape(str(a['name']))}</strong>
                            <small class="artist-card-meta">{a['song_count']:,} Tracks In Catalog</small>
                        </div>
                    </div>
                    <div>
                        <span class="badge badge-score artist-badge-pop">★ {a['avg_popularity']} Pop</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with col_songs:
        st.subheader("Top Chartbusters & Audio Audition")
        top_songs = song_repo.get_top_songs(limit=5)
        for s in top_songs:
            st.markdown(f"""
            <div style="margin-bottom: 6px;">
                <strong style="color: #0f172a; font-size: 15px;">{html.escape(str(s['title']))}</strong> — <span style="color: #4f46e5; font-weight: 600;">{html.escape(str(s['artist_name']))}</span>
                <span class="badge badge-hit">Hit ★ {s['popularity']}</span>
            </div>
            """, unsafe_allow_html=True)
            render_audio_preview_player(
                song_id=f"dash_{s['id']}",
                title=s["title"],
                artist=s["artist_name"],
                tempo=s.get("tempo", 120.0),
                energy=s.get("energy", 0.7),
                key=s.get("key", 0),
            )
            st.markdown("<hr style='border-color: rgba(203, 213, 225, 0.4); margin: 8px 0;'/>", unsafe_allow_html=True)
