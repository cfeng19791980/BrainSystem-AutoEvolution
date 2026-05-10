# -*- coding: utf-8 -*-
"""
Brain System Database Stats Check
"""
import sqlite3
from pathlib import Path

DATA_DIR = Path(r"C:\Users\Administrator\.openclaw\brain-system\data")

print("=" * 60)
print("Brain System Database Stats")
print("=" * 60)

db_files = [
    ".brain_vectors.db",
    ".brain_patterns.db",
    ".brain_kb.db",
    ".brain_cache.db",
    ".brain_feedback.db",
    ".evolution_kg.db",
    ".issue_kb.db",
    ".pr_review_kb.db",
    ".discussion_kb.db",
    ".changelog_kb.db",
]

total_records = 0

for db_file in db_files:
    db_path = DATA_DIR / db_file
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        
        db_records = 0
        for table in tables:
            if table != 'sqlite_sequence':
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                db_records += count
        
        total_records += db_records
        size_kb = db_path.stat().st_size / 1024
        
        print(f"\n{db_file}")
        print(f"  Tables: {len(tables)}")
        print(f"  Records: {db_records}")
        print(f"  Size: {size_kb:.1f} KB")
        
        conn.close()
    else:
        print(f"\n{db_file}: NOT FOUND")

print("\n" + "=" * 60)
print(f"Total Records: {total_records}")
print(f"Total DB Files: {len(db_files)}")
print("=" * 60)