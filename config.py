"""
Database configuration
Switch between SQLite (development/academic) and PostgreSQL (production)
"""
import os
from pathlib import Path

# Get absolute paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

# ============================================================================
# DATABASE CONFIGURATION - CHOOSE YOUR DATABASE
# ============================================================================

# OPTION 1: SQLite (Recommended for Academic/Development)
# ✅ No setup required
# ✅ All data in single file: data/multimedia.db
# ✅ Perfect for evaluation and testing
DATABASE_TYPE = 'sqlite'
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATA_DIR / "multimedia.db"}'

# OPTION 2: PostgreSQL (Better performance for production)
# Uncomment below and configure if using PostgreSQL
# ❌ Requires PostgreSQL server running
# DATABASE_TYPE = 'postgresql'
# SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://username:password@localhost:5432/multimedia_db'

# OPTION 3: MySQL (Via XAMPP)
# Uncomment below if using MySQL
# ❌ Requires MySQL server running (via XAMPP)
# DATABASE_TYPE = 'mysql'
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/multimedia_db'

# ============================================================================
# FLASK CONFIGURATION
# ============================================================================

UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False  # Set to True to see SQL queries

MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max upload size: 16MB

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tiff'}

# Dataset paths
SMALL_DATASET_PATH = BASE_DIR / 'small_dataset'
FEATURES_PATH = BASE_DIR / 'features'

# Feature extraction settings
FEATURE_VECTOR_DIM = 512  # Color histogram (8x8x8 bins)
FEATURE_EXTRACTION_METHOD = 'color_histogram'

# Search settings
DEFAULT_TOP_K = 50  # Number of results to return
SIMILARITY_THRESHOLD = 0.1  # Minimum similarity to include

print(f"🗄️  Using {DATABASE_TYPE.upper()} database")
print(f"📁 Database file: {SQLALCHEMY_DATABASE_URI}")
print(f"📂 Dataset path: {SMALL_DATASET_PATH}")
