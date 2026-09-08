"""
Configuration management for Sangeet: Music Intelligence Platform.
Loads settings from .env and defines project path constants.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Root Directory
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Load environment variables
ENV_FILE = ROOT_DIR / ".env"
load_dotenv(ENV_FILE)

# Project Directories
SRC_DIR = ROOT_DIR / "src"
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ASSETS_DIR = ROOT_DIR / "assets"
GALLERY_DIR = ASSETS_DIR / "artist_gallery"
MODELS_DIR = ROOT_DIR / "models"
DATABASE_DIR = ROOT_DIR / "database"

# Ensure runtime directories exist
for folder in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, ASSETS_DIR, GALLERY_DIR, MODELS_DIR, DATABASE_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Canonical SQLite Database Path
# Primary source of truth: Sangeet.db in root or database/Sangeet.db
DB_PATH = ROOT_DIR / "Sangeet.db"

# Credentials & APIs
OPENROUTER_API_KEY = (os.getenv("openrouter") or os.getenv("OPENROUTER_API_KEY") or "").strip('"\n\r ')
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
OPENROUTER_MAX_TOKENS = 2048

KAGGLE_USERNAME = (os.getenv("KAGGLE_USERNAME") or "").strip('"\n\r ')
KAGGLE_KEY = (os.getenv("KAGGLE_KEY") or "").strip('"\n\r ')

# Synchronize Kaggle credentials into system env for kaggle library
if KAGGLE_USERNAME and KAGGLE_KEY:
    os.environ["KAGGLE_USERNAME"] = KAGGLE_USERNAME
    os.environ["KAGGLE_KEY"] = KAGGLE_KEY

MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
DEFAULT_PAGE_SIZE = 25
