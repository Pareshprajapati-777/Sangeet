"""
Master-Grade Audio Preview & Playback Engine for Sangeet.
Generates rich, multi-layered stereo acoustic instrumental previews (piano/guitar chords,
melodic bass, natural rhythm) synthesized directly from acoustic DNA,
plus native Streamlit audio controls and Spotify Web Player embeds.
"""

import io
import wave
import base64
import html
import re
from functools import lru_cache
from typing import Optional

import numpy as np
import streamlit as st


@lru_cache(maxsize=256)
def _build_master_preview_wav(
    tempo: float,
    energy: float,
    key: int,
    valence: float = 0.5,
    danceability: float = 0.5,
) -> bytes:
    """
    Synthesizes a rich stereo 16-bit PCM WAV audio track featuring:
    1. Multi-harmonic warm acoustic piano / guitar chord progressions (major/minor based on valence)
    2. Deep bassline with dynamic filter envelope
    3. Acoustic drums & groove percussion scaled by danceability & energy
    4. Smooth stereo panning and master normalization.
    """
    sample_rate = 32000
    duration_seconds = 8.5
    sample_count = int(sample_rate * duration_seconds)
    audio_l = np.zeros(sample_count, dtype=np.float64)
    audio_r = np.zeros(sample_count, dtype=np.float64)

    bpm = max(60.0, min(180.0, float(tempo or 120.0)))
    beat_dur = 60.0 / bpm
    bar_dur = beat_dur * 4.0

    # Key to root frequency (A3 = 220Hz base)
    root_f = 220.0 * (2.0 ** ((int(key or 0) % 12) / 12.0))
    if root_f > 360.0:
        root_f /= 2.0

    # Harmonic progression (Major for happy/high valence, soulful Minor for lower valence)
    if float(valence or 0.5) >= 0.5:
        # I - V - vi - IV Progression
        scale_steps = [[0, 4, 7], [7, 11, 14], [9, 12, 16], [5, 9, 12]]
    else:
        # i - VI - III - VII Soulful Minor Progression
        scale_steps = [[0, 3, 7], [8, 12, 15], [3, 7, 10], [10, 14, 17]]

    num_bars = int(np.ceil(duration_seconds / bar_dur))
    for b in range(num_bars):
        b_start = b * bar_dur
        chord = scale_steps[b % len(scale_steps)]
        chord_freqs = [root_f * (2.0 ** (s / 12.0)) for s in chord]

        # 1. Warm Piano / Acoustic Chords on beats
        for beat in range(4):
            beat_time = b_start + beat * beat_dur
            if beat_time >= duration_seconds:
                break
            s_idx = int(beat_time * sample_rate)
            e_idx = min(sample_count, int((beat_time + beat_dur * 1.75) * sample_rate))
            ch_len = e_idx - s_idx
            if ch_len <= 0:
                continue
            local_t = np.linspace(0, ch_len / sample_rate, ch_len, endpoint=False)
            env = np.exp(-3.2 * local_t / (beat_dur * 1.4))

            for i_nf, nf in enumerate(chord_freqs):
                tone = (
                    np.sin(2 * np.pi * nf * local_t)
                    + 0.40 * np.sin(4 * np.pi * nf * local_t)
                    + 0.18 * np.sin(6 * np.pi * nf * local_t)
                    + 0.08 * np.sin(8 * np.pi * nf * local_t)
                )
                pan_l = 0.45 + 0.15 * (i_nf % 2)
                pan_r = 0.45 + 0.15 * ((i_nf + 1) % 2)
                audio_l[s_idx:e_idx] += tone * env * (0.13 * float(energy or 0.6)) * pan_l
                audio_r[s_idx:e_idx] += tone * env * (0.13 * float(energy or 0.6)) * pan_r

        # 2. Resonant Bassline (Sub-bass octave below)
        bass_freq = chord_freqs[0] / 2.0
        for b_step in range(2):
            bass_time = b_start + b_step * (bar_dur / 2.0)
            if bass_time >= duration_seconds:
                break
            s_idx = int(bass_time * sample_rate)
            e_idx = min(sample_count, int((bass_time + bar_dur / 2.0) * sample_rate))
            ch_len = e_idx - s_idx
            if ch_len <= 0:
                continue
            local_t = np.linspace(0, ch_len / sample_rate, ch_len, endpoint=False)
            b_env = np.exp(-2.2 * local_t / (bar_dur / 2.0))
            bass_tone = np.sin(2 * np.pi * bass_freq * local_t) + 0.32 * np.sin(4 * np.pi * bass_freq * local_t)
            audio_l[s_idx:e_idx] += bass_tone * b_env * (0.22 * float(energy or 0.6))
            audio_r[s_idx:e_idx] += bass_tone * b_env * (0.22 * float(energy or 0.6))

    # 3. Drums / Percussion (Kick, Snare, Hi-hat)
    effective_dance = max(0.2, float(danceability or 0.5))
    total_beats = int(duration_seconds / beat_dur)
    for bt in range(total_beats):
        bt_time = bt * beat_dur
        # Kick on 1 and 3
        if bt % 2 == 0:
            k_len = min(int(0.22 * sample_rate), sample_count - int(bt_time * sample_rate))
            if k_len > 0:
                s_idx = int(bt_time * sample_rate)
                k_t = np.linspace(0, k_len / sample_rate, k_len, endpoint=False)
                k_f = 45.0 + 85.0 * np.exp(-22 * k_t)
                k_phase = 2 * np.pi * np.cumsum(k_f) / sample_rate
                k_env = np.exp(-12 * k_t)
                kick = np.sin(k_phase) * k_env * (0.34 * effective_dance)
                audio_l[s_idx:s_idx + k_len] += kick
                audio_r[s_idx:s_idx + k_len] += kick
        # Snare on 2 and 4
        else:
            sn_len = min(int(0.18 * sample_rate), sample_count - int(bt_time * sample_rate))
            if sn_len > 0:
                s_idx = int(bt_time * sample_rate)
                sn_t = np.linspace(0, sn_len / sample_rate, sn_len, endpoint=False)
                sn_noise = np.random.uniform(-1, 1, sn_len) * np.exp(-14 * sn_t) * (0.16 * effective_dance)
                sn_tone = np.sin(2 * np.pi * 175.0 * sn_t) * np.exp(-18 * sn_t) * (0.14 * effective_dance)
                audio_l[s_idx:s_idx + sn_len] += sn_noise + sn_tone
                audio_r[s_idx:s_idx + sn_len] += sn_noise + sn_tone

        # Hi-hat on 8th notes
        for sub in [0, 0.5]:
            hh_time = bt_time + sub * beat_dur
            hh_len = min(int(0.06 * sample_rate), sample_count - int(hh_time * sample_rate))
            if hh_len > 0:
                s_idx = int(hh_time * sample_rate)
                hh_t = np.linspace(0, hh_len / sample_rate, hh_len, endpoint=False)
                hh_noise = np.random.uniform(-1, 1, hh_len) * np.exp(-35 * hh_t) * (0.07 * float(energy or 0.5))
                audio_l[s_idx:s_idx + hh_len] += hh_noise * 0.7
                audio_r[s_idx:s_idx + hh_len] += hh_noise * 1.0

    # Fade in / Fade out
    fade_samples = int(sample_rate * 0.05)
    fade_in = np.linspace(0.0, 1.0, fade_samples)
    fade_out = np.linspace(1.0, 0.0, fade_samples)
    audio_l[:fade_samples] *= fade_in
    audio_r[:fade_samples] *= fade_in
    audio_l[-fade_samples:] *= fade_out
    audio_r[-fade_samples:] *= fade_out

    # Peak normalization
    max_val = max(np.max(np.abs(audio_l)), np.max(np.abs(audio_r)), 0.001)
    audio_l = audio_l / max_val * 0.86
    audio_r = audio_r / max_val * 0.86

    stereo = np.empty((sample_count, 2), dtype=np.int16)
    stereo[:, 0] = np.int16(np.clip(audio_l, -1.0, 1.0) * 32767)
    stereo[:, 1] = np.int16(np.clip(audio_r, -1.0, 1.0) * 32767)

    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(stereo.tobytes())
    return output.getvalue()


def _extract_spotify_id(song_id: str) -> Optional[str]:
    """Extracts raw Spotify track ID if song_id matches standard 22-char Spotify alphanumeric ID."""
    if not song_id:
        return None
    cleaned = str(song_id).strip()
    for prefix in ["srch_", "dash_", "pl_", "fav_", "rec_", "pred_artist_", "vision_", "recommendation_"]:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
    if len(cleaned) == 22 and re.match(r"^[0-9A-Za-z]{22}$", cleaned):
        return cleaned
    return None


def get_audio_player_html(
    song_id: str,
    title: str,
    artist: str,
    tempo: float = 120.0,
    energy: float = 0.5,
    key: int = 0,
    valence: float = 0.5,
    danceability: float = 0.5,
) -> str:
    """Retained for compatibility with callers that request HTML string."""
    audio_data = _build_master_preview_wav(
        round(max(60.0, min(180.0, float(tempo or 120.0))), 2),
        round(max(0.1, min(1.0, float(energy or 0.5))), 2),
        int(key or 0) % 12,
        round(max(0.0, min(1.0, float(valence or 0.5))), 2),
        round(max(0.0, min(1.0, float(danceability or 0.5))), 2),
    )
    encoded_audio = base64.b64encode(audio_data).decode("ascii")
    return f'<audio controls preload="none" src="data:audio/wav;base64,{encoded_audio}"></audio>'


def render_audio_preview_player(
    song_id: str,
    title: str,
    artist: str,
    tempo: float = 120.0,
    energy: float = 0.5,
    key: int = 0,
    valence: float = 0.5,
    danceability: float = 0.5,
    auto_render: bool = True,
):
    """
    Renders a master stereo audio player backed by high-fidelity acoustic synthesis.
    If a Spotify track ID is present, also offers instantaneous Spotify web preview!
    """
    tempo_value = round(max(60.0, min(180.0, float(tempo or 120.0))), 2)
    energy_value = round(max(0.1, min(1.0, float(energy or 0.5))), 2)
    key_value = int(key or 0) % 12
    valence_value = round(max(0.0, min(1.0, float(valence or 0.5))), 2)
    dance_value = round(max(0.0, min(1.0, float(danceability or 0.5))), 2)

    audio_data = _build_master_preview_wav(
        tempo_value,
        energy_value,
        key_value,
        valence_value,
        dance_value,
    )

    if auto_render:
        st.audio(audio_data, format="audio/wav")
        spotify_id = _extract_spotify_id(song_id)
        if spotify_id:
            st.caption(
                f"🎧 Master Preview · {title} — {artist} · {int(tempo_value)} BPM · [Open on Spotify](https://open.spotify.com/track/{spotify_id})"
            )
        else:
            st.caption(f"🎧 Master Preview · {title} — {artist} · {int(tempo_value)} BPM · Key {key_value}")
        return ""
    return audio_data

