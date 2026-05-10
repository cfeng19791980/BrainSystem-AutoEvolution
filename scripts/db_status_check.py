# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

DATA_DIR = Path(r"C:\Users\Administrator\.openclaw\brain-system\data")

print("=" * 60)
print("Database Status Check")
print("=" * 60)

# Issue KB
conn = sqlite3.connect(str(DATA_DIR / ".issue_kb.db"))
cursor = conn.cursor()
cursor.execute("SELECT repo, COUNT(*) FROM issue_entries GROUP BY repo")
print("\nIssues by repo:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")
cursor.execute("SELECT COUNT(*) FROM issue_entries")
total = cursor.fetchone()[0]
print(f"Total: {total}")
conn.close()

# Vector DB
conn = sqlite3.connect(str(DATA_DIR / ".brain_vectors.db"))
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM vectors")
print(f"\nVectors: {cursor.fetchone()[0]}")
conn.close()

# PR Review KB
conn = sqlite3.connect(str(DATA_DIR / ".pr_review_kb.db"))
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM pr_review_entries")
print(f"\nPR Reviews: {cursor.fetchone()[0]}")
conn.close()

# Evolution KB
conn = sqlite3.connect(str(DATA_DIR / ".evolution_kg.db"))
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM evolution_entries")
print(f"\nEvolution entries: {cursor.fetchone()[0]}")
conn.close()

# Patterns
conn = sqlite3.connect(str(DATA_DIR / ".brain_patterns.db"))
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM patterns")
print(f"\nPatterns: {cursor.fetchone()[0]}")
conn.close()

print("\n" + "=" * 60)