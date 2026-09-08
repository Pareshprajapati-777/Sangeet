# TRD — Music Intelligence Platform
## Final Technical Requirements — Local-First Build

> **Primary stack:** Python + Streamlit + SQLite. The system is intentionally simple enough to build, debug and demonstrate locally.

## 0. Non-Negotiable Technical Decisions
1. SQLite is the single application source of truth.
2. Python owns ETL, services, ML/DL and integrations.
3. Streamlit owns the UI.
4. Repository/service boundaries are used so UI code does not contain scattered SQL.
5. CSV/Kaggle ingestion must work without Spotify.
6. Spotify API is a deferred adapter, not a Phase-1 dependency.
7. External integrations must have graceful fallbacks.
8. No PostgreSQL migration work is part of this project plan.
9. No cloud deployment is required for the local project.
10. Use simple local files/model artifacts before introducing additional infrastructure.



## Phase 1
Python
Streamlit
SQLite
sqlite3
Pandas
NumPy
Plotly
Folium
streamlit-folium
scikit-learn
XGBoost
TensorFlow/Keras
OpenCV
STT/TTS adapter
pytest
Git/GitHub

## Phase 2
Everything in Phase 1 plus:
- Fuzzy matching
- NLP / intent extraction
- Recommendation hybridization
- User preference storage
- Playlist engine
- Explainability
- Better embedding models
- Model versioning

## Final Phase
Everything above plus, when justified:
- FastAPI/API layer
- External production database migration
- Redis/cache
- Background jobs
- Vector database/vector index
- Authentication
- Role-based access
- Observability
- Production model serving
- Scalable deployment

Do not introduce production infrastructure before it is actually needed.

---

# 2. Layered Architecture

Presentation Layer
→ Streamlit pages/components

Application Layer
→ Use cases/services

Domain Layer
→ Music entities, recommendation rules, search logic

Data Layer
→ Repositories

Persistence
→ SQLite Phase 1
→ External production database optional Final Phase

ML/DL Layer
→ Training pipelines + model artifacts

External Integration Layer
→ Kaggle, STT, TTS, public metadata, image/model providers

---

# 3. Canonical Project Structure

music-intelligence/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── LICENSE
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── exports/
│   └── music.db
│
├── database/
│   ├── schema.sql
│   ├── seed.py
│   └── migrations/
│
├── assets/
│   ├── artist_gallery/
│   └── icons/
│
├── models/
│   ├── ml/
│   ├── dl/
│   └── embeddings/
│
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_recommendation.ipynb
│   └── 05_model_training.ipynb
│
├── src/
│   ├── config.py
│   ├── db.py
│   ├── etl.py
│   ├── validation.py
│   ├── logging_config.py
│   │
│   ├── domain/
│   │   ├── entities.py
│   │   └── rules.py
│   │
│   ├── repositories/
│   │   ├── songs.py
│   │   ├── artists.py
│   │   ├── albums.py
│   │   ├── locations.py
│   │   └── users.py
│   │
│   ├── services/
│   │   ├── search.py
│   │   ├── analytics.py
│   │   ├── crud.py
│   │   ├── recommender.py
│   │   ├── playlist.py
│   │   ├── voice.py
│   │   ├── vision.py
│   │   ├── location.py
│   │   ├── ml.py
│   │   ├── dl.py
│   │   └── assistant.py
│   │
│   ├── integrations/
│   │   ├── kaggle.py
│   │   ├── stt.py
│   │   ├── tts.py
│   │   └── metadata.py
│   │
│   └── utils/
│
├── pages/
│   ├── home.py
│   ├── data_manager.py
│   ├── search.py
│   ├── analytics.py
│   ├── artist_location.py
│   ├── voice_search.py
│   ├── image_intelligence.py
│   ├── recommendations.py
│   ├── playlists.py
│   ├── ml_lab.py
│   ├── dl_lab.py
│   └── assistant.py
│
└── tests/

---

# 4. Database Evolution

## Phase 1
artists
songs
albums
genres
languages
locations
song_locations
song_audio_features (optional)

## Phase 2
users
user_favorites
user_history
playlists
playlist_songs
artist_relationships
song_relationships
search_history

## Final Phase
user_taste_profiles
recommendation_events
model_versions
embedding_index metadata
product_events
audit_logs
data_sources
data_quality_runs

Database schema must evolve through migrations, not destructive manual edits.

---

# 5. Data Pipeline

Kaggle API / CSV
→ raw/
→ schema validation
→ profiling
→ cleaning
→ normalization
→ entity resolution
→ relationship building
→ quality checks
→ SQLite
→ analytics/model datasets

Every ingestion should produce:
- row count
- inserted count
- updated count
- rejected count
- duplicate count
- missing-value summary
- validation errors
- source metadata

---

# 6. Search Architecture

Phase 1:
SQL exact/partial search.

Phase 2:
Fuzzy + typo-tolerant + multi-filter + NLP intent.

Final:
Hybrid lexical + semantic/vector retrieval.

Search response contract:
status
entity_type
count
records
summary_text
confidence (when applicable)

This contract feeds:
- UI
- Voice
- Assistant
- Analytics drill-down

---

# 7. Voice Architecture

STT:
Audio → text

Search:
text → Search Service

Response:
Search Result → response generator → TTS

Voice should never contain database logic.

Fallback:
If TTS fails, show the text response normally.

---

# 8. Folium Architecture

Entity
→ location service
→ public coordinate validation
→ map marker
→ tooltip
→ popup.

Tooltip = concise.
Popup = detailed.

Possible future:
- clustering
- filters
- timeline
- relationship layers.

---

# 9. Image Intelligence

Phase 1:
Face detection → embedding → labeled artist gallery → threshold → database.

Phase 2:
Multiple reference images + better embeddings + unknown rejection.

Final:
Multimodal retrieval with text/image embeddings where technically justified.

Never return a confident identity below the configured threshold.

---

# 10. Recommendation Architecture

Phase 1:
Content-based cosine similarity.

Phase 2:
Hybrid:
content + artist + genre + audio + user preferences.

Final:
Hybrid ranking:
content
+ collaborative filtering
+ context
+ popularity
+ diversity
+ freshness.

Always expose recommendation reason.

---

# 11. ML Architecture

Phase 1:
One reliable prediction task.

Phase 2:
Model comparison + tuning + explainability.

Final:
Model registry + versioning + monitoring + retraining workflow.

Required:
- reproducible preprocessing
- train/validation/test separation
- no leakage
- saved preprocessing
- saved model
- evaluation report

---

# 12. Deep Learning Architecture

Phase 1:
Dense network for tabular task.

Phase 2:
Better architectures / embeddings / audio classification if data supports it.

Final:
Multimodal/audio models only when they provide measurable value.

DL must be justified by performance or capability, not included only for resume keywords.

---

# 13. Streamlit Architecture

Use:
- st.Page/st.navigation
- reusable components
- service calls from pages
- st.cache_data for repeatable data
- st.cache_resource for reusable resources
- pagination
- session_state only when needed

Pages must remain thin:
UI → service call → render.

---

# 14. API / Production Evolution

Phase 1:
No API required.

Phase 2:
Internal service contracts.

Final:
Optional FastAPI layer:
Streamlit
→ API
→ services
→ repositories
→ External production database/vector storage.

This is introduced only if multiple clients, mobile apps or external integrations are required.

---

# 15. Performance Evolution

Phase 1:
SQLite indexes + pagination + caching.

Phase 2:
Optimized queries + precomputed analytics + embeddings.

Final:
External production database + Redis/cache + background jobs + vector retrieval if required.

---

# 16. Security

All phases:
- secrets outside Git
- parameterized SQL
- upload validation
- size limits
- safe file handling
- destructive-action confirmation
- public-location-only policy
- license tracking

Final:
- authentication
- authorization
- rate limiting
- audit logs
- encrypted secrets
- monitoring

---

# 17. Testing Strategy

Unit:
services, repositories, validation, ETL, recommendation, voice response, model preprocessing.

Integration:
Kaggle/CSV → SQLite
SQLite → search
SQLite → analytics
model → prediction

End-to-end:
User search → results → voice.
Image → artist → songs.
Song → recommendation.
Song → location map.

Final:
CI pipeline + regression tests + model tests.

---

# 18. Deployment Evolution

Phase 1:
Local Python + SQLite + Streamlit.

Phase 2:
Streamlit deployment + persistent storage strategy.

Final:
Streamlit frontend + API/backend + External production database + optional Redis/vector infrastructure.

---

# 19. Observability

Phase 1:
Application logs + error messages.

Phase 2:
Feature usage and model metrics.

Final:
- structured logs
- performance monitoring
- error tracking
- model drift monitoring
- data-quality alerts

---

# 20. Migration Rule

Do not rewrite the application when moving from SQLite.

Required abstraction:
Repository → database implementation.

SQLiteRepository can later become External production databaseRepository.

---

# 21. Non-Functional Requirements

- Maintainable
- Testable
- Modular
- Reproducible
- Explainable
- Privacy-aware
- License-aware
- Fast enough for interactive use
- Graceful error handling
- Clear empty/loading/error states
