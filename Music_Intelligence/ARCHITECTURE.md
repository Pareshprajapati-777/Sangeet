# Architecture & System Design
## Music Intelligence Platform — Final Local-First Architecture

## 0. Architecture Decision
The correct architecture for this project is:

**UI → Service → Repository → SQLite**

Data acquisition and ML/DL are supporting pipelines. Spotify is a future adapter only.

Do not introduce a second production database or distributed infrastructure for the local build.



                         ┌──────────────────────┐
                         │ Kaggle API / CSV     │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │ ETL + Data Quality   │
                         │ Python / Pandas      │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │ SQLite — Phase 1     │
                         │ Source of Truth      │
                         └──────────┬───────────┘
                                    ↓
                       ┌──────────────────────────┐
                       │ Repository / Data Layer  │
                       └────────────┬─────────────┘
                                    ↓
                       ┌──────────────────────────┐
                       │       Service Layer      │
                       ├──────────────────────────┤
                       │ Search                    │
                       │ Analytics                 │
                       │ CRUD                      │
                       │ Recommendation            │
                       │ Playlist                  │
                       │ Voice                    │
                       │ Vision                   │
                       │ Location                 │
                       │ ML / DL                  │
                       │ AI Assistant             │
                       └────────────┬─────────────┘
                                    ↓
                       ┌──────────────────────────┐
                       │      Streamlit UI        │
                       └──────────────────────────┘

Final evolution:
Streamlit → API → Services → External production database + optional Vector DB/Cache.

---

# 2. Phase Roadmap

PHASE 1
Data foundation
→ Search
→ Analytics
→ CRUD
→ Voice
→ Folium
→ Image
→ Recommendation
→ ML
→ DL

PHASE 2
Advanced Search
→ NLP
→ Personalization
→ Playlists
→ Hybrid Recommendation
→ Artist Intelligence
→ Advanced Maps
→ Better Vision/Voice
→ Explainable ML

FINAL
Hybrid AI Recommendation
→ Multimodal Search
→ Audio Intelligence
→ AI Assistant
→ Knowledge Graph
→ Production Architecture
→ Monitoring
→ Scalable Database/API

---

# 3. Search Flow

Text / Voice
     ↓
Search Parser
     ↓
Search Service
     ↓
Repository
     ↓
SQLite / Future External production database
     ↓
Structured SearchResult
     ├── UI
     ├── Voice
     ├── Assistant
     └── Analytics

---

# 4. Voice Flow

Microphone
   ↓
STT
   ↓
Search/Intent
   ↓
Service Layer
   ↓
Result
   ├── Screen
   └── TTS

Example:
“Arijit Singh”
→ Artist search
→ 25 songs
→ “Arijit Singh has 25 songs in the database.”

---

# 5. Image Flow

Image Upload
     ↓
Validation
     ↓
Face Detection
     ↓
Embedding
     ↓
Artist Gallery
     ↓
Similarity
     ↓
Confidence Threshold
     ↓
Artist ID
     ↓
SQLite
     ↓
Artist Profile
     ↓
Song Count + Songs + Albums + Genres

---

# 6. Recommendation Flow

Selected Song
     ↓
Feature Engineering
     ↓
Content Vector
     ↓
Similarity
     ↓
Ranking
     ↓
Top-N
     ↓
Explanation

Phase 2 adds:
User Preferences + Behavior.

Final adds:
Collaborative + Context + Diversity + Freshness.

---

# 7. Analytics Flow

SQLite
 ↓
Pandas
 ↓
Aggregation
 ↓
Visualization
 ↓
Interactive Filters
 ↓
Drill-down
 ↓
Search/detail page

---

# 8. Folium Flow

Song / Artist
 ↓
Location Service
 ↓
Public Location
 ↓
Coordinate Validation
 ↓
Folium
 ├── Hover Tooltip
 └── Click Popup

Popup can contain:
Song
Artist
Movie/source
Singer
Composer
Lyricist
Location
Relationship

---

# 9. ML/DL Flow

SQLite
 ↓
Dataset Builder
 ↓
Feature Engineering
 ↓
Train/Test Split
 ↓
Preprocessing
 ├─────────────┐
 ↓             ↓
ML Models     DL Model
 ↓             ↓
Metrics       Metrics
 └──────┬──────┘
        ↓
 Model Comparison
        ↓
 Prediction Service
        ↓
 Streamlit

---

# 10. Final AI Assistant Flow

User text/voice
      ↓
Intent + Entity Extraction
      ↓
Tool Selection
 ┌────┼────┬─────┬──────┐
 ↓    ↓    ↓     ↓      ↓
Search Analytics Artist Reco Location
 └────┴────┴─────┴──────┘
             ↓
       Answer Generator
             ↓
      Text + Optional Voice

The assistant should ground answers in application data.

---

# 11. Database Evolution

Phase 1:
Artists
Songs
Albums
Genres
Languages
Locations
SongLocations

Phase 2:
Users
Favorites
History
Playlists
Relationships
SearchHistory

Final:
TasteProfiles
RecommendationEvents
ModelVersions
Embeddings
ProductEvents
AuditLogs
DataSources
QualityRuns

---

# 12. Final Architecture Principle

The most important rule:

**Do not let features communicate randomly with the database.**

Correct:
UI → Service → Repository → Database

Incorrect:
UI → raw SQL everywhere

This keeps the project stable while adding every future phase.
