# 🎯 Multimedia Retrieval System - Database Integration Guide

## Project Overview

**Title:** Evaluating Retrieval Performance in a Multimedia Database: Metadata vs. Content-Based Approaches

This is an academic research project that compares two image retrieval methods:
- **Metadata-Based Retrieval (MBR)**: Keyword and category search
- **Content-Based Image Retrieval (CBIR)**: Visual similarity search using color histograms

## ✨ What's New: Database Integration

Your project has been upgraded from file-based storage (CSV + NumPy) to **database-backed storage**. This provides:

✅ **Faster queries** - Indexed keyword search and feature lookups  
✅ **Better organization** - Structured data with relationships  
✅ **Research tracking** - Log all searches and manual judgments  
✅ **Easy experimentation** - Switch between MBR and CBIR seamlessly  
✅ **Scalability** - Handle growing datasets efficiently  

---

## 📋 Quick Start (5 minutes)

### 1. Install Database Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `flask-sqlalchemy` - ORM for database access
- `psycopg2-binary` - PostgreSQL driver (optional)
- `pymysql` - MySQL driver (optional)
- `python-dotenv` - Configuration management

### 2. Run Setup Guide

```bash
python database_setup.py
```

This interactive guide will:
- Check your installation
- Explain database options
- Help you configure your database
- Run the migration

### 3. Migrate Your Data

```bash
python migrate_to_database.py
```

This moves your existing data from CSV/NumPy to the database:
- ✅ Reads `metadata.csv`
- ✅ Reads `features/features.npy`
- ✅ Creates database tables
- ✅ Inserts all images and features

### 4. Run the Application

```bash
python app.py
```

Opens automatically at: http://127.0.0.1:5000

---

## 🗄️ Database Options

### Option 1: SQLite (Recommended for Academic Projects) ⭐

**Best for:** Thesis projects, classroom use, data sharing

```
✅ Pros:
  - Zero setup required
  - Database is a single file: data/multimedia.db
  - Perfect for evaluation and testing
  - Easy to backup and share via email
  - Fast enough for <100K images

❌ Cons:
  - Slower on very large datasets
  - Limited to single-user
  - No built-in vector search
```

**Default in config.py:**
```python
DATABASE_TYPE = 'sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/multimedia.db'
```

**No additional setup needed!**

---

### Option 2: PostgreSQL (Recommended for Research/Production)

**Best for:** Large-scale research, multi-user systems, vector similarity search

```
✅ Pros:
  - Best performance for large datasets
  - pgvector extension for efficient similarity search
  - Multi-user support
  - Advanced SQL capabilities
  - Professional-grade reliability

❌ Cons:
  - Requires server installation
  - More complex setup
  - Separate installation on each machine
```

**Installation & Setup:**

```bash
# Windows: Download from https://www.postgresql.org/download/windows/
# macOS: brew install postgresql
# Linux: sudo apt-get install postgresql

# Create database and user:
psql -U postgres
CREATE USER multimedia_user WITH PASSWORD 'your_password';
CREATE DATABASE multimedia_db OWNER multimedia_user;
```

**Update config.py:**
```python
DATABASE_TYPE = 'postgresql'
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://multimedia_user:password@localhost:5432/multimedia_db'
```

---

### Option 3: MySQL (XAMPP)

**Best for:** Windows users, simple setups, learning database concepts

```
✅ Pros:
  - Easy setup via XAMPP
  - Good for medium datasets
  - Web-based management (PhpMyAdmin)

❌ Cons:
  - Requires XAMPP running
  - No built-in vector support
  - Slower than PostgreSQL
```

**Setup:**
1. Download XAMPP: https://www.apachefriends.org/
2. Start MySQL from XAMPP Control Panel
3. Create database via PhpMyAdmin: http://localhost/phpmyadmin
4. Update config.py:

```python
DATABASE_TYPE = 'mysql'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/multimedia_db'
```

---

## 📊 Database Schema

### Images Table
Stores image metadata:
```sql
CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    image_name VARCHAR(255) UNIQUE,      -- e.g., "image_0020.jpg"
    file_path TEXT,                       -- full path on disk
    category VARCHAR(100),                -- e.g., "airplanes"
    keywords TEXT,                        -- searchable text
    file_size INTEGER,                    -- bytes
    upload_date TIMESTAMP                 -- when added
);
```

### ImageFeature Table
Stores visual features for CBIR:
```sql
CREATE TABLE image_features (
    id INTEGER PRIMARY KEY,
    image_id INTEGER REFERENCES images(id),
    features_json TEXT,                   -- 512D histogram as JSON
    extraction_date TIMESTAMP,
    extraction_method VARCHAR(100)        -- "color_histogram_512"
);
```

### SearchQuery Table
Logs all searches for evaluation:
```sql
CREATE TABLE search_queries (
    id INTEGER PRIMARY KEY,
    query_text TEXT,                      -- keyword or image path
    search_type VARCHAR(20),              -- "MBR" or "CBIR"
    query_date TIMESTAMP,
    results_count INTEGER,
    execution_time FLOAT                  -- seconds
);
```

### RelevanceJudgment Table
For manual evaluation:
```sql
CREATE TABLE relevance_judgments (
    id INTEGER PRIMARY KEY,
    query_image_id INTEGER REFERENCES images(id),
    retrieved_image_id INTEGER REFERENCES images(id),
    search_type VARCHAR(20),              -- "MBR" or "CBIR"
    is_relevant BOOLEAN,                  -- True if relevant
    judge_date TIMESTAMP,
    notes TEXT                            -- comments
);
```

---

## 🔍 Using the System

### Via Web Interface

1. Open http://127.0.0.1:5000
2. Choose search method:
   - **📁 MBR**: Enter keyword (e.g., "airplane", "face")
   - **🖼 CBIR**: Upload an image or enter path

3. View results with metrics:
   - **Precision**: How many results are actually relevant
   - **Recall**: How many total relevant images were found
   - **Time**: Query execution time in seconds

### Via Python Code

```python
from models import db, Image, ImageFeature
from app import app

with app.app_context():
    # Search by keyword
    results = Image.query.filter(
        Image.keywords.ilike('%airplane%')
    ).all()
    
    # Query statistics
    total_images = Image.query.count()
    categories = db.session.query(Image.category).distinct().count()
    print(f"{total_images} images in {categories} categories")
    
    # Access features
    img = Image.query.first()
    features_array = img.features.features_array  # numpy array
```

### Via REST API

```bash
# Get database statistics
curl http://127.0.0.1:5000/api/stats

# Returns:
{
  "total_images": 50,
  "total_features": 50,
  "categories": 5,
  "total_queries": 42
}
```

---

## 📝 Data Migration Details

The `migrate_to_database.py` script:

1. **Loads existing data:**
   - `metadata.csv` → Image records
   - `features/features.npy` → ImageFeature records
   - `features/image_paths.npy` → File paths

2. **Validates files:**
   - Checks files exist on disk
   - Gets file sizes
   - Reports any missing files

3. **Creates indices:**
   - Index on image_name (fast lookup)
   - Index on category (fast filtering)
   - Index on keywords (fast search)

4. **Handles errors gracefully:**
   - Skips corrupted images
   - Reports detailed error messages
   - Commits in batches for safety

### Migration Progress
```
🔄 MIGRATING DATA TO DATABASE
=====================================================================
1️⃣  Creating database tables...
   ✅ Tables created

2️⃣  Loading metadata from CSV...
   ✅ Loaded 50 image records

3️⃣  Loading feature vectors from NumPy...
   ✅ Loaded 50 feature vectors (dim: 512)

4️⃣  Inserting into database...
   ... processed 50/50 images

=====================================================================
✅ MIGRATION COMPLETE
=====================================================================
📊 Statistics:
   • Images added: 50
   • Features added: 50
   • Errors: 0
```

---

## 🔧 Configuration (config.py)

Key settings:

```python
# Database selection
DATABASE_TYPE = 'sqlite'  # or 'postgresql', 'mysql'
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/multimedia.db'

# Dataset paths
SMALL_DATASET_PATH = 'small_dataset'
FEATURES_PATH = 'features'

# Feature extraction
FEATURE_VECTOR_DIM = 512  # 8x8x8 color histogram
FEATURE_EXTRACTION_METHOD = 'color_histogram'

# Search settings
DEFAULT_TOP_K = 50  # Results to return
SIMILARITY_THRESHOLD = 0.1  # Minimum similarity
```

---

## 📊 Project Structure

```
multimedia_retrieval/
├── app.py                      # Main Flask app (DATABASE-INTEGRATED)
├── models.py                   # SQLAlchemy models (NEW)
├── config.py                   # Database config (NEW)
├── migrate_to_database.py      # Data migration script (NEW)
├── database_setup.py           # Setup guide (NEW)
├── requirements.txt            # Dependencies (UPDATED)
├── metadata.csv                # Original metadata (used once)
├── feature_extraction.py       # Feature computation
├── build_feature_database.py   # Feature generation
├── evaluation_*.py             # Evaluation scripts
├── small_dataset/              # Images (5 categories × ~10 images)
│   ├── airplanes/
│   ├── bonsai/
│   ├── car_side/
│   ├── faces/
│   └── watch/
├── features/                   # Feature vectors
│   ├── features.npy            # 512D histograms
│   └── image_paths.npy         # Image file paths
├── data/                       # Database file (NEW)
│   └── multimedia.db           # SQLite database (created after migration)
└── static/
    ├── uploads/                # User-uploaded images
    └── small_dataset/          # Static files
```

---

## 🎓 For Academic Evaluation

### Research Questions
- Which method (MBR vs CBIR) performs better for different query types?
- How do precision and recall compare?
- What's the query time for each method?
- How does performance scale with dataset size?

### Data Collection
All searches are logged in `SearchQuery` table:
```python
from models import SearchQuery

# Get all searches of each type
mbr_queries = SearchQuery.query.filter_by(search_type='MBR').all()
cbr_queries = SearchQuery.query.filter_by(search_type='CBIR').all()

# Calculate average execution time
import statistics
mbr_times = [q.execution_time for q in mbr_queries]
avg_mbr_time = statistics.mean(mbr_times)
```

### Manual Evaluation
Use the `RelevanceJudgment` table to record manual judgments:
```python
from models import db, RelevanceJudgment

# Record that image_45 is relevant to image_12's MBR query
judgment = RelevanceJudgment(
    query_image_id=12,
    retrieved_image_id=45,
    search_type='MBR',
    is_relevant=True,
    notes='Both show airplanes'
)
db.session.add(judgment)
db.session.commit()
```

### Export for Analysis
```python
import pandas as pd

# Export all evaluation data
queries = SearchQuery.query.all()
df = pd.DataFrame([{
    'search_type': q.search_type,
    'query_date': q.query_date,
    'results_count': q.results_count,
    'execution_time': q.execution_time
} for q in queries])

df.to_csv('search_log.csv', index=False)
```

---

## 🐛 Troubleshooting

### Empty database after migration?
```bash
# Check the log output - did it say "Files not found"?
python migrate_to_database.py  # Run again with verbose output
```

### "Database is locked" error (SQLite)?
```bash
# Just wait a moment and try again
# SQLite has limited concurrent access
```

### PostgreSQL connection refused?
```bash
# Make sure PostgreSQL is running:
# Windows: Services → PostgreSQL
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql
```

### Can't upload images in CBIR?
```bash
# Check that static/uploads/ directory exists:
mkdir -p static/uploads
```

### Feature loading errors?
```bash
# Make sure features.npy and image_paths.npy exist:
ls -la features/
# Should show: features.npy, image_paths.npy
```

---

## 📚 Further Reading

### Database Concepts
- SQLAlchemy ORM: https://docs.sqlalchemy.org/
- PostgreSQL: https://www.postgresql.org/docs/
- SQLite: https://www.sqlite.org/docs.html

### Image Retrieval
- Content-based image retrieval: https://en.wikipedia.org/wiki/Content-based_image_retrieval
- Color histograms: https://en.wikipedia.org/wiki/Color_histogram
- Cosine similarity: https://en.wikipedia.org/wiki/Cosine_similarity

### Evaluation Metrics
- Precision and recall: https://en.wikipedia.org/wiki/Precision_and_recall
- Evaluation metrics: https://en.wikipedia.org/wiki/Evaluation_of_information_retrieval

---

## ✅ Checklist

- [ ] Install packages: `pip install -r requirements.txt`
- [ ] Run setup: `python database_setup.py`
- [ ] Migrate data: `python migrate_to_database.py`
- [ ] Run app: `python app.py`
- [ ] Test MBR with keyword search
- [ ] Test CBIR with image upload
- [ ] Check /api/stats endpoint
- [ ] Export search logs for analysis

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review [models.py](models.py) for database structure
3. Check [config.py](config.py) for configuration options
4. Run `python database_setup.py` for interactive help

---

**Version:** 1.0 Database Integrated  
**Last Updated:** 2026-06-01  
**Status:** ✅ Ready for Academic Use
