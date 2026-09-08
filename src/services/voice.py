"""
Voice and Speech Synthesis Service for Sangeet.
Generates natural, smooth speech synthesis components with markdown sanitization,
sentence chunking to eliminate browser dropouts, and natural neural voice selection.
"""

import html
import json
import re
import uuid
from typing import Optional
import streamlit.components.v1 as components


def clean_text_for_speech(text: str) -> str:
    """Sanitizes raw markdown/HTML into natural spoken English with zero syntax artifacts."""
    if not text:
        return ""
    # Remove code blocks
    s = re.sub(r"```[\s\S]*?```", "", text)
    # Remove inline code
    s = re.sub(r"`([^`]+)`", r"\1", s)
    # Remove markdown links [text](url) -> text
    s = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", s)
    # Remove images
    s = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", s)
    # Remove headers (### Title -> Title)
    s = re.sub(r"#+\s*", "", s)
    # Remove bold/italic (* or _)
    s = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", s)
    # Remove HTML tags
    s = re.sub(r"<[^>]+>", " ", s)
    # Remove emojis and special symbols
    s = re.sub(r"[🎵🎶🎤🎧✨🔥🚀📍🏙️👤🤖🎼🌊☕🎸🔊🗣️❤️🤍★☀-➿\U0001f300-\U0001f9ff]", "", s)
    # Clean bullet points and dashes
    s = re.sub(r"^\s*[-*•]\s*", "", s, flags=re.MULTILINE)
    # Clean multiple spaces and newlines
    s = re.sub(r"\s+", " ", s).strip()
    return s


class VoiceService:
    @staticmethod
    def generate_speech_html(text_to_speak: str, auto_play: bool = False, button_label: str = "Read Out Loud") -> str:
        """
        Generates a smooth, natural HTML5 Web Speech API audio player.
        Features:
        - Natural sentence chunking (prevents Chrome 15-second cutoff bug)
        - Priority natural neural voice selection
        - Clean smooth playback with Play / Stop toggle and active speech ripple indicator.
        """
        clean_text = clean_text_for_speech(text_to_speak)
        text_literal = json.dumps(clean_text, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        label_value = str(button_label or "Read Out Loud").strip()
        if label_value.startswith("🔊"):
            label_value = label_value.replace("🔊", "", 1).strip()
        escaped_label = html.escape(label_value, quote=True)
        label_literal = json.dumps(label_value, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        unique_id = uuid.uuid4().hex[:8]
        auto_run_script = f"setTimeout(function() {{ if (window.speakText_{unique_id}) window.speakText_{unique_id}(); }}, 400);" if auto_play else ""

        html_code = f"""
        <div class="voice-announcer-wrap" id="wrap_{unique_id}" style="margin: 6px 0; display: inline-flex; align-items: center; gap: 12px; font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;">
            <button onclick="window.toggleSpeech_{unique_id}()"
                    id="tts_btn_{unique_id}"
                    class="voice-tts-btn"
                    style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                           color: #ffffff;
                           border: 1px solid rgba(255, 255, 255, 0.3);
                           padding: 8px 18px;
                           border-radius: 24px;
                           font-weight: 700;
                           font-size: 13px;
                           cursor: pointer;
                           display: inline-flex;
                           align-items: center;
                           gap: 8px;
                           box-shadow: 0 4px 14px rgba(79, 70, 229, 0.28);
                           transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);">
                <span id="tts_icon_{unique_id}">🔊</span>
                <span id="tts_label_{unique_id}">{escaped_label}</span>
            </button>
            <span id="tts_status_{unique_id}" style="font-size: 12px; color: #4338ca; font-weight: 600; display: flex; align-items: center; gap: 6px;"></span>

            <script>
            (function() {{
                const rawText = {text_literal};
                let isSpeaking = false;
                let currentUtteranceIndex = 0;
                let sentences = [];

                function splitIntoSentences(text) {{
                    if (!text) return [];
                    const matches = text.match(/[^.!?]+[.!?]+|[^.!?]+$/g);
                    return matches ? matches.map(s => s.trim()).filter(s => s.length > 0) : [text];
                }}

                function getBestVoice() {{
                    const voices = window.speechSynthesis.getVoices();
                    if (!voices || voices.length === 0) return null;

                    // Priority 1: Indian English Natural Neural voices
                    const inNatural = voices.find(v => (v.lang === 'en-IN' || v.lang.startsWith('en_IN')) && (v.name.includes('Natural') || v.name.includes('Neural') || v.name.includes('Neerja') || v.name.includes('Prabhat')));
                    if (inNatural) return inNatural;

                    // Priority 2: Indian English general voices
                    const inVoice = voices.find(v => v.lang === 'en-IN' || v.lang.startsWith('en_IN') || v.name.includes('India'));
                    if (inVoice) return inVoice;

                    // Priority 3: Global Natural/Neural English voices
                    const naturalVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Online (Natural)') || v.name.includes('Google UK English Female') || v.name.includes('Google US English') || v.name.includes('Samantha') || v.name.includes('Karen')));
                    if (naturalVoice) return naturalVoice;

                    // Priority 4: Any English voice
                    const enVoice = voices.find(v => v.lang.startsWith('en'));
                    return enVoice || voices[0];
                }}

                function speakSentence(index) {{
                    if (index >= sentences.length || !isSpeaking) {{
                        stopSpeech();
                        return;
                    }}
                    currentUtteranceIndex = index;
                    const sentence = sentences[index];
                    const utterance = new SpeechSynthesisUtterance(sentence);
                    utterance.rate = 1.0;
                    utterance.pitch = 1.0;
                    utterance.volume = 1.0;
                    utterance.lang = 'en-IN';

                    const bestVoice = getBestVoice();
                    if (bestVoice) utterance.voice = bestVoice;

                    utterance.onend = function() {{
                        if (isSpeaking) {{
                            speakSentence(index + 1);
                        }}
                    }};

                    utterance.onerror = function(err) {{
                        console.warn("Speech error:", err);
                        stopSpeech();
                    }};

                    window.speechSynthesis.speak(utterance);
                }}

                function stopSpeech() {{
                    isSpeaking = false;
                    try {{ window.speechSynthesis.cancel(); }} catch(e) {{}}
                    const btn = document.getElementById("tts_btn_{unique_id}");
                    const label = document.getElementById("tts_label_{unique_id}");
                    const icon = document.getElementById("tts_icon_{unique_id}");
                    const status = document.getElementById("tts_status_{unique_id}");
                    if (btn) {{
                        btn.style.background = "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)";
                        btn.style.boxShadow = "0 4px 14px rgba(79, 70, 229, 0.28)";
                    }}
                    if (label) label.innerText = {label_literal};
                    if (icon) icon.innerText = "🔊";
                    if (status) status.innerHTML = "";
                }}

                window.speakText_{unique_id} = function() {{
                    if (!('speechSynthesis' in window)) {{
                        alert("Your browser does not support voice speech synthesis.");
                        return;
                    }}
                    try {{
                        window.speechSynthesis.cancel();
                        window.speechSynthesis.resume();
                    }} catch(e) {{}}

                    sentences = splitIntoSentences(rawText);
                    if (sentences.length === 0) return;

                    isSpeaking = true;
                    const btn = document.getElementById("tts_btn_{unique_id}");
                    const label = document.getElementById("tts_label_{unique_id}");
                    const icon = document.getElementById("tts_icon_{unique_id}");
                    const status = document.getElementById("tts_status_{unique_id}");

                    if (btn) {{
                        btn.style.background = "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)";
                        btn.style.boxShadow = "0 4px 14px rgba(239, 68, 68, 0.35)";
                    }}
                    if (label) label.innerText = "Stop Reading";
                    if (icon) icon.innerText = "⏹️";
                    if (status) {{
                        status.innerHTML = '<span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#22c55e; animation: pulse 1s infinite;"></span> Speaking...';
                    }}

                    // Load voices if not already available
                    if (window.speechSynthesis.getVoices().length === 0) {{
                        window.speechSynthesis.onvoiceschanged = function() {{
                            speakSentence(0);
                        }};
                    }} else {{
                        speakSentence(0);
                    }}
                }};

                window.toggleSpeech_{unique_id} = function() {{
                    if (isSpeaking) {{
                        stopSpeech();
                    }} else {{
                        window.speakText_{unique_id}();
                    }}
                }};

                {auto_run_script}
            }})();
            </script>
        </div>
        """
        return html_code

    @staticmethod
    def render_speech_widget(text_to_speak: str, auto_play: bool = False, button_label: str = "Read Out Loud"):
        """Renders the smooth browser speech synthesis widget in a Streamlit component."""
        html_content = VoiceService.generate_speech_html(text_to_speak, auto_play=auto_play, button_label=button_label)
        components.html(html_content, height=52, scrolling=False)

    @staticmethod
    def format_search_summary(count: int, query: str = "", top_track: str = "", artist: str = "") -> str:
        """Formats concise, spoken search count summaries matching user requirements."""
        if count == 0:
            return f"No records found for '{query}'." if query else "No records found."

        record_word = "record" if count == 1 else "records"
        if query:
            if top_track and artist:
                return f"Found {count:,} {record_word} matching '{query}'. Top result is {top_track} by {artist}."
            return f"Found {count:,} {record_word} matching '{query}'."
        else:
            if top_track and artist:
                return f"Found {count:,} {record_word}. Top result is {top_track} by {artist}."
            return f"Found {count:,} {record_word}."

    @staticmethod
    def format_recommendation_summary(source_title: str, top_match_title: str, top_artist: str, score: float) -> str:
        return f"Based on {source_title}, your top recommended track is {top_match_title} by {top_artist}, with a {score} percent acoustic match."

