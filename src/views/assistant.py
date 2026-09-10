"""
AI Assistant view module for Sangeet (Tab 9).
Grounded RAG conversational musicologist with natural neural voice synthesis.
"""

import streamlit as st
from src.utils.theme import render_hero_banner
from src.services.assistant import AssistantService
from src.services.voice import VoiceService

def render_assistant():
    render_hero_banner(
        "robot",
        "Sangeet AI Assistant",
        "Conversational musicologist grounded in the local Sangeet database with smooth natural neural voice readout."
    )

    if "assistant_service" not in st.session_state:
        st.session_state.assistant_service = AssistantService()

    assistant_service = st.session_state.assistant_service

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "Namaste! I am Sangeet AI, your personal music intelligence assistant grounded across our 114K catalog (89,752 songs, 17,637 Indian & global artists, and 42+ studios/filming hubs). Ask me about artist discographies, audio DNA, filming locations, or platform capabilities!"
            }
        ]

    # Voice & Control Toolbar
    col_t_title, col_t_voice = st.columns([3, 1])
    with col_t_title:
        st.markdown("##### 💡 Suggested Inquiries (Click to Ask):")
    with col_t_voice:
        auto_speak_chat = st.checkbox("🔊 Auto-speak replies", value=False, key="chat_auto_speak_toggle")

    c_p1, c_p2, c_p3, c_p4 = st.columns(4)
    preset_query = None
    with c_p1:
        if st.button("🎤 Arijit Singh Catalog", key="ai_btn1", use_container_width=True):
            preset_query = "Tell me about Arijit Singh, his top songs, and audio profile in the Sangeet catalog."
    with c_p2:
        if st.button("🌍 Global: Taylor Swift", key="ai_btn2", use_container_width=True):
            preset_query = "Tell me about Taylor Swift and her top tracks in the catalog."
    with c_p3:
        if st.button("🏛️ Full Project Architecture", key="ai_btn3", use_container_width=True):
            preset_query = "Give me complete information about Sangeet platform, its 9 modules, ML models, and audio capabilities."
    with c_p4:
        if st.button("📍 Kun Faya Kun Filming", key="ai_btn4", use_container_width=True):
            preset_query = "Where was the song Kun Faya Kun filmed and what is its musical significance?"

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Render Chat Messages inside fixed-height scroll container to prevent input dislocation
    chat_container = st.container(height=520)
    with chat_container:
        for idx, msg in enumerate(st.session_state.chat_messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and len(msg["content"]) > 25:
                    VoiceService.render_speech_widget(
                        msg["content"],
                        auto_play=False,
                        button_label="Listen to AI Voice"
                    )

    user_input = st.chat_input("Ask Sangeet AI about songs, artists, audio features, or project architecture...", key="ai_chat_input")

    query_to_send = preset_query or user_input
    if query_to_send:
        st.session_state.chat_messages.append({"role": "user", "content": query_to_send})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(query_to_send)

            with st.chat_message("assistant"):
                with st.spinner("Consulting Sangeet RAG catalog and synthesizing response..."):
                    reply = assistant_service.chat(st.session_state.chat_messages)
                    st.markdown(reply)
                    VoiceService.render_speech_widget(
                        reply,
                        auto_play=auto_speak_chat,
                        button_label="Listen to AI Voice"
                    )
                    st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()

