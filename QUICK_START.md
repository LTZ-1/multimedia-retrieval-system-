# 🚀 Database Integration - Quick Reference Card

## Installation (One-Time)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run interactive setup guide
python database_setup.py

# 3. Migrate your existing data
python migrate_to_database.py

# 4. Start the application
python app.py
```

## Running the System

```bash
python app.py
```

Then open: **http://127.0.0.1:5000**

## Database Files

- **SQLite**: `data/multimedia.db` (default, no setup needed)
- **PostgreSQL**: Configure in `config.py`
- **MySQL**: Configure in `config.py` + requires XAMPP

## Two Search Methods

### 📁 Metadata-Based Retrieval (MBR)
- **Input**: Keyword (e.g., "airplane", "face")
- **How**: Database LIKE search on keywords
- **Speed**: ⚡ Very fast
- **Best for**: Known categories and keywords

### 🖼 Content-Based Image Retrieval (CBIR)
- **Input**: Upload an image
- **How**: Compute 512D color histogram, find similar images
- **Speed**: ⚡ Fast
- **Best for**: Finding visually similar images

## Evaluation Metrics

| Metric | Formula | What it means |
|--------|---------|---------------|
| **Precision** | relevant_retrieved / total_retrieved | How many results are actually relevant |
| **Recall** | relevant_retrieved / total_relevant | How many total relevant images were found |
| **Time** | milliseconds | Query execution speed |

## API Endpoints

```
GET  http://127.0.0.1:5000/
     Main search interface

GET  http://127.0.0.1:5000/api/stats
     Returns: {total_images, total_features, categories, total_queries}
```

## Database Commands

```python
from models import db, Image, ImageFeature, SearchQuery
from app import app

with app.app_context():
    # Count images
    total = Image.query.count()
    
    # Search by keyword
    results = Image.query.filter(
        Image.keywords.ilike('%airplane%')
    ).all()
    
    # Get all searches
    queries = SearchQuery.query.all()
    
    # Get image features
    img = Image.query.first()
    features = img.features.features_array  # numpy array
```

## File Locations

```
small_dataset/                    ← Your images
├── airplanes/
├── bonsai/
├── car_side/
├── faces/
└── watch/

features/                         ← Pre-extracted features
├── features.npy
└── image_paths.npy

data/                            ← Database (auto-created)
└── multimedia.db

metadata.csv                      ← Original metadata (used once)
```

## Configuration

**config.py** - Key settings:

```python
DATABASE_TYPE = 'sqlite'           # Change to 'postgresql' or 'mysql'
SQLALCHEMY_DATABASE_URI = '...'    # Connection string
SMALL_DATASET_PATH = 'small_dataset'
FEATURE_VECTOR_DIM = 512           # Color histogram dimensions
DEFAULT_TOP_K = 50                 # Results per query
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Empty database | Run `python migrate_to_database.py` |
| Module not found | Run `pip install -r requirements.txt` |
| Can't connect to PostgreSQL | Check PostgreSQL is running |
| SQLite locked | Wait a moment, SQLite has limited concurrency |
| Images not showing | Ensure `static/uploads/` directory exists |

## Data Migration

```bash
# One-time operation to move CSV/NumPy data to database
python migrate_to_database.py
```

Creates tables and inserts:
- ✅ 50 images from metadata.csv
- ✅ 50 feature vectors from features.npy
- ✅ Search indices for fast queries

## Project Structure

```
multimedia_retrieval/
├── app.py                    ← Main app (DATABASE-INTEGRATED)
├── models.py                 ← Database models
├── config.py                 ← Configuration
├── migrate_to_database.py    ← Data migration script
├── requirements.txt          ← Dependencies
├── small_dataset/            ← Images (50 images, 5 categories)
├── features/                 ← Pre-computed features
├── data/                     ← Database file
└── static/                   ← Web files
    └── uploads/              ← User uploads
```

## Performance Tips

1. **SQLite**: Good for <100K images
2. **PostgreSQL**: Best for large datasets with pgvector
3. **MySQL**: Good middle ground for medium datasets

## Academic Use

### Track Evaluation
All searches logged in database:
```python
from models import SearchQuery
import pandas as pd

# Export evaluation data
logs = SearchQuery.query.all()
df = pd.DataFrame([(q.search_type, q.execution_time) for q in logs])
df.to_csv('evaluation.csv')
```

### Record Relevance Judgments
```python
from models import RelevanceJudgment, db

judgment = RelevanceJudgment(
    query_image_id=1,
    retrieved_image_id=5,
    search_type='MBR',
    is_relevant=True
)
db.session.add(judgment)
db.session.commit()
```

## Next Steps

1. ✅ Installation complete
2. ⏭️ Run: `python migrate_to_database.py`
3. ⏭️ Run: `python app.py`
4. ⏭️ Test at: http://127.0.0.1:5000
5. ⏭️ Evaluate both methods
6. ⏭️ Export results for thesis

---

**Version:** 1.0 Database Integrated  
**Status:** ✅ Ready to Use
