#!/usr/bin/env python3
"""
Database Setup and Migration Guide
Multimedia Retrieval System

This script helps you set up the database and migrate your existing data.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(title):
    print(f"\n{'='*70}")
    print(f"✅ {title}")
    print(f"{'='*70}\n")

def print_step(step_num, title):
    print(f"\n{step_num}️⃣  {title}")
    print("-" * 70)

def check_python_packages():
    """Check if required packages are installed"""
    print_step(1, "Checking Python Packages")
    
    required = {
        'flask': 'Flask',
        'sqlalchemy': 'SQLAlchemy',
        'flask_sqlalchemy': 'Flask-SQLAlchemy',
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'sklearn': 'Scikit-learn'
    }
    
    missing = []
    for module, name in required.items():
        try:
            __import__(module)
            print(f"✓ {name} installed")
        except ImportError:
            print(f"✗ {name} NOT installed")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"\nInstall missing packages with:")
        print(f"  pip install -r requirements.txt\n")
        return False
    
    print("\n✅ All required packages installed!")
    return True

def explain_database_options():
    """Explain database options"""
    print_step(2, "Database Options")
    
    print("""
📌 You have 3 database options:

1️⃣  SQLITE (Recommended for Academic Projects)
    ✅ No setup required
    ✅ All data in single file: data/multimedia.db
    ✅ Perfect for evaluation and testing
    ✅ Easy to backup and share
    ⚠️  Slower for very large datasets (>1M images)
    
2️⃣  POSTGRESQL (Recommended for Production)
    ✅ Better performance
    ✅ Vector similarity search (pgvector extension)
    ✅ Multi-user support
    ❌ Requires server installation
    ❌ More complex setup
    
3️⃣  MYSQL (Via XAMPP)
    ✅ Lightweight
    ✅ Easy setup via XAMPP
    ✅ Good for smaller datasets (<1M)
    ❌ No native vector support
    ❌ Requires XAMPP running

""")

def show_sqlite_setup():
    """Show SQLite setup (default)"""
    print_step(3, "SQLite Setup (Default)")
    
    print("""
✅ SQLite is already configured!

The database will be created automatically at:
  data/multimedia.db

Next steps:
  1. Run: python migrate_to_database.py
  2. Run: python app.py
  3. Open: http://127.0.0.1:5000
    """)

def show_postgresql_setup():
    """Show PostgreSQL setup instructions"""
    print_step(3, "PostgreSQL Setup")
    
    print("""
❌ Requires manual setup. Steps:

1. Install PostgreSQL
   Windows: https://www.postgresql.org/download/windows/
   Mac: brew install postgresql
   Linux: sudo apt-get install postgresql

2. Create database and user:
   psql -U postgres
   CREATE USER multimedia_user WITH PASSWORD 'your_password';
   CREATE DATABASE multimedia_db OWNER multimedia_user;

3. Update config.py:
   Change DATABASE_TYPE = 'sqlite' to:
   DATABASE_TYPE = 'postgresql'
   SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://multimedia_user:your_password@localhost:5432/multimedia_db'

4. Run migration:
   python migrate_to_database.py

5. Run the app:
   python app.py
    """)

def show_mysql_setup():
    """Show MySQL setup instructions"""
    print_step(3, "MySQL Setup (XAMPP)")
    
    print("""
❌ Requires XAMPP. Steps:

1. Download XAMPP from: https://www.apachefriends.org/

2. Start MySQL from XAMPP Control Panel

3. Create database:
   Open http://localhost/phpmyadmin
   Create new database: multimedia_db

4. Update config.py:
   Change DATABASE_TYPE = 'sqlite' to:
   DATABASE_TYPE = 'mysql'
   SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/multimedia_db'

5. Run migration:
   python migrate_to_database.py

6. Run the app:
   python app.py
    """)

def run_migration():
    """Run the data migration"""
    print_step(4, "Data Migration")
    
    print("""
📊 The migration script will:

1. Load existing CSV metadata (metadata.csv)
2. Load existing feature vectors (features/features.npy)
3. Create database tables
4. Insert all images and features into database
5. Create search indices for fast queries

This is a ONE-TIME operation.
    """)
    
    response = input("Ready to migrate data? (y/n): ").strip().lower()
    
    if response == 'y':
        print("\n🔄 Starting migration...\n")
        try:
            subprocess.run([sys.executable, 'migrate_to_database.py'], check=True)
            print("\n✅ Migration completed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Migration failed: {e}")
            return False
    else:
        print("⏭️  Skipping migration for now")
    
    return True

def explain_search_methods():
    """Explain search methods"""
    print_step(5, "Search Methods Explained")
    
    print("""
🎯 Your system evaluates TWO retrieval methods:

📁 METADATA-BASED RETRIEVAL (MBR)
   - Searches by keywords and categories
   - Fast keyword matching using database
   - Best for: well-annotated data
   - Advantages: explainable, fast
   - Limitations: missing keywords = no results

🖼 CONTENT-BASED RETRIEVAL (CBIR)
   - Searches by visual similarity (color histograms)
   - Uses cosine similarity on 512D feature vectors
   - Best for: finding visually similar images
   - Advantages: finds unlabeled similar images
   - Limitations: depends on feature quality

📊 EVALUATION METRICS:
   - Precision: relevant_retrieved / total_retrieved
   - Recall: relevant_retrieved / total_relevant_in_dataset
   - Retrieval Time: query execution time
    """)

def show_api_endpoints():
    """Show available API endpoints"""
    print_step(6, "API Endpoints")
    
    print("""
🔌 REST API Endpoints:

GET http://127.0.0.1:5000/
   Main search interface

GET http://127.0.0.1:5000/api/stats
   Returns database statistics:
   {
     "total_images": 50,
     "total_features": 50,
     "categories": 5,
     "total_queries": 12
   }

POST http://127.0.0.1:5000/
   Perform search:
   - method: 'mbr' or 'cbr'
   - query: keyword for MBR
   - upload: image file for CBIR
    """)

def show_next_steps():
    """Show next steps"""
    print_step(7, "Next Steps")
    
    print("""
1️⃣  Run the migration:
   python migrate_to_database.py

2️⃣  Start the application:
   python app.py

3️⃣  Open your browser:
   http://127.0.0.1:5000

4️⃣  Test both search methods:
   - Try MBR with keywords: "airplane", "face", "watch"
   - Try CBIR by uploading test images

5️⃣  Monitor statistics:
   http://127.0.0.1:5000/api/stats

6️⃣  For evaluation/research:
   - The SearchQuery and RelevanceJudgment tables
   - Store all queries and manual relevance judgments
   - Export for analysis in Jupyter/Python
    """)

def main():
    """Main setup flow"""
    print_header("MULTIMEDIA RETRIEVAL SYSTEM - DATABASE SETUP")
    
    print("""
Welcome to the Database Integration Guide!

This project evaluates two image retrieval methods:
  • Metadata-Based Retrieval (MBR)
  • Content-Based Image Retrieval (CBIR)

Your existing dataset will be migrated to a database for:
  ✅ Faster queries
  ✅ Better organization
  ✅ Research/evaluation tracking
  ✅ Easy experimentation
    """)
    
    # Check packages
    if not check_python_packages():
        print("\n❌ Please install missing packages first:")
        print("   pip install -r requirements.txt")
        return
    
    # Explain options
    explain_database_options()
    
    # Show setup info
    print("\n📌 Current Configuration: SQLite (config.py)")
    response = input("\nChange database? (SQLite/PostgreSQL/MySQL): ").strip().lower()
    
    if response in ['postgres', 'postgresql']:
        show_postgresql_setup()
    elif response in ['mysql', 'mariadb']:
        show_mysql_setup()
    else:
        show_sqlite_setup()
    
    # Run migration
    if run_migration():
        explain_search_methods()
        show_api_endpoints()
        show_next_steps()
        
        print_header("SETUP COMPLETE ✅")
        print("""
You're ready to start!

Run: python app.py

Then open: http://127.0.0.1:5000
        """)
    else:
        print("\n⚠️  Setup incomplete. Please fix the issues above and try again.")

if __name__ == '__main__':
    main()
