# 🎵 SANGEET — Music Intelligence & Discovery Platform

**Sangeet** is a local-first, full-stack Music Intelligence and Discovery ecosystem built with Python, Streamlit, and SQLite. It combines music catalog exploration, geospatial mapping, deep facial recognition, content-based recommendation vectors, predictive Machine Learning & Deep Learning laboratories, and an AI conversational musicologist.

---

## 🏛️ System Architecture

Sangeet adheres to a strict layered design:

```
Streamlit Pages (UI Presentation)
       ↓
Service Layer (ETL, Search, Analytics, Vision, Recommender, ML, DL, Assistant, Location)
       ↓
Repository Layer (Parameterized SQL & Transactions)
       ↓
SQLite Database (Sangeet.db — Single Source of Truth)
```

No business logic or raw SQL queries reside within Streamlit page templates.

---

## 🌟 Key Platform Modules

| Module | Features & Capabilities |
|---|---|
| **📊 Dashboard** | Live catalog telemetry (songs, artists, albums, genres, locations), top artist rankings, and average acoustic feature radar DNA. |
| **🔍 Smart Search & Voice** | Multi-attribute filtering (title, artist, album, genre, language, year, popularity), native browser audio controls for feature-driven previews, and browser Web Speech Text-to-Speech readouts. |
| **📥 Data Manager / CRUD** | Kaggle API dataset synchronization, CSV upload & schema validation, deduplication audit logging, and full database CRUD operations for songs and artists. |
| **📈 Analytics** | Multidimensional Plotly visualizations: Danceability vs. Energy vibe mapping, audio feature correlation heatmaps, valence distributions, and release year trends. |
| **🗺️ Artist & Filming Map** | Interactive Folium geospatial intelligence with clustered markers, tooltips, and rich HTML popups linking real-world locations (Film City Mumbai, Mehboob Studio, Nizamuddin Dargah, Kashmir Betaab Valley, Swiss Yash Chopra lakes) to musical works. |
| **📸 Image Intelligence** | Upload artist portraits and real gallery references; 128-dimensional facial embeddings match indexed references with an explicit unknown result when confidence is low. |
| **✨ Content Recommender** | Content-based cosine similarity engine evaluating acoustic feature vectors (danceability, energy, loudness, tempo, valence) with transparent "Why this was recommended" explanations. |
| **🎧 Playlists & Favorites** | Create and manage custom collections, explore curated sets (Bollywood Essentials, Sufi & Soulful, High-Octane Bhangra), and bookmark favorite tracks. |
| **🧪 ML Laboratory** | Train and evaluate classical machine learning models (Random Forest, Logistic Regression, Gradient Boosting) for Hit Song Classification. Inspect ROC-AUC, confusion matrices, feature importances, and score live custom tracks. |
| **🧠 Deep Learning Lab** | PyTorch Feed-Forward Deep Neural Network with BatchNorm1d and Dropout regularization. Inspect real-time loss and accuracy curves across training epochs. |
| **🤖 Sangeet AI Assistant** | Grounded conversational musicologist powered by OpenRouter (`google/gemini-3.8-flash`) with a local SQLite fallback when the API is unavailable, plus voice speech synthesis. |

Audio previews are synthesized from the stored audio features because this local catalog does not distribute copyrighted song audio. Use the native player on any song card to listen to an instrumental preview.

The main shell keeps the existing tab design while grouping Image Intelligence with the Deep Learning Lab in tab 6, and Recommendations with the Machine Learning Lab in tab 7. The merged tabs expose quick results first and keep the full experiment controls inside expandable sections.

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure Python 3.10+ is installed on your machine.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Your `.env` file should configure:
```env
DATABASE_URL=sqlite:///Sangeet.db
MAX_UPLOAD_SIZE_MB=50
openrouter=your_openrouter_api_key
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
```

### 4. Database Setup & Seeding
To initialize the SQLite schema and seed the catalog:
```bash
python database/seed.py
```

### 5. Launch the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Automated Testing
Run the complete automated test suite:
```bash
python -m pytest tests/
```

---

## 📁 Repository Structure

`app.py` is the canonical 9-tab shell. Tab 6 groups artist-photo intelligence with DL, and tab 7 groups recommendations with ML; the `pages/` files remain compatibility wrappers for the original standalone pages.

```
Sangeet/
├── app.py                     # Main Streamlit entrance & dark theme shell
├── requirements.txt           # Python dependency specifications
├── README.md                  # System manual and architecture documentation
├── .env                       # Local secrets & API keys
├── Sangeet.db                 # Canonical SQLite database
│
├── assets/
│   ├── style.css              # Custom dark-mode glassmorphic theme
│   └── artist_gallery/        # Reference artist portraits
│
├── database/
│   ├── schema.sql             # Canonical SQLite table schemas & indexes
│   └── seed.py                # Database seeder (curated catalog + Kaggle sync + real face references)
│
├── src/
│   ├── config.py              # Environment configuration & path constants
│   ├── db.py                  # Thread-safe SQLite connection & transaction manager
│   ├── domain/
│   │   └── entities.py        # Domain data classes & contracts
│   ├── repositories/
│   │   ├── base.py            # Generic query executor
│   │   ├── songs.py           # Song & audio features repository
│   │   ├── artists.py         # Artist profile & face encodings repository
│   │   ├── albums.py          # Album tracklist repository
│   │   ├── locations.py       # Geographical points of interest repository
│   │   └── playlists.py       # Playlists & favorites persistence
│   ├── services/
│   │   ├── etl.py             # Data acquisition, cleaning & quality audit
│   │   ├── search.py          # Multi-criteria search with voice summary
│   │   ├── analytics.py       # Catalog statistics & correlations
│   │   ├── recommender.py     # Content-based cosine recommendation engine
│   │   ├── location.py        # Folium interactive geospatial map builder
│   │   ├── vision.py          # 128-d face recognition & artist matching
│   │   ├── ml.py              # Scikit-learn tabular classification lab
│   │   ├── dl.py              # PyTorch Deep Neural Network lab
│   │   ├── voice.py           # Web Speech API text-to-speech engine
│   │   └── assistant.py       # Grounded OpenRouter AI Assistant
│   └── utils/
│       ├── audio_mock.py      # Feature-driven synthetic WAV preview generator
│       └── export_helpers.py  # CSV / JSON export formatters
│
├── pages/
│   ├── 1_Dashboard.py         # Compatibility page wrappers
│   ├── 2_Analytics.py
│   ├── 3_Data_Manager.py
│   ├── 4_Search.py
│   ├── 5_ML_Lab.py
│   ├── 6_DL_Lab.py
│   ├── 7_Playlists.py
│   └── 8_AI_Assistant.py
│
└── tests/
    └── test_core.py           # Automated test suite
```

---

## 📜 License & Acknowledgements
- **Primary Music Features:** Saichaitanya Reddy / Spotify Tracks Dataset (Audio Features)
- **Local-First Architecture:** SQLite3 WAL mode
- **Biometric Recognition:** `dlib` & `face_recognition`
- **Conversational Intelligence:** OpenRouter API (`google/gemini-3.8-flash`)
