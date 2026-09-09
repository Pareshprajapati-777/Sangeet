"""
Unified Artist Intelligence Module for Sangeet (Tab 6).
Includes:
1. Photo Catalog & Real Gallery Face Verification
2. Image-based Music Artist Recognition & Profile Linkage
"""

from pathlib import Path
from PIL import Image
import pandas as pd
import plotly.express as px
import streamlit as st

from src.services.music_artist_classifier import MusicArtistClassifierService
from src.utils.audio_mock import render_audio_preview_player
from src.utils.theme import get_svg_icon_html, render_hero_banner
from src.views.vision import render_vision


def _render_music_artist_classifier_tab():
    """Sub-tab 2: Image-based Music Artist Recognition."""
    mic_html = get_svg_icon_html("mic", 26)
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; background: rgba(255,255,255,0.78); backdrop-filter: blur(16px); padding: 14px 22px; border-radius: 16px; border: 1px solid rgba(226,232,240,0.85); box-shadow: 0 4px 18px -4px rgba(99,102,241,0.08);">
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(168,85,247,0.15) 100%); display: flex; align-items: center; justify-content: center; border: 1px solid rgba(99,102,241,0.25); box-shadow: 0 2px 8px rgba(99,102,241,0.12);">
                {mic_html}
            </div>
            <div>
                <div style="font-size: 1.1rem; font-weight: 800; color: #0f172a; font-family: 'Outfit', sans-serif; letter-spacing: -0.01em;">
                    Music Artist Prediction (Image-based)
                </div>
                <div style="font-size: 0.84rem; color: #64748b; margin-top: 1px;">
                    128-D facial biometrics & deep visual feature matching across Indian & Global music artists
                </div>
            </div>
        </div>
        <div style="display: inline-flex; align-items: center; gap: 6px; font-size: 0.82rem; color: #4338ca; font-weight: 700; background: #eef2ff; border: 1px solid rgba(99,102,241,0.25); padding: 5px 14px; border-radius: 20px;">
            <span>🎤</span> <span>Verified Music Catalog</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "music_artist_service" not in st.session_state:
        st.session_state.music_artist_service = MusicArtistClassifierService()
    service = st.session_state.music_artist_service

    uploaded_file = st.file_uploader(
        "Upload any music artist portrait or photo (JPG, PNG, WEBP):",
        type=["jpg", "jpeg", "png", "webp"],
        key="music_artist_upload_file",
    )

    # Resolve active image
    active_img_source = None
    source_label = ""
    if uploaded_file:
        active_img_source = uploaded_file
        source_label = f"Uploaded Photo: {uploaded_file.name}"

    detect_btn = st.button("🔍 Predict Music Artist", type="primary", key="btn_detect_music_artist")

    if (detect_btn or uploaded_file) and active_img_source is not None:
        with st.spinner("Extracting facial biometrics and matching against music catalog..."):
            try:
                result = service.predict(active_img_source)
            except Exception as exc:
                st.error(f"Prediction error: {exc}")
                return

        top_artist = result["top_artist"]
        top_conf = result["top_confidence"]
        preds = result["predictions"]
        profile = result["artist_profile"] or {}
        top_songs = result["top_songs"]
        ref_path = result.get("reference_image_path")

        st.markdown("---")

        # Top Result Hero Card
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%); border-radius: 18px; padding: 24px 30px; color: white; box-shadow: 0 12px 28px -5px rgba(79,70,229,0.35); margin-bottom: 22px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
                <div>
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700; opacity: 0.9;">
                        ✓ Identified Music Artist · {result.get('match_type', 'Face Biometrics')}
                    </div>
                    <div style="font-size: 32px; font-weight: 800; margin: 4px 0; letter-spacing: -0.01em;">
                        {top_artist}
                    </div>
                    <div style="font-size: 14px; opacity: 0.92; font-weight: 500;">
                        Origin: {profile.get('country', 'India')} · Debut Year: {profile.get('debut_year', 'N/A')}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="display: inline-block; background: rgba(255,255,255,0.22); padding: 8px 24px; border-radius: 30px; font-size: 24px; font-weight: 800; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.3);">
                        {top_conf:.1f}% Match
                    </div>
                    <div style="font-size: 11px; opacity: 0.85; margin-top: 5px;">Sangeet Facial Biometrics</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Visual Comparison Columns: Detected Face vs Catalog Reference
        col_orig, col_ref = st.columns(2)
        with col_orig:
            st.markdown("##### 📸 Uploaded Portrait (Detected Bounding Box)")
            st.image(result["annotated_image"], use_container_width=True, caption=source_label)

        with col_ref:
            st.markdown("##### 👤 Official Catalog Reference Portrait")
            if ref_path and Path(ref_path).is_file():
                st.image(ref_path, use_container_width=True, caption=f"Verified Master Profile: {top_artist}")
            else:
                st.image(result["original_image"], use_container_width=True, caption=f"Matched Artist: {top_artist}")

        # Artist Details & Probability Distribution
        col_meta, col_chart = st.columns([3, 3])
        with col_meta:
            st.markdown(f"##### 🎵 Artist Profile: **{top_artist}**")
            st.markdown(f"**Origin & Country:** {profile.get('country', 'India')}")
            st.markdown(f"**Debut Era:** {profile.get('debut_year', 'N/A')}")
            bio_text = profile.get("bio") or f"Renowned music legend {top_artist} with timeless discography in Indian and global music."
            st.markdown(f"**Biography:**\n> {bio_text}")

        with col_chart:
            df_chart = pd.DataFrame(preds)
            fig = px.bar(
                df_chart,
                x="percentage",
                y="artist",
                orientation="h",
                color="percentage",
                color_continuous_scale="Viridis",
                title="Top Music Artist Candidate Probabilities (%)",
                text="percentage",
            )
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(
                paper_bgcolor="rgba(255, 255, 255, 0.5)",
                plot_bgcolor="rgba(248, 250, 252, 0.6)",
                font=dict(family="Outfit, sans-serif", color="#1e293b"),
                yaxis=dict(autorange="reversed", title=""),
                xaxis=dict(title="Match Probability (%)", range=[0, max(top_conf * 1.25, 40)]),
                margin=dict(l=10, r=30, t=40, b=20),
                coloraxis_showscale=False,
                height=260,
            )
            st.plotly_chart(fig, use_container_width=True)

        # Top Hit Tracks
        st.markdown("---")
        st.markdown(f"#### 🎧 Top Hit Tracks by {top_artist}")
        if top_songs:
            for song in top_songs:
                render_audio_preview_player(
                    song_id=f"pred_artist_{song['id']}",
                    title=song["title"],
                    artist=song.get("artist_name") or top_artist,
                    tempo=song.get("tempo", 122.0),
                    energy=song.get("energy", 0.6),
                    key=song.get("key", 0),
                )
        else:
            st.info(f"No songs currently linked to {top_artist} in the quick catalog.")


def render_artist_intelligence():
    """Main entry point for Tab 6."""
    render_hero_banner(
        "mic",
        "Artist Visual Intelligence & Recognition",
        "Facial Portrait Cataloging · Image-Based Music Artist Prediction · Sangeet Biometrics",
    )

    tab_vision, tab_music_artist = st.tabs([
        "👤 1. Photo Catalog & Face Verification",
        "🎤 2. Music Artist Recognition (Image-based)",
    ])

    with tab_vision:
        render_vision(show_hero=False)

    with tab_music_artist:
        _render_music_artist_classifier_tab()
