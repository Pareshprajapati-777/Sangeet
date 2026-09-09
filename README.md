# 🎵 SANGEET — Music Intelligence & Discovery Platform

> 🎶 **Explore. Analyze. Recommend. Discover.**  
> Sangeet is a local-first, full-stack Music Intelligence platform combining music discovery, analytics, geospatial intelligence, computer vision, recommendation systems, ML/DL experiments, and an AI musicologist.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Scikit Learn](https://img.shields.io/badge/Scikit--learn-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

---

## 🌟 What is Sangeet?

**Sangeet** is more than a music player. It is a **Music Intelligence & Discovery ecosystem** built with Python, Streamlit, and SQLite.

It brings together:

- 🎼 Music catalog exploration
- 🔎 Smart search and voice interaction
- 📊 Interactive analytics
- 🗺️ Artist & filming-location intelligence
- 📸 Facial recognition for artist identification
- ✨ Content-based music recommendations
- 🤖 Machine Learning hit-song classification
- 🧠 Deep Learning experimentation
- 🎧 Playlists and favorites
- 💬 AI-powered conversational musicologist

---

## 🏗️ System Architecture

Sangeet follows a clean layered architecture so UI code stays separate from business logic and database operations.

```text
┌─────────────────────────────────────┐
│       🖥️ Streamlit UI / Pages       │
└──────────────────┬──────────────────┘
                   ↓
┌─────────────────────────────────────┐
│     ⚙️ Service Layer                │
│ ETL • Search • Analytics • Vision   │
│ Recommender • ML • DL • AI • Maps   │
└──────────────────┬──────────────────┘
                   ↓
┌─────────────────────────────────────┐
│     🗄️ Repository Layer             │
│   Parameterized SQL & Transactions  │
└──────────────────┬──────────────────┘
                   ↓
┌─────────────────────────────────────┐
│       💾 SQLite Database             │
│       Sangeet.db — Source of Truth │
└─────────────────────────────────────┘
```

> 🔐 Business logic and raw SQL queries are kept outside Streamlit page templates.

---

## 🚀 Platform Features

| # | Module | What it does |
|---|---|---|
| 01 | 📊 **Dashboard** | Live catalog telemetry, top artists, genres, albums, locations, and acoustic-feature insights. |
| 02 | 🔎 **Smart Search & Voice** | Search by title, artist, album, genre, language, year, popularity, plus browser voice interaction. |
| 03 | 📥 **Data Manager** | Kaggle synchronization, CSV import, schema validation, deduplication audits, and CRUD operations. |
| 04 | 📈 **Analytics** | Plotly-powered vibe maps, correlation heatmaps, valence distributions, and release-year trends. |
| 05 | 🗺️ **Artist & Filming Map** | Interactive Folium maps connecting musical works with real-world filming and cultural locations. |
| 06 | 📸 **Image Intelligence** | 128-dimensional facial embeddings for artist recognition with low-confidence unknown detection. |
| 07 | ✨ **Content Recommender** | Cosine-similarity recommendations using danceability, energy, loudness, tempo, and valence. |
| 08 | 🎧 **Playlists & Favorites** | Create custom collections, explore curated playlists, and save favorite tracks. |
| 09 | 🧪 **ML Laboratory** | Random Forest, Logistic Regression, and Gradient Boosting for hit-song classification. |
| 10 | 🧠 **Deep Learning Lab** | PyTorch feed-forward neural network with BatchNorm and Dropout, plus training curves. |
| 11 | 🤖 **Sangeet AI Assistant** | AI musicologist powered by OpenRouter with a local SQLite fallback and voice synthesis. |

---

## 🎯 Recommendation Engine

The recommendation system uses **content-based filtering** rather than collaborative user history.

### 🎚️ Audio Features

- 💃 Danceability
- ⚡ Energy
- 🔊 Loudness
- 🥁 Tempo
- 😊 Valence

Recommendations are generated using **cosine similarity**, with a transparent **"Why this was recommended?"** explanation.

---

## 🧪 Machine Learning Lab

Train and evaluate multiple classification models for **Hit Song Classification**:

- 🌲 Random Forest
- 📉 Logistic Regression
- 🚀 Gradient Boosting

### 📊 Evaluation

- ROC-AUC
- Confusion Matrix
- Feature Importance
- Custom live-track scoring

---

## 🧠 Deep Learning Lab

Sangeet includes a PyTorch-based Feed-Forward Neural Network featuring:

- 🔢 Dense layers
- 📏 BatchNorm1d
- 💧 Dropout regularization
- 📉 Real-time loss tracking
- 🎯 Accuracy tracking across epochs

---

## 📸 Computer Vision

The Image Intelligence module uses **dlib + face_recognition** to create **128-dimensional face embeddings**.

Upload an artist image → extract the embedding → compare against indexed references → return the closest artist match or **Unknown** when confidence is insufficient.

---

## 🎵 Audio Preview

Sangeet does **not distribute copyrighted song audio**.

Instead, audio previews are synthesized from stored musical features, allowing users to interact with the catalog while keeping the project local-first.

---

## 🗺️ Geospatial Intelligence

Explore musical works through interactive maps powered by **Folium**.

Example locations include:

📍 Film City Mumbai  
📍 Mehboob Studio  
📍 Nizamuddin Dargah  
📍 Kashmir Betaab Valley  
📍 Swiss Yash Chopra locations

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| 🐍 Language | Python |
| 🎨 UI | Streamlit |
| 🗄️ Database | SQLite |
| 📊 Visualization | Plotly, Matplotlib |
| 🗺️ Maps | Folium |
| 🤖 Machine Learning | Scikit-learn |
| 🧠 Deep Learning | PyTorch |
| 👁️ Computer Vision | dlib, face_recognition |
| 💬 AI | OpenRouter |
| 📦 Data | Pandas, NumPy, Kaggle API |
| 🧪 Testing | Pytest |

---

## ⚡ Getting Started

### 1️⃣ Clone the repository

```bash
git clone https://github.com/Pareshprajapati-777/Sangeet.git
cd Sangeet
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure environment variables

Create a `.env` file:

```env
DATABASE_URL=sqlite:///Sangeet.db
MAX_UPLOAD_SIZE_MB=50
openrouter=your_openrouter_api_key
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
```

> 🔒 Never commit real API keys or secrets to GitHub.

### 4️⃣ Initialize the database

```bash
python database/seed.py
```

### 5️⃣ Launch Sangeet

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

---

## 🧪 Run Tests

Run the complete test suite:

```bash
python -m pytest tests/
```

---

## 📁 Project Structure

```text
Sangeet/
│
├── 🎵 app.py
├── 📦 requirements.txt
├── 📖 README.md
├── 🔐 .env
├── 💾 Sangeet.db
│
├── 🎨 assets/
│   ├── style.css
│   └── artist_gallery/
│
├── 🗄️ database/
│   ├── schema.sql
│   └── seed.py
│
├── ⚙️ src/
│   ├── config.py
│   ├── db.py
│   ├── domain/
│   │   └── entities.py
│   ├── repositories/
│   │   ├── base.py
│   │   ├── songs.py
│   │   ├── artists.py
│   │   ├── albums.py
│   │   ├── locations.py
│   │   └── playlists.py
│   ├── services/
│   │   ├── etl.py
│   │   ├── search.py
│   │   ├── analytics.py
│   │   ├── recommender.py
│   │   ├── location.py
│   │   ├── vision.py
│   │   ├── ml.py
│   │   ├── dl.py
│   │   ├── voice.py
│   │   └── assistant.py
│   └── utils/
│       ├── audio_mock.py
│       └── export_helpers.py
│
├── 📄 pages/
│   ├── 1_Dashboard.py
│   ├── 2_Analytics.py
│   ├── 3_Data_Manager.py
│   ├── 4_Search.py
│   ├── 5_ML_Lab.py
│   ├── 6_DL_Lab.py
│   ├── 7_Playlists.py
│   └── 8_AI_Assistant.py
│
└── 🧪 tests/
    └── test_core.py
```

---

## 🧭 Application Flow

```text
🎵 Discover Music
       ↓
🔎 Search & Filter
       ↓
📊 Analyze Audio Features
       ↓
✨ Get Recommendations
       ↓
🎧 Build Playlists
       ↓
📸 Identify Artists
       ↓
🗺️ Explore Locations
       ↓
🧪 Experiment with ML/DL
       ↓
🤖 Ask Sangeet AI
```

---

## 📜 License & Acknowledgements

- 🎼 **Primary Music Features:** Saichaitanya Reddy / Spotify Tracks Dataset
- 💾 **Local Database:** SQLite3 with WAL mode
- 👁️ **Biometric Recognition:** dlib & face_recognition
- 🤖 **Conversational Intelligence:** OpenRouter / Google Gemini
- 🐍 **Core Ecosystem:** Python, Streamlit, Pandas, NumPy, PyTorch & Scikit-learn

---

## ⭐ Support the Project

If you find **Sangeet** useful or interesting:

⭐ Star the repository  
🍴 Fork the project  
🐛 Report issues  
💡 Suggest improvements  
🤝 Contribute

---

<div align="center">

### 🎶 Sangeet — Turning Music Data into Intelligence. 🎶

**Built with Python 🐍 • Data 📊 • AI 🤖 • Music 🎵**

</div>
