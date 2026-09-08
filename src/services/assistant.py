"""
Grounded RAG Assistant Service for Sangeet.
Integrates a comprehensive project knowledge base, deep catalog entity retrieval
(Indian & International artists, tracks, audio DNA, filming locations/studios),
and structured conversational response synthesis with smooth speech output.
"""

import logging
import re
import sqlite3
from typing import Any, Dict, List, Optional
import requests

from src.config import OPENROUTER_API_KEY, OPENROUTER_MAX_TOKENS, OPENROUTER_MODEL, ROOT_DIR
from src.repositories.artists import ArtistRepository
from src.repositories.locations import LocationRepository
from src.repositories.songs import SongRepository
from src.services.analytics import AnalyticsService
from src.db import get_connection

logger = logging.getLogger("sangeet.assistant")

# Complete Project Architecture & Capability Knowledge Base
PROJECT_INFO = {
    "name": "Sangeet — Music Intelligence Platform",
    "version": "2.0 (Master Glass Edition)",
    "tagline": "AI-Powered Music Discovery, Acoustic Telemetry, and Artist Intelligence",
    "architecture": "Local-First Music Intelligence & Discovery Ecosystem backed by SQLite WAL mode, FTS5 full-text indexing, Scikit-Learn ML, PyTorch DL, Hugging Face Transformers, Meta AI MusicGen, and 128-D Facial Biometrics.",
    "dataset": "114K Spotify & Indian Music Catalog with 89,752 verified tracks, 17,637 artists, 57,644 albums, and 12-dimensional audio DNA features.",
    "modules": [
        "1. Dashboard: Real-time telemetry, KPI metrics, genre distributions, audio radar DNA, and top chartbusters with master preview audio.",
        "2. Analytics: Multi-dimensional vibe mapping (danceability vs energy), feature correlation heatmap, valence distribution, and release decade trajectories.",
        "3. Data Management: Full CRUD operations for adding, editing, or deleting catalog tracks with automatic FTS5 synchronization.",
        "4. Smart Search: Sub-millisecond FTS5 full-text search across songs, artists, albums, and genres with instant voice readout and CSV/JSON export.",
        "5. Artist & Filming Location Map: Interactive Folium geospatial map with 42+ verified studios, recording facilities, and iconic Bollywood/South Indian filming hubs.",
        "6. Artist Visual Intelligence: 128-D facial feature embeddings + ResNet18 deep visual matching to identify music artists from uploaded portraits with 1-click catalog linkage.",
        "7. Song Prediction & Generation Studio: Empirical commercial hit classifier (HistGradientBoosting / Random Forest), Hugging Face lyrics artist sequence classifier (tjl223), and Meta AI MusicGen conditional text-to-music audio synthesis.",
        "8. Playlists & Personalization: Curated collections, custom playlist creation, favorited tracks, and continuous loop playback.",
        "9. AI Assistant: Conversational musicologist grounded in the local RAG database with smooth Web Speech API voice announcements."
    ],
    "audio_features": {
        "danceability": "Measures suitability for dancing based on tempo, rhythm stability, beat strength, and overall regularity (0.0 to 1.0).",
        "energy": "Perceptual measure of intensity, activity, dynamic range, loudness, and timbre (0.0 to 1.0). Fast and loud tracks (like EDM/Rock) have high energy.",
        "valence": "Musical positiveness / happiness conveyed by a track (0.0 to 1.0). High valence sounds happy, cheerful, euphoric; low valence sounds sad, melancholic, or soulful.",
        "tempo": "Overall estimated pace of a track in Beats Per Minute (BPM).",
        "acousticness": "Confidence measure from 0.0 to 1.0 of whether the track is acoustic (unplugged, live acoustic instruments).",
        "instrumentalness": "Predicts whether a track contains no vocals. Rap or spoken word tracks have near 0.0, classical/ambient tracks have near 1.0.",
        "liveness": "Detects the presence of an audience in the recording (0.0 to 1.0). Values above 0.8 indicate strong likelihood of a live concert recording.",
        "speechiness": "Detects the presence of spoken words. Values above 0.66 are typically speech, audiobooks, or talk radio; 0.33-0.66 is rap; below 0.33 is music.",
        "loudness": "Overall loudness of a track in decibels (dB), averaged across the entire track (typically between -60 dB and 0 dB).",
        "key_mode": "Musical pitch class (0=C, 1=C#, 2=D...) and modality (1=Major scale / bright, 0=Minor scale / dark)."
    },
    "technologies": [
        "Database: SQLite 3 with Write-Ahead Logging (WAL), 64MB cache, 256MB memory mapping, and FTS5 full-text indexing.",
        "Machine Learning: HistGradientBoostingClassifier & RandomForestClassifier with 10-fold cross validation for commercial hit potential prediction.",
        "Deep Learning: PyTorch Feed-Forward Neural Network trained on multi-dimensional audio feature vectors.",
        "Transformers: Hugging Face DistilBERT Sequence Classification (tjl223/song-artist-classifier-v2) for lyric-to-artist attribution.",
        "Audio Generation: Meta AI MusicGen (facebook/musicgen-small) + high-speed procedural multi-harmonic stereo audio synthesis.",
        "Visual Intelligence: dlib 128-D facial feature embeddings + PyTorch ResNet18 visual embeddings.",
        "Voice: HTML5 Web Speech API with sentence chunking and priority Indian/Global natural neural voice selection."
    ]
}


class AssistantService:
    STOP_WORDS = {
        "a", "about", "after", "all", "an", "and", "are", "as", "at", "be", "by",
        "can", "could", "did", "do", "does", "for", "from", "get", "give", "has", "have",
        "how", "i", "in", "is", "it", "me", "my", "of", "on", "or", "please",
        "recommend", "show", "some", "song", "songs", "tell", "the", "their",
        "this", "to", "track", "tracks", "what", "where", "which", "who", "with", "you"
    }

    def __init__(self):
        self.song_repo = SongRepository()
        self.artist_repo = ArtistRepository()
        self.location_repo = LocationRepository()
        self.analytics_service = AnalyticsService()

    @classmethod
    def _search_phrases(cls, prompt: str) -> List[str]:
        tokens = [
            token
            for token in re.findall(r"[a-z0-9][a-z0-9'&.-]*", prompt.casefold())
            if token not in cls.STOP_WORDS and len(token) > 1
        ]
        phrases = []
        for phrase_size in (3, 2, 1):
            for index in range(len(tokens) - phrase_size + 1):
                phrase = " ".join(tokens[index : index + phrase_size])
                if phrase not in phrases:
                    phrases.append(phrase)
        return phrases

    def _get_grounded_context(self, user_prompt: str) -> Dict[str, Any]:
        """Retrieves comprehensive structured catalog facts and project knowledge matching the query."""
        prompt_lower = user_prompt.casefold()
        context = {
            "matched_artists": [],
            "matched_songs": [],
            "matched_locations": [],
            "project_matches": [],
            "kpis": self.analytics_service.get_overview_kpis(),
        }

        # 1. Project Platform Knowledge Matching
        if any(k in prompt_lower for k in ["project", "sangeet", "module", "platform", "model", "feature", "musicgen", "hit predictor", "how it work", "architecture", "system", "technology", "tech stack", "database", "sqlite", "fts5"]):
            context["project_matches"] = PROJECT_INFO["modules"]

        # 2. Artist Retrieval (Indian & Foreign/Global Artists)
        search_phrases = self._search_phrases(user_prompt)
        matched_artist_ids = set()

        conn = get_connection()
        cur = conn.cursor()

        # Direct search in artists table
        for phrase in search_phrases[:8]:
            cur.execute("""
                SELECT a.id, a.name, a.country, a.debut_year, a.bio,
                       COUNT(s.id) as total_songs,
                       ROUND(AVG(s.popularity), 1) as avg_pop,
                       ROUND(AVG(f.tempo), 1) as avg_tempo,
                       ROUND(AVG(f.energy), 2) as avg_energy,
                       ROUND(AVG(f.valence), 2) as avg_valence
                FROM artists a
                LEFT JOIN songs s ON a.id = s.artist_id
                LEFT JOIN song_audio_features f ON s.id = f.song_id
                WHERE LOWER(a.name) LIKE ?
                GROUP BY a.id
                ORDER BY total_songs DESC, avg_pop DESC
                LIMIT 3
            """, (f"%{phrase}%",))
            rows = cur.fetchall()
            for r in rows:
                if r["id"] not in matched_artist_ids:
                    matched_artist_ids.add(r["id"])
                    # Fetch top 10 songs for this artist
                    cur.execute("""
                        SELECT s.id, s.title, s.genre, s.popularity, s.release_year,
                               f.tempo, f.energy, f.danceability, f.valence, f.loudness
                        FROM songs s
                        LEFT JOIN song_audio_features f ON s.id = f.song_id
                        WHERE s.artist_id = ?
                        ORDER BY s.popularity DESC, s.title ASC
                        LIMIT 10
                    """, (r["id"],))
                    top_songs = [dict(s_row) for s_row in cur.fetchall()]

                    context["matched_artists"].append({
                        "id": r["id"],
                        "name": r["name"],
                        "country": r["country"] or "India",
                        "debut_year": r["debut_year"] or "N/A",
                        "bio": r["bio"] or "",
                        "song_count": r["total_songs"],
                        "avg_popularity": r["avg_pop"] or 50.0,
                        "avg_tempo": r["avg_tempo"] or 120.0,
                        "avg_energy": r["avg_energy"] or 0.6,
                        "avg_valence": r["avg_valence"] or 0.5,
                        "top_songs": top_songs
                    })

        # 3. Song Retrieval (Tracks with Audio DNA)
        matched_song_ids = set()
        for phrase in search_phrases[:8]:
            songs = self.song_repo.search(query=phrase, limit=8)
            for s in songs:
                if s["id"] not in matched_song_ids:
                    matched_song_ids.add(s["id"])
                    context["matched_songs"].append(s)
                if len(context["matched_songs"]) >= 10:
                    break

        # 4. Location Retrieval (Studios & Filming Hubs)
        all_locs = self.location_repo.get_locations_with_songs()
        for loc in all_locs:
            s_title = str(loc.get("song_title") or "").casefold()
            l_name = str(loc.get("location_name") or "").casefold()
            l_city = str(loc.get("city") or "").casefold()
            l_desc = str(loc.get("description") or "").casefold()
            if any(p in l_name or p in s_title or p in l_city or p in l_desc for p in search_phrases):
                context["matched_locations"].append(loc)
                if len(context["matched_locations"]) >= 6:
                    break

        conn.close()
        return context

    def _format_context_text(self, context: Dict[str, Any]) -> str:
        lines = []
        kpis = context.get("kpis", {})
        lines.append(f"PLATFORM METRICS: {kpis.get('total_songs', 0):,} Total Songs, {kpis.get('total_artists', 0):,} Artists, {kpis.get('total_albums', 0):,} Albums, {kpis.get('total_genres', 0)} Genres, Avg Popularity {kpis.get('avg_popularity', 0)}/100.")

        if context.get("project_matches"):
            lines.append("PLATFORM MODULES: " + " | ".join(PROJECT_INFO["modules"]))

        for art in context.get("matched_artists", []):
            song_list = ", ".join(f"'{s['title']}' (Pop: {s.get('popularity', 50)}, {int(s.get('tempo', 120))} BPM)" for s in art.get("top_songs", [])) or "None indexed"
            lines.append(f"ARTIST RECORD: {art['name']} (Origin: {art.get('country', 'India')}, Tracks in DB: {art.get('song_count', 0)}, Avg Pop: {art.get('avg_popularity')}). Top tracks: {song_list}.")

        for s in context.get("matched_songs", []):
            lines.append(f"TRACK: '{s['title']}' by {s['artist_name']} | Genre: {s.get('genre', 'Pop')} | Popularity: {s.get('popularity', 50)} | Tempo: {int(s.get('tempo', 120))} BPM | Energy: {s.get('energy', 0.5)} | Valence: {s.get('valence', 0.5)}.")

        for loc in context.get("matched_locations", []):
            lines.append(f"LOCATION: {loc.get('location_name')} ({loc.get('location_type')}) in {loc.get('city')}, {loc.get('country')}. Linked Song: '{loc.get('song_title')}' - Notes: {loc.get('scene_notes')}.")

        return "\n".join(lines)

    def _local_answer(self, prompt: str, context: Dict[str, Any]) -> str:
        """Intelligent, structured local RAG conversational synthesis with complete answers."""
        p_lower = prompt.casefold()

        # 1. Project Overview, Architecture & Modules
        if any(w in p_lower for w in ["what is sangeet", "about sangeet", "about project", "project info", "features of", "capabilities", "modules", "architecture", "system", "tech stack", "technology"]):
            modules_list = "\n".join([f"- **{m.split(':')[0]}**: {m.split(':')[1]}" for m in PROJECT_INFO["modules"]])
            tech_list = "\n".join([f"- **{t.split(':')[0]}**: {t.split(':')[1]}" for t in PROJECT_INFO["technologies"]])
            return f"""### 🎵 Sangeet — Music Intelligence Platform
**{PROJECT_INFO['name']}** is an enterprise-grade, local-first music discovery, acoustic analysis, and artificial intelligence platform.

#### 📊 Live Database & Telemetry:
- **Total Tracks Indexed:** **{context['kpis']['total_songs']:,}** Songs across **{context['kpis']['total_genres']}** Genres
- **Artist & Album Scale:** **{context['kpis']['total_artists']:,}** Artists & **{context['kpis']['total_albums']:,}** Albums
- **Acoustic Knowledge:** 12-dimensional Audio DNA per track (BPM, Energy, Valence, Danceability, Key/Mode, Acousticness, etc.)
- **Acoustic Landmarks:** 42+ verified studios and filming locations across India & international hubs.
- **Average Track Popularity:** **{context['kpis']['avg_popularity']} / 100**

---

#### 🧭 9 Complete Platform Modules:
{modules_list}

---

#### ⚡ AI Models & Technical Architecture:
{tech_list}"""

        # 2. Audio Feature Inquiries (Valence, Danceability, Energy, Tempo, Acousticness, etc.)
        for feat, desc in PROJECT_INFO["audio_features"].items():
            if feat in p_lower or (feat == "tempo" and any(k in p_lower for k in ["tempo", "bpm", "speed", "beats per minute"])):
                feat_title = feat.replace("_", " ").title()
                return f"""### 🎛️ Audio DNA Telemetry: **{feat_title}**

**Definition & Meaning:**
> {desc}

#### 🎵 How it works in Sangeet:
- **Calculation:** Normalized acoustic parameter extracted and indexed for all **{context['kpis']['total_songs']:,}** tracks in the catalog.
- **Role in Recommendations:** Used in **Content-Based Cosine Similarity** (Tab 7) to match tracks with identical musical vibe and harmonic mood.
- **Role in Machine Learning:** Fed into **HistGradientBoosting & Random Forest** classifiers to score commercial hit probability!

💡 *Explore live distributions of this feature in **Tab 2 (Analytics)**!*"""

        # 3. Multi-Artist Comparison (e.g. "Compare Arijit Singh and Shreya Ghoshal" or "Arijit vs Sonu")
        if len(context["matched_artists"]) >= 2 and any(k in p_lower for k in ["compare", "vs", "versus", "difference", "both", "between"]):
            art1, art2 = context["matched_artists"][0], context["matched_artists"][1]
            return f"""### ⚖️ Artist Intelligence Comparison: **{art1['name']}** vs. **{art2['name']}**

| Metric / Attribute | 🎤 **{art1['name']}** | 🎤 **{art2['name']}** |
| :--- | :--- | :--- |
| **Origin / Country** | {art1.get('country', 'India')} | {art2.get('country', 'India')} |
| **Catalog Track Count** | **{art1['song_count']:,}** songs | **{art2['song_count']:,}** songs |
| **Average Popularity** | **★ {art1['avg_popularity']} / 100** | **★ {art2['avg_popularity']} / 100** |
| **Average Tempo (BPM)** | {int(art1['avg_tempo'])} BPM | {int(art2['avg_tempo'])} BPM |
| **Acoustic Energy** | {int(art1['avg_energy'] * 100)}% | {int(art2['avg_energy'] * 100)}% |
| **Mood / Valence** | {int(art1['avg_valence'] * 100)}% | {int(art2['avg_valence'] * 100)}% |

#### 🎧 Top Tracks for {art1['name']}:
{chr(10).join([f"- **{s['title']}** (Popularity: ★ {s.get('popularity', 50)}, {int(s.get('tempo', 120))} BPM)" for s in art1.get('top_songs', [])[:5]])}

#### 🎧 Top Tracks for {art2['name']}:
{chr(10).join([f"- **{s['title']}** (Popularity: ★ {s.get('popularity', 50)}, {int(s.get('tempo', 120))} BPM)" for s in art2.get('top_songs', [])[:5]])}"""

        # 4. Single Artist Inquiry (Indian & Foreign/Global Artists)
        if context["matched_artists"]:
            art = context["matched_artists"][0]
            songs = art.get("top_songs", [])
            song_rows = ""
            for idx, s in enumerate(songs, start=1):
                genre_badge = s.get("genre", "Pop").title()
                pop_val = s.get("popularity", 50)
                tempo_val = int(s.get("tempo", 120))
                energy_val = int(float(s.get("energy", 0.5)) * 100)
                valence_val = int(float(s.get("valence", 0.5)) * 100)
                song_rows += f"\n{idx}. **{s['title']}** — *{genre_badge}* · Popularity: **★ {pop_val}/100** · **{tempo_val} BPM** (Energy: {energy_val}%, Valence: {valence_val}%)"

            bio_text = art.get("bio") or f"Renowned global musical icon **{art['name']}** celebrated for timeless discography and acclaimed releases."

            return f"""### 🎤 Complete Artist Profile: **{art['name']}**

- **Origin / Country:** {art.get('country', 'India')}
- **Total Tracks in Database:** **{art.get('song_count', len(songs)):,}** indexed tracks
- **Average Catalog Popularity:** **★ {art.get('avg_popularity', 50.0)} / 100**
- **Average Acoustic Pace:** **{int(art.get('avg_tempo', 120))} BPM** (Energy: {int(art.get('avg_energy', 0.6)*100)}%, Mood/Valence: {int(art.get('avg_valence', 0.5)*100)}%)
- **Debut Era:** {art.get('debut_year', 'N/A')}

> {bio_text}

#### 🎧 Top Hit Tracks in Catalog ({len(songs)} tracks listed):
{song_rows or 'No specific track titles indexed yet.'}

💡 *You can listen to master audio previews for {art['name']} in **Tab 4 (Search)** or **Tab 6 (Artist Photo & Catalog)**!*"""

        # 5. Filming Location & Acoustic Studio Inquiry
        if any(w in p_lower for w in ["where", "film", "shoot", "studio", "location", "place", "city", "mumbai", "chennai", "hyderabad", "kolkata"]) or context["matched_locations"]:
            if context["matched_locations"]:
                loc_details = ""
                for idx, loc in enumerate(context["matched_locations"], start=1):
                    loc_details += f"""
{idx}. **{loc.get('location_name')}** ({loc.get('location_type', 'Studio').replace('_', ' ').title()})
   - **City & Country:** {loc.get('city')}, {loc.get('country')}
   - **Associated Song/Production:** *{loc.get('song_title') or 'General Acoustic Studio'}* by {loc.get('artist_name') or 'Various Artists'}
   - **Acoustic & Production Notes:** {loc.get('scene_notes') or loc.get('description') or 'Historic music recording and filming landmark.'}
"""
                return f"""### 📍 Filming & Recording Location Intelligence
Here is the detailed geospatial record from Sangeet's 42+ Public Music Landmarks Registry:
{loc_details}
💡 *View these studio pins on the interactive map in **Tab 5 (Artist Map)**!*"""

        # 6. Specific Song / Track Inquiry
        if context["matched_songs"]:
            s_details = ""
            for idx, s in enumerate(context["matched_songs"][:6], start=1):
                tempo = int(s.get("tempo", 120))
                energy = int(float(s.get("energy", 0.5)) * 100)
                dance = int(float(s.get("danceability", 0.5)) * 100)
                valence = int(float(s.get("valence", 0.5)) * 100)
                loudness = s.get("loudness", -10.0)
                s_details += f"""
{idx}. **{s['title']}**
   - **Artist:** **{s['artist_name']}** · **Album:** {s.get('album_title', 'Single')} ({s.get('release_year') or 'N/A'})
   - **Genre:** *{s.get('genre', 'Pop').title()}* · **Popularity:** **★ {s.get('popularity', 50)}/100**
   - **Acoustic DNA:** **{tempo} BPM** · Energy: **{energy}%** · Danceability: **{dance}%** · Valence (Mood): **{valence}%** · Loudness: **{loudness} dB**
"""
            return f"""### 🎵 Track Intelligence & Acoustic Telemetry
Found matching tracks in the Sangeet 114K catalog:
{s_details}
💡 *Audition these tracks with master stereo previews in **Tab 4 (Search)** or **Tab 1 (Dashboard)**!*"""

        # 7. Recommendations & Mood Inquiry
        if any(w in p_lower for w in ["recommend", "suggest", "soulful", "romantic", "party", "chill", "acoustic", "happy", "sad", "lo-fi", "workout", "energetic"]):
            top_songs = self.song_repo.get_top_songs(limit=8)
            rec_lines = "\n".join([f"- **{s['title']}** — **{s['artist_name']}** (*{s.get('genre', 'Pop').title()}*, Popularity: ★ {s.get('popularity', 50)}/100 · {int(s.get('tempo', 120))} BPM)" for s in top_songs])
            return f"""### ✨ Curated Recommendations from Catalog:

{rec_lines}

💡 *To find acoustically similar tracks for any song using Content-Based Cosine Similarity, check out **Tab 7 (Song Prediction / Generation)**!*"""

        # 8. Platform Telemetry / General Fallback
        return f"""### 🎵 Sangeet Music Intelligence Assistant
Namaste! I am your AI musicologist grounded across our entire Sangeet database of **{context['kpis']['total_songs']:,} tracks**, **{context['kpis']['total_artists']:,} artists**, and **42+ studio/filming landmarks**.

**Here are some things you can ask me:**
1. **Artists (Indian & Global):** "Tell me about Arijit Singh", "Taylor Swift discography", "Compare AR Rahman and Kishore Kumar", "How many songs does Diljit have?"
2. **Audio DNA Features:** "What is valence?", "What does danceability measure?", "Explain energy and BPM".
3. **Filming & Studios:** "Where was Kun Faya Kun filmed?", "Tell me about AM Studios Chennai", "Filming locations in Mumbai".
4. **Platform & Architecture:** "What is Sangeet?", "How does the ML Hit Predictor work?", "Explain the 9 modules".
5. **Track Lookup & Recommendations:** "Tell me about Tum Hi Ho", "Recommend romantic tracks", "Find high energy songs".

What would you like to explore?"""

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Answers with grounded local catalog facts, project architecture, and optional OpenRouter LLM."""
        last_user_message = next(
            (message["content"] for message in reversed(messages) if message.get("role") == "user"),
            "",
        )
        context = self._get_grounded_context(last_user_message)
        context_text = self._format_context_text(context)

        if not OPENROUTER_API_KEY:
            return self._local_answer(last_user_message, context)

        system_instruction = f"""You are Sangeet AI, the expert musicologist and intelligence assistant for the Sangeet Music Intelligence Platform.
Use the grounded catalog context and project architecture facts below to provide articulate, complete, accurate, beautifully formatted answers.
Never invent artist track counts, filming locations, or song metadata not grounded in data.
Answer in clear, engaging, conversational language.

GROUNDED CATALOG & PROJECT CONTEXT:
{context_text}
"""
        api_messages = [{"role": "system", "content": system_instruction}]
        api_messages.extend(
            {"role": message["role"], "content": message["content"]}
            for message in messages[-6:]
            if message.get("role") in {"user", "assistant"}
        )
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/sangeet-music-intelligence",
            "X-Title": "Sangeet Music Intelligence",
        }
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": api_messages,
            "max_tokens": OPENROUTER_MAX_TOKENS,
            "temperature": 0.4,
        }
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=18,
            )
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content")
                if content:
                    return content
            logger.error("OpenRouter API error %s: %s", response.status_code, response.text)
        except (requests.RequestException, ValueError) as exc:
            logger.error("Assistant request failed: %s", exc)

        return self._local_answer(last_user_message, context)


