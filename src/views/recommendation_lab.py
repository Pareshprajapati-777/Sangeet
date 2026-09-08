"""Merged recommendation and machine-learning module."""

import pandas as pd
import streamlit as st

from src.services.ml import MLService
from src.views.ml_lab import render_ml_lab
from src.views.recommendations import render_recommendations


def _feature_values(track):
    return {
        feature: track.get(feature)
        for feature in MLService.FEATURE_COLS
        if track.get(feature) is not None
    }


def _render_quick_hit_predictions(source_song, recommendations):
    with st.expander("Quick ML hit prediction for this recommendation set", expanded=False):
        st.caption("Train once, then compare the source and recommended tracks without leaving this tab.")
        if "ml_service" not in st.session_state:
            st.session_state.ml_service = MLService()
        service = st.session_state.ml_service
        if st.button("Train hit predictor", key="recommendation_train_ml"):
            try:
                with st.spinner("Training the hit predictor..."):
                    st.session_state.ml_results = service.train_models()
            except ValueError as exc:
                st.error(str(exc))

        if "ml_results" not in st.session_state:
            st.info("Click **Train hit predictor** to score these tracks.")
            return

        model_name = st.selectbox(
            "Prediction model",
            ["Gradient Boosting", "Random Forest", "Logistic Regression"],
            key="recommendation_ml_model",
        )
        tracks = [{"label": f"Source · {source_song['title']}", "track": source_song}]
        tracks.extend(
            {"label": f"Recommended · {recommendation['title']}", "track": recommendation}
            for recommendation in recommendations
        )
        rows = []
        for item in tracks:
            try:
                prediction = service.predict_hit_probability(
                    _feature_values(item["track"]),
                    model_name=model_name,
                )
                rows.append(
                    {
                        "Track": item["label"],
                        "Artist": item["track"].get("artist_name", "Unknown Artist"),
                        "Hit probability": f"{prediction['hit_probability']:.1f}%",
                        "Verdict": prediction["verdict"],
                    }
                )
            except ValueError as exc:
                st.error(str(exc))
                return
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def render_recommendation_lab():
    source_song, recommendations = render_recommendations()
    if source_song and recommendations:
        _render_quick_hit_predictions(source_song, recommendations)
    with st.expander("Machine Learning Lab", expanded=False):
        render_ml_lab(show_hero=False)
