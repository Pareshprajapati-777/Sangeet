"""
Deep Learning Laboratory view module for Sangeet.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.utils.theme import get_glass_plotly_layout, render_hero_banner
from src.services.dl import DLService

def render_dl_lab(show_hero: bool = True):
    if show_hero:
        render_hero_banner(
            "brain",
            "Deep Learning Laboratory (PyTorch)",
            "Interactive neural network training with Batch Normalization, Dropout regularization, and real-time loss dynamics."
        )

    if "dl_service" not in st.session_state:
        st.session_state.dl_service = DLService()

    dl_service = st.session_state.dl_service

    st.subheader("1. Neural Network Hyperparameters")

    c_ep, c_lr, c_hid, c_drop = st.columns(4)
    with c_ep:
        epochs = st.slider("Training Epochs", 10, 60, 30, step=5, key="dl_epochs")
    with c_lr:
        lr = st.select_slider("Learning Rate", options=[0.001, 0.003, 0.005, 0.01], value=0.005, key="dl_lr")
    with c_hid:
        hidden_units = st.selectbox("Hidden Layer Units", [32, 64, 128], index=1, key="dl_hidden")
    with c_drop:
        dropout = st.slider("Dropout Rate", 0.1, 0.5, 0.25, step=0.05, key="dl_dropout")

    if st.button("⚡ Train Neural Network", type="primary", key="dl_train_btn"):
        try:
            with st.spinner("Executing PyTorch training loop on CPU..."):
                dl_results = dl_service.train_neural_network(
                    epochs=epochs,
                    learning_rate=lr,
                    hidden_dim=hidden_units,
                    dropout_rate=dropout
                )
                st.session_state.dl_results = dl_results
        except ValueError as exc:
            st.error(str(exc))

    if "dl_results" in st.session_state:
        dl_results = st.session_state.dl_results
        history = dl_results["history"]
        df_hist = pd.DataFrame(history)

        st.markdown("---")
        st.subheader("2. Model Architecture & Convergence Telemetry")

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Validation Accuracy", f"{dl_results['final_val_acc']:.2f}%")
        col_m2.metric("Validation Loss (BCE)", f"{dl_results['final_val_loss']:.4f}")
        col_m3.metric("Trainable Parameters", f"{dl_results['total_params']:,}")
        st.caption(f"Hit threshold: popularity ≥ {dl_results['hit_threshold']} · Training epochs completed: {dl_results['epochs_run']}")

        c_loss, c_acc = st.columns(2)

        with c_loss:
            fig_loss = go.Figure()
            fig_loss.add_trace(go.Scatter(x=df_hist["epoch"], y=df_hist["train_loss"], name="Train Loss", line=dict(color="#4f46e5", width=2.5)))
            fig_loss.add_trace(go.Scatter(x=df_hist["epoch"], y=df_hist["val_loss"], name="Val Loss", line=dict(color="#db2777", width=2.5, dash="dash")))
            fig_loss.update_layout(get_glass_plotly_layout("Binary Cross-Entropy Loss Curve"))
            fig_loss.update_layout(xaxis_title="Epoch", yaxis_title="Loss")
            st.plotly_chart(fig_loss)

        with c_acc:
            fig_acc = go.Figure()
            fig_acc.add_trace(go.Scatter(x=df_hist["epoch"], y=df_hist["train_acc"], name="Train Accuracy", line=dict(color="#059669", width=2.5)))
            fig_acc.add_trace(go.Scatter(x=df_hist["epoch"], y=df_hist["val_acc"], name="Val Accuracy", line=dict(color="#d97706", width=2.5, dash="dash")))
            fig_acc.update_layout(get_glass_plotly_layout("Accuracy Dynamics (%)"))
            fig_acc.update_layout(xaxis_title="Epoch", yaxis_title="Accuracy (%)")
            st.plotly_chart(fig_acc)

        st.markdown("""
        #### 💡 Deep Learning Insights
        - **BatchNorm1d Layers:** Normalize mini-batch internal covariate shift, ensuring stable gradients across all epochs.
        - **Dropout Regularization:** Prevents over-relying on individual acoustic features like high danceability alone.
        - **Tabular DL vs Classical ML:** While neural networks effectively model nonlinear feature interactions, classical ensemble models (Random Forest, Gradient Boosting) often perform competitively on structured tabular metadata with faster inference.
        """)
    else:
        st.info("Click 'Train Neural Network' to launch the PyTorch model training.")
