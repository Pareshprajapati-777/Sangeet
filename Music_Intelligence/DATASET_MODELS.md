# Dataset & Model Master Plan
## Final Research-Backed Source Map — Local-First Music Intelligence

> **Purpose:** This document is the fifth project artifact and is the canonical source map for datasets, enrichment, models, gaps and merge order.
> **Decision:** Spotify API is deferred. The 114K Spotify tracks dataset remains the Phase-1 primary dataset.



**There is no single dataset that covers the whole product.**
Use a layered approach:

**Primary music data**
→ Spotify 114K

**Music metadata enrichment**
→ MusicBrainz

**Large-scale audio research**
→ Million Song Dataset

**Movie/cast/crew enrichment**
→ IMDb datasets

**Artist-image recognition**
→ Bollywood Celebrity Faces + ArcFace/InsightFace

**Semantic search**
→ all-MiniLM-L6-v2

**Voice input**
→ Whisper large-v3

**Genre/audio DL**
→ Wav2Vec2 music genre classifier

Then merge the useful fields into the application's normalized SQLite schema.

---

# 2. DATASETS — USE / MERGE PLAN

## A. PRIMARY — MUST USE

### 1. Spotify Tracks Dataset — 114K
Role: **Main Phase-1 music dataset**

Link:
https://www.kaggle.com/datasets/saichaitanyareddyai/spotify-tracks-dataset-audio-features

Useful fields:
- track_id
- track_name
- artists
- album_name
- popularity
- duration_ms
- explicit
- danceability
- energy
- key
- loudness
- mode
- speechiness
- acousticness
- instrumentalness
- liveness
- valence
- tempo
- time_signature
- track_genre

Why:
Best compact foundation for EDA, recommendation and ML because it is CSV, large enough, and has audio features.

Source evidence:
The dataset reports 114,000 tracks, 114 genres, 31,437 artists and 20 columns. citeturn0search1

Status: **MUST USE**

---

## B. MUST MERGE — MUSIC METADATA

### 2. MusicBrainz Database / API
Link:
https://musicbrainz.org/doc/MusicBrainz_Database/Download

Role:
- artist metadata
- release/album relationships
- recording relationships
- works
- labels
- aliases
- places
- relationships
- additional music metadata

MusicBrainz core database is CC0; supplementary datasets have different licensing. citeturn1search0turn1search1

Important:
Use MBIDs as stable identifiers when matching entities.

Status: **MUST MERGE**

---

## C. MUST MERGE FOR MOVIE/CREDIT INTELLIGENCE

### 3. IMDb Non-Commercial Datasets
Link:
https://developer.imdb.com/non-commercial-datasets/

Role:
- titles
- people
- cast/principals
- crew
- title relationships
- ratings/metadata where applicable

Use it to connect movie/source information with people.

Status: **MUST MERGE IF MOVIE/CINEMA TAB IS REQUIRED**

---

## D. RESEARCH / OPTIONAL LARGE-SCALE AUDIO

### 4. Million Song Dataset
Link:
https://millionsongdataset.com/

Role:
- ~1 million songs
- metadata
- audio-analysis features
- large-scale recommendation experiments

It does **not** contain the actual song audio. citeturn0search2turn0search6

Status: **OPTIONAL FOR PHASE 1; STRONGLY RECOMMENDED PHASE 2/FINAL**

---

## E. IMAGE DATA — MUST USE FOR PHASE-1 IMAGE FEATURE

### 5. Bollywood Celebrity Faces
Link:
https://huggingface.co/datasets/VashuTheGreat2/bollywood_celeb_faces

Role:
- labeled celebrity face images
- artist/celebrity classification/embedding gallery

The dataset currently reports 17,328 images and celebrity-name labels. citeturn0search0

Status: **MUST USE FOR INITIAL IMAGE DEMO**

### Backup / alternative
https://huggingface.co/datasets/amitpuri/bollywood-celebs

This has labeled Bollywood celebrity classes and an MIT license in its dataset card. citeturn0search4

Status: **BACKUP / OPTIONAL**

---

# 3. DATA THAT MUST BE CREATED BY MERGING

Create a normalized internal dataset:

## music_master.csv / SQLite tables

### Song
- song_id
- source IDs
- title
- artist_id
- album_id
- genre_id
- language_id
- release_year
- duration
- popularity
- rating
- audio features

### Artist
- artist_id
- canonical_name
- aliases
- birthplace if available
- public location
- image references
- source IDs

### Album
- album_id
- title
- release date/year
- artist

### Credits
- song_id
- artist
- singer
- composer
- lyricist
- producer
- other roles where available

### Movie/Source
- source_id
- title
- release year
- cast
- crew
- music relationship

### Location
- location_id
- name
- type
- latitude
- longitude
- description
- source

### Image Gallery
- artist_id
- image_path
- source
- license
- embedding

---

# 4. MODELS — RECOMMENDED

## A. Face Recognition / Image Intelligence

### InsightFace / ArcFace — buffalo_l
Reference:
https://huggingface.co/deepghs/insightface/tree/main/buffalo_l

Use:
Face detection + face embedding + similarity matching.

The buffalo_l pack includes detection and recognition components, including w600k_r50. citeturn1search3

**Important licensing:** verify the original InsightFace model terms before commercial deployment; many InsightFace pretrained models are research-oriented.

Status:
**RECOMMENDED FOR IMAGE FEATURE**

Do NOT use a generic image classifier as the final identity system. Embedding + similarity + confidence threshold is better for a growing artist gallery.

---

## B. Semantic Search / NLP

### all-MiniLM-L6-v2
Link:
https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

Use:
- semantic song search
- artist search
- natural-language query matching
- similar descriptions
- Phase-2 recommendation/search enrichment

It creates 384-dimensional embeddings and is designed for semantic search/similarity. citeturn2search0

License: Apache-2.0. citeturn2search3

Status:
**PHASE 2 MUST USE**

---

## C. Voice Input / STT

### OpenAI Whisper large-v3
Link:
https://huggingface.co/openai/whisper-large-v3

Use:
- microphone input
- voice search
- Hindi/English/multilingual speech recognition

The model card lists 99 languages and Apache-2.0 licensing. citeturn2search1

Status:
**PHASE 2 / OPTIONAL PHASE 1**

Practical note:
large-v3 is heavy. For a lightweight local Streamlit deployment, start with a smaller Whisper variant if hardware is limited.

---

## D. Music Genre / Audio DL

### Wav2Vec2 Music Genre Classifier
Link:
https://huggingface.co/gastonduault/music-classifier

Use:
- uploaded audio → genre prediction
- Deep Learning demonstration
- audio intelligence

The model is a Wav2Vec2-based music genre classifier and reports approximately 75% validation accuracy / 74% F1 on its stated validation setup. citeturn0search3

Alternative:
https://huggingface.co/jvalero/wav2vec2-base-music_genre_classifier-g3b

This model reports validation results around 0.74 accuracy at its best listed checkpoint. citeturn0search13

Status:
**PHASE 2 / FINAL**

---

# 5. ML MODELS — DO NOT DOWNLOAD A PRETRAINED MODEL

For the main tabular prediction task, **train your own models**.

Recommended:
1. Logistic Regression — baseline
2. Random Forest — strong interpretable baseline
3. XGBoost — strong tabular model
4. Neural Network / Keras — Deep Learning comparison

Tasks:
- Popularity prediction, OR
- Hit/not-hit classification

Choose the target only after checking whether the dataset has a defensible label.

Status:
**MUST TRAIN YOUR OWN**

Reason:
Using a random pretrained tabular model would add less value than demonstrating a proper reproducible ML pipeline.

---

# 6. DATA GAP REPORT

## COMPULSORY GAPS

### 1. Exact Song → Movie → Shooting Location
**NOT reliably provided by the primary dataset.**

MusicBrainz provides many music/place relationships, but that is not equivalent to a complete Bollywood movie shooting-location database. MusicBrainz documents recording/release place relationships such as recording/engineering locations. citeturn0search5turn0search10

Action:
Create a separate `locations` + `song_locations` enrichment table from verified public sources.

Status: **MISSING — MUST ENRICH IF THIS FEATURE IS REQUIRED**

### 2. Complete Composer / Lyricist / Singer Credits
**NOT guaranteed in Spotify 114K.**

Action:
Enrich through MusicBrainz and a legally usable Indian/Bollywood metadata source.

Status: **PARTIALLY MISSING — MUST ENRICH**

### 3. Exact Artist Birthplace + Coordinates
**NOT complete in the primary dataset.**

MusicBrainz can provide artist/area/place relationships, but coverage is not guaranteed for every artist. The Million Song Dataset also explicitly notes that location is missing for some artists. citeturn0search6

Action:
Enrichment + geocoding.

Status: **PARTIALLY MISSING — ENRICH**

### 4. Exact Artist Image → Music Database ID
No universal ready-made mapping.

Action:
Create your own `artist_id ↔ image ↔ embedding` mapping.

Status: **MISSING — MUST CREATE**

---

# 7. OPTIONAL GAPS

### Raw Song Audio
Not required for Phase 1 because Spotify-style audio features are already available.

Million Song Dataset also contains derived features rather than the actual audio. citeturn0search2

Status: **OPTIONAL**

### Lyrics
Not required for the planned Phase-1 core.

Status: **OPTIONAL / LICENSING REQUIRED**

### User Behavior
Favorites, likes, skips and history do not exist until users use the application.

Status: **GENERATE FROM APP USAGE IN PHASE 2**

---

# 8. FINAL SOURCE STACK

## Phase 1
1. Spotify 114K — PRIMARY
2. MusicBrainz — MUSIC METADATA ENRICHMENT
3. IMDb — MOVIE/CREDIT ENRICHMENT
4. Bollywood Faces — IMAGE GALLERY
5. ArcFace/InsightFace — IMAGE EMBEDDINGS
6. Custom ML models — POPULARITY/HIT PREDICTION
7. Keras neural network — DL

## Phase 2
8. Million Song Dataset — LARGE AUDIO/METADATA RESEARCH
9. all-MiniLM-L6-v2 — SEMANTIC SEARCH
10. Whisper — VOICE INPUT
11. Wav2Vec2 music classifier — AUDIO DL
12. User interaction data — PERSONALIZATION

## Final
13. Hybrid recommendation model
14. Vector/embedding index
15. Knowledge graph
16. Multimodal retrieval
17. Production model serving

---

# 9. Recommended Merge Order

Spotify
↓
Normalize artist/album/song IDs
↓
MusicBrainz entity matching
↓
IMDb movie/title/people enrichment
↓
Location enrichment
↓
Image gallery mapping
↓
Face embeddings
↓
SQLite canonical database
↓
Analytics
↓
Recommendation
↓
ML/DL
↓
Phase-2 semantic/voice/personalization

---

# 10. One Important Rule

**Do not force every source into one giant CSV.**

Keep source-specific raw data separate and create a clean normalized SQLite database as the single application source of truth.

This prevents duplicate columns, broken joins and future migration problems.

## Final decision

**Primary:** Spotify 114K  
**Metadata:** MusicBrainz  
**Cinema:** IMDb  
**Images:** Bollywood Celebrity Faces  
**Face model:** ArcFace/InsightFace  
**Semantic model:** all-MiniLM-L6-v2  
**Voice model:** Whisper  
**Audio DL:** Wav2Vec2 music classifier  
**ML:** Train Logistic Regression + Random Forest + XGBoost yourself  
**DL:** Train Keras model yourself  
**Large-scale research:** Million Song Dataset  
**Still missing:** complete shooting-location mapping, complete Indian credits, complete birthplace coordinates, and image↔artist-ID mapping.

Those missing pieces are **enrichment work**, not a reason to stop the project.

## 11. API Strategy — Deferred
Spotify API is deliberately excluded from the current implementation.

When it is added later, it should sit behind `src/integrations/spotify.py` and feed the same service/repository contracts. The application must still work from the local SQLite database when Spotify is unavailable.

Possible future API use:
- current metadata enrichment
- artwork/preview enrichment where legally and technically available
- live catalog lookup

It must not replace the local dataset or make the application unusable offline.

## 12. Local Project Data Flow
Raw CSV/Kaggle
→ validation
→ cleaning
→ normalization
→ entity matching
→ enrichment
→ SQLite
→ repositories
→ services
→ Streamlit
→ ML/DL/recommendation features

## 13. Acceptance Checklist
- [ ] Primary 114K dataset loaded successfully.
- [ ] Duplicate and missing-value report generated.
- [ ] Canonical SQLite schema created.
- [ ] Artist/song/album/genre relationships validated.
- [ ] Enrichment sources stored separately.
- [ ] Artist-image gallery mapped to internal artist IDs.
- [ ] Face embeddings generated and indexed.
- [ ] Recommendation features generated.
- [ ] ML target verified before training.
- [ ] DL experiment reproducible.
- [ ] Missing location/credit fields explicitly marked rather than fabricated.
- [ ] Spotify API remains disabled until intentionally implemented.
