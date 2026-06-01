"""
Migration script: Move data from CSV/NumPy to database
Run this ONCE to populate the database with existing dataset
"""
import os
import sys
import numpy as np
import pandas as pd
import json
from pathlib import Path
from flask import Flask
from models import db, Image, ImageFeature
from config import SQLALCHEMY_DATABASE_URI, SMALL_DATASET_PATH, FEATURES_PATH

# Setup Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def migrate_data():
    """
    Migrate existing CSV metadata and NumPy features to database
    """
    with app.app_context():
        print("\n" + "="*70)
        print("🔄 MIGRATING DATA TO DATABASE")
        print("="*70)
        
        # Create all tables
        print("\n1️⃣  Creating database tables...")
        db.create_all()
        print("   ✅ Tables created")
        
        # Check if already migrated
        existing_images = Image.query.count()
        if existing_images > 0:
            print(f"\n⚠️  Database already contains {existing_images} images!")
            response = input("   Delete and re-migrate? (y/n): ").strip().lower()
            if response == 'y':
                print("   🗑️  Clearing existing data...")
                ImageFeature.query.delete()
                Image.query.delete()
                db.session.commit()
                print("   ✅ Database cleared")
            else:
                print("   ❌ Migration cancelled")
                return
        
        # Load existing data
        print("\n2️⃣  Loading metadata from CSV...")
        metadata_csv = Path(__file__).parent / 'metadata.csv'
        
        if not metadata_csv.exists():
            print(f"   ❌ Error: metadata.csv not found at {metadata_csv}")
            return
        
        try:
            metadata_df = pd.read_csv(metadata_csv)
            print(f"   ✅ Loaded {len(metadata_df)} image records")
        except Exception as e:
            print(f"   ❌ Error reading CSV: {e}")
            return
        
        # Load feature vectors
        print("\n3️⃣  Loading feature vectors from NumPy...")
        features_file = FEATURES_PATH / 'features.npy'
        image_paths_file = FEATURES_PATH / 'image_paths.npy'
        
        if not features_file.exists() or not image_paths_file.exists():
            print(f"   ⚠️  Feature files not found - will proceed without features")
            print(f"      Features path: {features_file}")
            features = None
            image_paths = None
        else:
            try:
                features = np.load(features_file)
                image_paths = np.load(image_paths_file, allow_pickle=True)
                print(f"   ✅ Loaded {len(features)} feature vectors (dim: {features.shape[1]})")
            except Exception as e:
                print(f"   ⚠️  Error loading features: {e}")
                features = None
                image_paths = None
        
        # Insert images and features
        print("\n4️⃣  Inserting into database...")
        added_count = 0
        feature_count = 0
        duplicate_count = 0
        errors = []
        
        for idx, row in metadata_df.iterrows():
            try:
                # Check if image file exists
                category = row['category']
                image_name = row['image_name']
                full_file_path = os.path.join(SMALL_DATASET_PATH, category, image_name)
                
                if not os.path.exists(full_file_path):
                    errors.append(f"File not found: {full_file_path}")
                    continue
                
                # Store relative path for web serving (small_dataset/category/image.jpg)
                relative_path = f"small_dataset/{category}/{image_name}"
                
                # Check if image already exists (skip duplicates)
                existing = Image.query.filter_by(image_name=image_name).first()
                if existing:
                    duplicate_count += 1
                    continue
                
                # Create image record
                image = Image(
                    image_name=image_name,
                    file_path=relative_path,  # Store relative path for web serving
                    category=category,
                    keywords=row.get('keywords', ''),
                    file_size=os.path.getsize(full_file_path)
                )
                
                db.session.add(image)
                db.session.flush()  # Get the auto-generated ID
                
                # Add features if available
                if features is not None and idx < len(features):
                    feature_vec = features[idx]
                    feature_record = ImageFeature(
                        image_id=image.id,
                        features_json=json.dumps(feature_vec.tolist()),
                        extraction_method='color_histogram_512'
                    )
                    db.session.add(feature_record)
                    feature_count += 1
                
                added_count += 1
                
                # Progress indicator
                if (idx + 1) % 50 == 0:
                    print(f"   ... processed {idx + 1}/{len(metadata_df)} images")
                    db.session.commit()
            
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
                db.session.rollback()  # Rollback failed transaction
                print(f"   ❌ Error at row {idx}: {e}")
        
        # Final commit
        try:
            db.session.commit()
        except Exception as e:
            print(f"   ❌ Final commit failed: {e}")
            db.session.rollback()
            return
        
        # Summary
        print("\n" + "="*70)
        print("✅ MIGRATION COMPLETE")
        print("="*70)
        print(f"📊 Statistics:")
        print(f"   • Images added: {added_count}")
        print(f"   • Features added: {feature_count}")
        print(f"   • Duplicates skipped: {duplicate_count}")
        print(f"   • Errors: {len(errors)}")
        
        if errors:
            print(f"\n⚠️  Errors encountered:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"   - {error}")
            if len(errors) > 10:
                print(f"   ... and {len(errors) - 10} more errors")
        
        print("\n✅ Your database is ready! Dataset is now stored in the database.")
        print("   Run: python app.py")


if __name__ == '__main__':
    migrate_data()
