# PRD — Music Intelligence Platform
## Final Local-First Product Requirements: Phase 1 → Phase 2 → Final

> **Decision:** This is a local project first. SQLite remains the application's source of truth. Spotify API is deferred and is not required for any Phase-1 feature. Future external APIs must reduce manual work rather than become hard dependencies.

## 0. Product Rules
- Local-first: the complete core application must run on one machine.
- SQLite is the canonical application database for Phase 1, Phase 2, and the planned final local build.
- CSV/Kaggle ingestion is the primary data acquisition path.
- External APIs are adapters. If an API fails, the core app must continue using local data.
- Do not add PostgreSQL, cloud infrastructure, authentication, queues, or microservices merely for architectural fashion.
- Do not force every source into one CSV. Keep raw source data separate and normalize into SQLite.
- Advanced features are optional until their data and model quality are good enough to demonstrate.
- Restrictions are practical for a private/local project: use public/licensed datasets and respect their stated licenses, but do not design an enterprise compliance system.
- Spotify integration is intentionally deferred.


Music Intelligence is a useful music discovery and intelligence platform, not a portfolio-only dashboard.

It combines:
- Music search and discovery
- Artist intelligence
- Data analytics
- Interactive maps
- Voice interaction
- Image-based artist lookup
- Content-based recommendations
- Machine Learning
- Deep Learning
- Personalization
- Data management

Core principle:
**Every advanced feature must reuse the same underlying data model and services so the application remains stable as features are added.**

---

# PHASE 1 — Foundation + Core Intelligence

## Goal
Create a complete, usable MVP with a clean data pipeline and strong Data Science fundamentals.

### A. Data Acquisition
- CSV upload
- Kaggle API dataset download
- Raw-data storage
- Dataset metadata
- Source/version/license tracking

### B. ETL & Data Quality
- Schema validation
- Column normalization
- Missing-value analysis
- Duplicate detection
- Type conversion
- Outlier checks
- Data cleaning
- Relationship creation
- SQLite loading
- Ingestion report

### C. SQLite Database
Core entities:
- Artists
- Songs
- Albums
- Genres
- Languages
- Locations
- Song-location relationships
- Audio features where available

### D. Data Manager / CRUD
- Add
- View
- Edit
- Delete
- Search/filter
- Validation
- Delete confirmation
- Transaction rollback
- Import/export

### E. Dashboard
- Total songs
- Artists
- Albums
- Genres
- Languages
- Top songs
- Top artists
- Dataset health
- Recent activity

### F. Search
Search by:
- Song
- Artist
- Album
- Movie/source
- Genre
- Language
- Year

Results:
- Exact count
- Matching records
- Artist summary
- Song details
- No-result state

### G. Voice
Search result → structured response → Text-to-Speech.

Examples:
- “25 songs found for Arijit Singh.”
- “This artist has 25 songs in the database.”
- “No records found.”

Optional:
- Speech-to-text search input.

### H. Music Analytics
- Genre distribution
- Artist distribution
- Album analysis
- Language analysis
- Year trends
- Popularity
- Rating
- Duration
- Top-N
- Filters
- Drill-down
- Correlation analysis

### I. Artist + Location Intelligence
Public locations only:
- Birthplace
- Public shooting locations
- Studio/venue
- Song/movie-associated locations

Folium:
- Marker
- Hover tooltip
- Detailed click popup
- Song/artist/movie relationships

### J. Image Intelligence
- Artist image upload
- Face detection
- Embedding
- Labeled artist gallery
- Similarity search
- Confidence threshold
- Artist → song count → songs/albums/genres

### K. Recommendation
Content-based:
- Genre
- Language
- Artist
- Album
- Audio features

Output:
- Top-N
- Similarity score
- Explanation

### L. ML
Choose one defensible task after dataset inspection:
- Hit/Not-Hit classification, OR
- Popularity prediction

Models:
- Logistic Regression
- Random Forest
- XGBoost

### M. Deep Learning
- Feed-forward neural network
- Training/validation curves
- Early stopping
- Evaluation
- ML vs DL comparison

### Phase-1 Exit Criteria
All modules work on one shared SQLite database and can be demonstrated from ingestion to prediction/recommendation.

---

# PHASE 2 — Smart Discovery + Personalization

## Goal
Move from a data application to a genuinely useful discovery platform.

### A. Advanced Search
- Fuzzy search
- Typo tolerance
- Search suggestions
- Multi-filter search
- Search history
- Similar-artist search
- Similar-song search

### B. Natural-Language Search
Examples:
- “Show romantic Hindi songs after 2020.”
- “Give me popular songs by Arijit Singh.”
- “Find songs similar to this one.”

Pipeline:
Natural language → intent extraction → structured filters → Search Service.

### C. Better Recommendations
Add:
- Content-based hybrid scoring
- Artist similarity
- Genre similarity
- Language similarity
- Audio-feature similarity
- Popularity adjustment

### D. User Personalization
Optional account/profile layer:
- Favorite songs
- Favorite artists
- Recently viewed
- Search history
- Likes/dislikes

Use this data for personalized recommendations.

### E. Recommendation Explanation
Every recommendation should explain why:
- Same genre
- Similar audio features
- Same artist
- Similar era
- Similar language
- Similar popularity

### F. Playlist Intelligence
- Create playlist
- Add/remove songs
- Auto-generate playlist
- Genre playlist
- Artist playlist
- Mood/feature-based playlist where data supports it

### G. Advanced Analytics
- Artist trends
- Genre trends
- Language trends
- Popularity over time
- Artist collaboration analysis
- Composer/lyricist analysis
- Movie/song relationships
- Network graphs

### H. Artist Intelligence
Artist profile:
- Biography metadata
- Song count
- Albums
- Genres
- Languages
- Timeline
- Collaborators
- Public locations
- Popular songs
- Similar artists

### I. Location Intelligence
- Map filters
- Artist locations
- Song/movie locations
- Location-based exploration
- Cluster markers
- Timeline/location combinations

### J. Image Intelligence Upgrade
- Better embedding model
- Multiple gallery images per artist
- Gallery management
- Confidence calibration
- Unknown-person rejection
- Artist profile retrieval after match

### K. Voice Upgrade
- Voice input
- Voice search
- Voice result summaries
- Voice navigation
- Voice recommendation requests

### L. ML Upgrade
- Feature importance
- SHAP/explainability where appropriate
- Cross-validation
- Hyperparameter tuning
- Model comparison
- Model registry/versioning

### M. DL Upgrade
Depending on data availability:
- Better neural network
- Embedding models
- Audio classification
- Genre classification
- Mood classification

### Phase-2 Exit Criteria
The application should provide personalized discovery and intelligent search, not just static analytics.

---

# FINAL PHASE — Music Intelligence Ecosystem

## Goal
Turn the project into a polished, scalable, user-centered music intelligence product.

### A. Hybrid Recommendation Engine
Combine:
1. Content similarity
2. User behavior
3. Collaborative filtering
4. Popularity
5. Context
6. Diversity

Ranking:
Final Score =
content + behavior + collaborative + context + diversity adjustments.

### B. Advanced Personalization
- User profiles
- Taste vectors
- Long-term preferences
- Short-term session intent
- Personalized home page
- Personalized playlists
- “Because you liked...” explanations

### C. Audio Intelligence
If legally usable audio/features are available:
- Tempo
- Energy
- Danceability
- Valence
- Instrumentalness
- Spectral features
- Genre classification
- Mood classification
- Similarity from audio embeddings

### D. AI Music Search
Natural-language discovery:
- Mood
- Era
- Language
- Artist
- Genre
- Tempo
- Popularity
- Similarity

Example:
“Give me energetic Hindi songs similar to this song.”

### E. Advanced Artist Intelligence
- Artist knowledge graph
- Collaboration network
- Career timeline
- Genre evolution
- Song/album relationships
- Composer/lyricist network
- Location timeline

### F. Intelligent Map
- Map clustering
- Timeline
- Entity filtering
- Relationship visualization
- Public music-industry locations

### G. Multimodal Intelligence
Input:
- Text
- Voice
- Image
- Music/audio features

Output:
- Artist
- Song
- Similar songs
- Analytics
- Recommendations

### H. AI Assistant
A music-focused assistant can answer questions using the application's structured data:
- “How many songs does this artist have?”
- “Which are their most popular songs?”
- “Show similar artists.”
- “Compare two artists.”
- “What changed in this artist's releases over time?”

The assistant should use application data/tools rather than inventing facts.

### I. Production Readiness
- Authentication
- Role-based access
- User settings
- Audit logs
- Database migration strategy
- Backups
- Error monitoring
- Rate limits
- Caching
- API layer
- Scalable database

### J. Product Analytics
Track privacy-respectful product events:
- Search usage
- Recommendation clicks
- Feature usage
- Failed searches
- Popular filters
- Voice usage
- Image lookup success/failure

Use analytics to improve the product, not to collect unnecessary personal data.

### K. Quality / Trust
- Source attribution
- Dataset provenance
- Confidence indicators
- Model explanations
- “Unknown” instead of forced guesses
- Data freshness indicators
- Clear limitations

### Final Product Outcome
A user can:
1. Search music naturally.
2. Search artists and songs.
3. Hear voice responses.
4. Explore analytics.
5. Explore public locations.
6. Upload a supported artist image.
7. Discover similar music.
8. Get personalized recommendations.
9. Ask intelligent music questions.
10. Explore artist and music relationships.

---

# Feature Addition Rule
New features must be added through existing layers:
UI → Service → Repository → SQLite/API.

Never place business logic directly inside Streamlit pages.

# Future-Safe Rule
Phase 1 uses SQLite. If concurrent multi-user production usage becomes necessary, replace the persistence layer with External production database without redesigning the UI/service contracts.

# Safety / Privacy
- No private residence mapping.
- No unsupported identity claims.
- No copyrighted audio distribution.
- Respect image/data/model licenses.
- Keep credentials outside source control.
