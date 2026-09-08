"""
Machine Learning Laboratory view module for Sangeet.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.services.ml import MLService
from src.utils.theme import render_hero_banner

def render_ml_lab(show_hero: bool = True):
    if show_hero:
        render_hero_banner(
            "flask",
            "Machine Learning Laboratory",
            "Empirical model training on acoustic features for Hit Song Classification and real-time inference."
        )

    if "ml_service" not in st.session_state:
        st.session_state.ml_service = MLService()

    ml_service = st.session_state.ml_service

    st.subheader("1. Model Configuration & Training")

    c_split, c_seed, c_action = st.columns([2, 2, 2])
    with c_split:
        test_split = st.slider("Test Split Size", 0.15, 0.40, 0.25, step=0.05, key="ml_test_split")
    with c_seed:
        seed = st.number_input("Random Seed (Reproducibility)", value=42, step=1, key="ml_seed")
    with c_action:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        train_clicked = st.button("🚀 Train All Models", key="ml_train_btn")

    if train_clicked:
        try:
            with st.spinner("Training Logistic Regression, Random Forest, and Gradient Boosting..."):
                results = ml_service.train_models(test_size=test_split, random_state=int(seed))
                st.session_state.ml_results = results
        except ValueError as exc:
            st.error(str(exc))
            return

    if "ml_results" not in st.session_state:
        st.info("💡 Adjust training parameters above and click **🚀 Train All Models** to run empirical evaluations.")
        return

    results = st.session_state.ml_results

    st.markdown("---")
    st.subheader("2. Model Evaluation & Comparison")

    metrics_list = []
    for m_name, m_metrics in results["models"].items():
        metrics_list.append({
            "Model": m_name,
            "Accuracy (%)": f"{m_metrics['accuracy']*100:.2f}%",
            "Precision (%)": f"{m_metrics['precision']*100:.2f}%",
            "Recall (%)": f"{m_metrics['recall']*100:.2f}%",
            "F1 Score": f"{m_metrics['f1']:.3f}",
            "ROC-AUC": f"{m_metrics['roc_auc']:.3f}"
        })

    st.dataframe(pd.DataFrame(metrics_list), hide_index=True)
    st.caption(f"Dataset Size: {results['train_size']:,} Train / {results['test_size']:,} Test samples. Hit threshold: popularity ≥ {results['hit_threshold']}. Base Hit Proportion: {results['hit_ratio']*100:.1f}%.")

    col_feat, col_cm = st.columns([1, 1])

    with col_feat:
        st.subheader("Feature Importance (Random Forest)")
        imp_dict = results["feature_importances"]
        df_imp = pd.DataFrame(list(imp_dict.items()), columns=["Acoustic Feature", "Importance"])
        
        fig_imp = px.bar(
            df_imp,
            x="Importance",
            y="Acoustic Feature",
            orientation="h",
            color="Importance",
            color_continuous_scale="Purples",
            template="plotly_white"
        )
        fig_imp.update_layout(
            paper_bgcolor="rgba(255, 255, 255, 0.5)",
            plot_bgcolor="rgba(248, 250, 252, 0.6)",
            font=dict(family="Plus Jakarta Sans, sans-serif", color="#1e293b"),
            yaxis=dict(autorange="reversed"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_imp)

    with col_cm:
        st.subheader("Confusion Matrix (Gradient Boosting)")
        gb_cm = results["models"]["Gradient Boosting"]["confusion_matrix"]
        cm_df = pd.DataFrame(
            gb_cm,
            index=["Actual Non-Hit", "Actual Hit"],
            columns=["Pred Non-Hit", "Pred Hit"]
        )
        fig_cm = px.imshow(
            cm_df,
            text_auto=True,
            color_continuous_scale="Blues",
            template="plotly_white"
        )
        fig_cm.update_layout(
            paper_bgcolor="rgba(255, 255, 255, 0.5)",
            plot_bgcolor="rgba(248, 250, 252, 0.6)",
            font=dict(family="Plus Jakarta Sans, sans-serif", color="#1e293b"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_cm)

    st.markdown("---")
    st.subheader("3. Live Track Hit Predictor")
    st.write("Simulate audio characteristics to score track commercial potential:")

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        in_dance = st.slider("Danceability", 0.0, 1.0, 0.72, key="ml_dance")
        in_energy = st.slider("Energy", 0.0, 1.0, 0.81, key="ml_energy")
        in_loud = st.slider("Loudness (dB)", -30.0, 0.0, -5.5, key="ml_loud")

    with col_s2:
        in_speech = st.slider("Speechiness", 0.0, 0.8, 0.08, key="ml_speech")
        in_acoustic = st.slider("Acousticness", 0.0, 1.0, 0.25, key="ml_acoustic")
        in_instrumental = st.slider("Instrumentalness", 0.0, 1.0, 0.01, key="ml_instr")

    with col_s3:
        in_live = st.slider("Liveness", 0.0, 1.0, 0.15, key="ml_live")
        in_valence = st.slider("Valence (Happiness)", 0.0, 1.0, 0.65, key="ml_valence")
        in_tempo = st.slider("Tempo (BPM)", 60.0, 200.0, 124.0, key="ml_tempo")

    model_choice = st.selectbox("Predictor Model", ["Gradient Boosting", "Random Forest", "Logistic Regression"], key="ml_model_choice")

    features_input = {
        "danceability": in_dance, "energy": in_energy, "loudness": in_loud,
        "speechiness": in_speech, "acousticness": in_acoustic, "instrumentalness": in_instrumental,
        "liveness": in_live, "valence": in_valence, "tempo": in_tempo
    }

    pred = ml_service.predict_hit_probability(features_input, model_name=model_choice)

    st.markdown(f"""
    <div class="song-card" style="margin-top: 14px;">
        <div>
            <div style="font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Inference Result ({pred['model_used']})</div>
            <div style="font-size: 22px; font-weight: 800; color: #0f172a; margin-top: 4px;">{pred['verdict']}</div>
        </div>
        <div style="text-align: right;">
            <span class="badge badge-hit" style="font-size: 16px; padding: 6px 14px; font-weight: 700;">{pred['hit_probability']}% Hit Probability</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(pred["hit_probability"] / 100)
