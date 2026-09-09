"""
Unified Song Prediction & Generation Studio for Sangeet.
Combines:
1. Fast Cached ML Hit Prediction & Audio Profiler (instant inference)
2. Hugging Face Sequence Classification (tjl223/song-artist-classifier-v2)
3. Meta AI MusicGen Prompt-to-Music Generation with interactive player & download
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.services.artist_classifier import PRESET_LYRICS, ArtistClassifierService
from src.services.ml import MLService
from src.services.music_generation import GENRE_PRESETS, MusicGenerationService
from src.utils.theme import get_glass_plotly_layout, get_svg_icon_html, render_hero_banner
from src.views.recommendations import render_recommendations



def _inject_subtab_styles():
    """Apply premium styles to Tab 7 sub-tabs and controls."""
    st.markdown("""
    <style>

    /* Studio Card Panels with Sheen */
    .studio-panel {
        background: rgba(255, 255, 255, 0.88);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 24px 28px;
        box-shadow: 0 12px 36px -5px rgba(99, 102, 241, 0.08), 0 4px 12px -2px rgba(15, 23, 42, 0.03), inset 0 1px 2px #fff;
        margin-bottom: 22px;
        transition: transform 0.35s cubic-bezier(0.25, 1, 0.5, 1), box-shadow 0.35s cubic-bezier(0.25, 1, 0.5, 1);
        position: relative;
        overflow: hidden;
    }

    .studio-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
        transform: translate3d(-140%, 0, 0);
        animation: card-sheen 7s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        pointer-events: none;
        will-change: transform;
    }

    .studio-panel:hover {
        transform: translate3d(0, -2px, 0);
        box-shadow: 0 18px 42px -4px rgba(99, 102, 241, 0.16), inset 0 1px 2px #fff;
        border-color: rgba(99, 102, 241, 0.3);
    }

    .studio-panel-title {
        font-size: 1.08rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -0.01em;
    }

    .studio-panel-subtitle {
        font-size: 0.86rem;
        color: #64748b;
        margin-bottom: 16px;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.82rem;
        color: #059669;
        font-weight: 700;
        background: #ecfdf5;
        border: 1px solid rgba(5, 150, 105, 0.25);
        padding: 4px 14px;
        border-radius: 20px;
        box-shadow: 0 2px 8px rgba(5, 150, 105, 0.12);
    }
    </style>
    """, unsafe_allow_html=True)


def _render_hit_predictor_tab(ml_service: MLService):
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; background: rgba(255,255,255,0.75); padding: 12px 20px; border-radius: 14px; border: 1px solid rgba(226,232,240,0.85); box-shadow: 0 2px 8px -2px rgba(0,0,0,0.03);">
        <div style="font-size: 0.96rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">
            <span>🎯</span> <span>Song Hit Prediction & Acoustic Recommendations</span>
        </div>
        <div class="status-pill">
            <span style="font-size: 8px;">🟢</span> <span>Models Cached in Memory (Instant Inference)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Song Recommendations & Hit Potential Predictions
    source_song, recs = render_recommendations()
    if source_song and recs:
        st.markdown("---")
        c_title, c_sel = st.columns([3, 2])
        with c_title:
            st.markdown(f"##### 🎯 Hit Potential Comparison for **{source_song['title']}** & Recommendations")
            st.caption("Commercial hit probability evaluated for source song and acoustic matches:")
        with c_sel:
            model_choice = st.selectbox(
                "Prediction Model",
                ["Gradient Boosting", "Random Forest", "Logistic Regression"],
                key="rec_hit_model_choice",
            )

        tracks = [{"label": f"Source · {source_song['title']}", "track": source_song}]
        tracks.extend(
            {"label": f"Recommended · {r['title']}", "track": r}
            for r in recs
        )
        rows = []
        for item in tracks:
            track_feats = {
                feat: item["track"].get(feat)
                for feat in MLService.FEATURE_COLS
                if item["track"].get(feat) is not None
            }
            res = ml_service.predict_hit_probability(track_feats, model_name=model_choice)
            rows.append({
                "Track": item["label"],
                "Artist": item["track"].get("artist_name", "Unknown"),
                "Hit Probability": f"{res['hit_probability']:.1f}%",
                "Verdict": res["verdict"],
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def _render_artist_classifier_tab(classifier_service: ArtistClassifierService):
    mic_html = get_svg_icon_html("mic", 26)
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; background: rgba(255,255,255,0.78); backdrop-filter: blur(16px); padding: 14px 22px; border-radius: 16px; border: 1px solid rgba(226,232,240,0.85); box-shadow: 0 4px 18px -4px rgba(99,102,241,0.06);">
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, rgba(139,92,246,0.14) 0%, rgba(236,72,153,0.14) 100%); display: flex; align-items: center; justify-content: center; border: 1px solid rgba(139,92,246,0.22); box-shadow: 0 2px 8px rgba(139,92,246,0.12);">
                {mic_html}
            </div>
            <div>
                <div style="font-size: 1.1rem; font-weight: 800; color: #0f172a; font-family: 'Outfit', sans-serif; letter-spacing: -0.01em;">
                    Lyric & Verse Artist Classifier
                </div>
                <div style="font-size: 0.84rem; color: #64748b; margin-top: 1px;">
                    Evaluate lyrical phrasing against 20 global music artists using sequence classification
                </div>
            </div>
        </div>
        <div style="display: inline-flex; align-items: center; gap: 6px; font-size: 0.82rem; color: #4338ca; font-weight: 700; background: #eef2ff; border: 1px solid rgba(99,102,241,0.2); padding: 5px 14px; border-radius: 20px;">
            <span>🎤</span> <span>20 Artist Signatures</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    def _apply_preset():
        choice = st.session_state.get("hf_artist_preset_select")
        if choice and choice in PRESET_LYRICS:
            st.session_state["hf_artist_lyrics_input"] = PRESET_LYRICS[choice]["text"]

    def _set_quick_preset(p_key: str):
        st.session_state["hf_artist_preset_select"] = p_key
        if p_key in PRESET_LYRICS:
            st.session_state["hf_artist_lyrics_input"] = PRESET_LYRICS[p_key]["text"]

    def _clear_lyrics():
        st.session_state["hf_artist_lyrics_input"] = ""
        st.session_state["hf_artist_preset_select"] = "— Choose a sample lyric —"

    # Quick Demo Picks buttons
    st.markdown("<div style='font-size:0.83rem; font-weight:700; color:#475569; margin: 6px 0;'>⚡ Instant Demo Buttons:</div>", unsafe_allow_html=True)
    demo_cols = st.columns(6)
    quick_picks = [
        ("Taylor Swift", "Taylor Swift — Blank Space"),
        ("The Weeknd", "The Weeknd — Blinding Lights"),
        ("Drake", "Drake — God's Plan"),
        ("SZA", "SZA — Kill Bill"),
        ("Doja Cat", "Doja Cat — Paint The Town Red"),
        ("Nicki Minaj", "Nicki Minaj — Super Bass"),
    ]
    for col, (label, p_key) in zip(demo_cols, quick_picks):
        with col:
            st.button(
                f"🎵 {label}",
                key=f"quick_demo_{label}",
                on_click=_set_quick_preset,
                args=(p_key,),
                use_container_width=True,
            )

    col_preset, col_clear = st.columns([3, 1])
    with col_preset:
        preset_choice = st.selectbox(
            "📋 Quick Sample Lyrics Preset (Choose from 23 iconic artist tracks):",
            ["— Choose a sample lyric —"] + list(PRESET_LYRICS.keys()),
            key="hf_artist_preset_select",
            on_change=_apply_preset,
        )
    with col_clear:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        st.button(
            "🧹 Clear",
            key="btn_clear_lyrics",
            on_click=_clear_lyrics,
            use_container_width=True,
        )

    if "hf_artist_lyrics_input" not in st.session_state:
        st.session_state["hf_artist_lyrics_input"] = ""

    lyrics_input = st.text_area(
        "Enter song lyrics, song verse, or chorus:",
        value=st.session_state.get("hf_artist_lyrics_input", ""),
        height=130,
        placeholder="Paste lyrics snippet here to predict the artist signature...",
        key="hf_artist_lyrics_input",
    )

    classify_btn = st.button("🔍 Predict Artist Signature", type="primary", key="btn_classify_artist")

    if classify_btn or (preset_choice and preset_choice != "— Choose a sample lyric —"):
        if not lyrics_input.strip():
            st.warning("Please enter or select lyrics to classify.")
            return

        with st.spinner("Analyzing lyric semantics with sequence classification..."):
            try:
                result = classifier_service.predict_artist(lyrics_input, top_k=5)
            except Exception as exc:
                st.error(f"Inference error: {exc}")
                return

        top_artist = result["top_artist"]
        top_conf = result["top_confidence"]
        predictions = result["predictions"]

        col_card, col_chart = st.columns([2, 3])
        with col_card:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); border-radius: 18px; padding: 26px; color: white; box-shadow: 0 12px 28px -5px rgba(79,70,229,0.35); text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700; opacity: 0.85;">
                    Top Predicted Artist
                </div>
                <div style="font-size: 32px; font-weight: 800; margin: 12px 0 6px 0; letter-spacing: -0.01em;">
                    {top_artist}
                </div>
                <div style="display: inline-block; background: rgba(255,255,255,0.22); padding: 6px 18px; border-radius: 30px; font-size: 15px; font-weight: 700; backdrop-filter: blur(8px); margin: 6px auto 0 auto;">
                    {top_conf:.1f}% Confidence Score
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_chart:
            df_chart = pd.DataFrame(predictions)
            fig = px.bar(
                df_chart,
                x="percentage",
                y="artist",
                orientation="h",
                color="percentage",
                color_continuous_scale="Purples",
                title="Top Matching Artists Probability Distribution",
                text="percentage",
            )
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(
                paper_bgcolor="rgba(255, 255, 255, 0.5)",
                plot_bgcolor="rgba(248, 250, 252, 0.6)",
                font=dict(family="Plus Jakarta Sans, sans-serif", color="#1e293b"),
                yaxis=dict(autorange="reversed", title=""),
                xaxis=dict(title="Probability (%)", range=[0, max(top_conf * 1.25, 30)]),
                margin=dict(l=10, r=30, t=40, b=20),
                coloraxis_showscale=False,
                height=260,
            )
            st.plotly_chart(fig, use_container_width=True)


def _render_musicgen_tab(music_service: MusicGenerationService):
    mg_html = get_svg_icon_html("musicgen", 26)
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; background: rgba(255,255,255,0.78); backdrop-filter: blur(16px); padding: 14px 22px; border-radius: 16px; border: 1px solid rgba(226,232,240,0.85); box-shadow: 0 4px 18px -4px rgba(219,39,119,0.06);">
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, rgba(236,72,153,0.14) 0%, rgba(6,182,212,0.14) 100%); display: flex; align-items: center; justify-content: center; border: 1px solid rgba(236,72,153,0.22); box-shadow: 0 2px 8px rgba(236,72,153,0.12);">
                {mg_html}
            </div>
            <div>
                <div style="font-size: 1.1rem; font-weight: 800; color: #0f172a; font-family: 'Outfit', sans-serif; letter-spacing: -0.01em;">
                    Meta AI MusicGen Studio
                </div>
                <div style="font-size: 0.84rem; color: #64748b; margin-top: 1px;">
                    Conditional audio synthesis conditioned on natural language prompts, harmonic progressions, and rhythm
                </div>
            </div>
        </div>
        <div style="display: inline-flex; align-items: center; gap: 6px; font-size: 0.82rem; color: #db2777; font-weight: 700; background: #fdf2f8; border: 1px solid rgba(219,39,119,0.2); padding: 5px 14px; border-radius: 20px;">
            <span>⚡</span> <span>Neural Audio Engine</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Style presets
    st.markdown("##### 🎨 Style & Mood Presets")
    preset_cols = st.columns(len(GENRE_PRESETS))
    selected_preset_key = st.session_state.get("musicgen_selected_preset", "🌆 80s Retro Synthwave")

    for col, (preset_name, p_data) in zip(preset_cols, GENRE_PRESETS.items()):
        with col:
            is_active = (selected_preset_key == preset_name)
            btn_type = "primary" if is_active else "secondary"
            if st.button(preset_name, key=f"mg_preset_{preset_name}", type=btn_type):
                st.session_state.musicgen_selected_preset = preset_name
                st.session_state.musicgen_prompt_text = p_data["prompt"]
                st.session_state.musicgen_bpm = p_data["bpm"]
                st.rerun()

    active_preset = GENRE_PRESETS.get(
        st.session_state.get("musicgen_selected_preset", "🌆 80s Retro Synthwave"),
        GENRE_PRESETS["🌆 80s Retro Synthwave"]
    )

    prompt_default = st.session_state.get("musicgen_prompt_text", active_preset["prompt"])
    music_prompt = st.text_input(
        "Enter Musical Prompt / Style Description:",
        value=prompt_default,
        placeholder="e.g. 80s retro synthwave with pulsing analog bassline and warm pads...",
        key="musicgen_user_prompt",
    )

    col_dur, col_bpm, col_key = st.columns(3)
    with col_dur:
        duration = st.slider("Duration (seconds)", 4, 20, 8, step=1, key="musicgen_dur")
    with col_bpm:
        bpm = st.slider("Tempo (BPM)", 60, 160, int(st.session_state.get("musicgen_bpm", active_preset["bpm"])), step=1, key="musicgen_bpm_slider")
    with col_key:
        st.text_input("Musical Scale / Key", value=active_preset.get("key", "A minor"), disabled=True)

    gen_btn = st.button("✨ Generate Track with MusicGen", type="primary", key="btn_generate_music")

    if gen_btn:
        with st.spinner(f"Generating music matching prompt: '{music_prompt}'..."):
            audio_result = music_service.synthesize_harmonic_music(
                prompt=music_prompt,
                duration=duration,
                bpm=bpm,
                preset_name=st.session_state.get("musicgen_selected_preset"),
            )
            st.session_state.latest_generated_audio = audio_result

    if "latest_generated_audio" in st.session_state:
        audio = st.session_state.latest_generated_audio
        st.markdown("---")
        st.subheader("🎧 Generated Audio Output")

        col_player, col_dl = st.columns([3, 1])
        with col_player:
            st.audio(audio["audio_bytes"], format="audio/wav")
        with col_dl:
            st.download_button(
                label="📥 Download Track (.wav)",
                data=audio["audio_bytes"],
                file_name=f"musicgen_{audio['bpm']}bpm.wav",
                mime="audio/wav",
                type="secondary",
                use_container_width=True,
            )

        st.caption(f"Engine: {audio['engine']} · Sample Rate: {audio['sample_rate']:,} Hz · Duration: {audio['duration']}s · Key: {audio['key']} @ {audio['bpm']} BPM")

        # Waveform visualizer
        st.markdown("##### 🌊 Waveform Dynamics")
        fig_wave = go.Figure()
        fig_wave.add_trace(go.Scatter(
            y=audio["waveform"],
            mode="lines",
            line=dict(color="#db2777", width=1.5),
            name="Amplitude",
        ))
        fig_wave.update_layout(get_glass_plotly_layout("Acoustic Waveform Analysis"))
        fig_wave.update_layout(
            yaxis=dict(title="Normalized Amplitude", range=[-1.0, 1.0]),
            xaxis=dict(title="Time Progression", showticklabels=False),
            height=200,
            margin=dict(l=10, r=10, t=30, b=10),
        )
        st.plotly_chart(fig_wave, use_container_width=True)


def render_song_prediction_generation():
    """Main entry point for Merged Tab 7."""
    render_hero_banner(
        "studio",
        "Song Prediction & Generation Studio",
        "Hugging Face Artist Prediction (tjl223) · Meta AI MusicGen Studio",
    )

    _inject_subtab_styles()

    if "artist_classifier_service" not in st.session_state:
        st.session_state.artist_classifier_service = ArtistClassifierService()
    if "music_generation_service" not in st.session_state:
        st.session_state.music_generation_service = MusicGenerationService()

    tab_artist, tab_musicgen = st.tabs([
        "🎤 1. Song Artist Classifier",
        "🎼 2. Meta AI MusicGen (Song Generation)",
    ])

    with tab_artist:
        _render_artist_classifier_tab(st.session_state.artist_classifier_service)

    with tab_musicgen:
        _render_musicgen_tab(st.session_state.music_generation_service)
