#!/usr/bin/env python3
"""
Quick install script for SQLite database integration
Installs only essential packages for your multimedia retrieval system
"""
import subprocess
import sys

print("\n" + "="*70)
print("🚀 Installing Database Dependencies (SQLite Edition)")
print("="*70 + "\n")

# Essential packages for SQLite database
packages = [
    "flask-sqlalchemy>=3.0",
    "sqlalchemy>=2.0",
    "flask>=3.1",
    "waitress",
    "python-dotenv",
    "numpy",
    "pandas",
    "pillow",
    "matplotlib",
    "scikit-learn"
]

for pkg in packages:
    print(f"📦 Installing {pkg}...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg], 
                      check=True, capture_output=True)
        print(f"   ✅ {pkg} installed\n")
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️  {pkg} installation had issues, continuing...\n")

print("="*70)
print("✅ Installation Complete!")
print("="*70)
print("\nNext steps:")
print("  1. python migrate_to_database.py  (migrate data)")
print("  2. python app.py                   (start app)")
print("\n")
