#!/usr/bin/env python3
"""
Reset database - DELETE old data and start fresh
"""
import os
from pathlib import Path

db_file = Path(__file__).parent / 'data' / 'multimedia.db'

print("\n" + "="*70)
print("🗑️  DATABASE CLEANUP")
print("="*70)

if db_file.exists():
    print(f"\nFound database: {db_file}")
    print(f"File size: {db_file.stat().st_size / 1024:.1f} KB")
    
    response = input("\n⚠️  Delete this database? (yes/no): ").strip().lower()
    
    if response == 'yes':
        try:
            os.remove(db_file)
            print(f"\n✅ Database deleted!")
            print("\nNext steps:")
            print("  1. python migrate_to_database.py  (migrate data)")
            print("  2. python app.py                   (start app)")
        except Exception as e:
            print(f"\n❌ Error deleting database: {e}")
    else:
        print("\n❌ Cancelled")
else:
    print(f"\n✅ No database file found: {db_file}")
    print("   Ready to create new database!")
    print("\nRun: python migrate_to_database.py")

print("\n" + "="*70)
