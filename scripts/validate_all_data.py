# -*- coding: utf-8 -*-
import requests

BASE_URL = "http://127.0.0.1:5002"

print("=" * 60)
print("API Endpoint Validation")
print("=" * 60)

# 1. dual-kb stats
resp = requests.get(f"{BASE_URL}/dual-kb/stats", timeout=5)
print(f"\n/dual-kb/stats:")
print(f"  {resp.json()}")

# 2. patterns/ready
resp = requests.get(f"{BASE_URL}/patterns/ready", timeout=5)
print(f"\n/patterns/ready:")
print(f"  {resp.json()}")

# 3. health
resp = requests.get(f"{BASE_URL}/health", timeout=5)
print(f"\n/health:")
health = resp.json()
print(f"  components: {list(health['components'].keys())[:5]}")

print("\n" + "=" * 60)
print("Database Content Summary")
print("=" * 60)

import sqlite3
from pathlib import Path

DATA_DIR = Path(r"C:\Users\Administrator\.openclaw\brain-system\data")

# PR Reviews content
conn = sqlite3.connect(str(DATA_DIR / ".pr_review_kb.db"))
cursor = conn.cursor()
cursor.execute("SELECT repo, pr_number, comment_type, comment_body FROM pr_review_entries")
print("\nPR Reviews (5 entries):")
for row in cursor.fetchall():
    print(f"  {row[0]} PR#{row[1]} [{row[2]}]: {row[3][:50]}...")
conn.close()

# Issues sample
conn = sqlite3.connect(str(DATA_DIR / ".issue_kb.db"))
cursor = conn.cursor()
cursor.execute("SELECT repo, issue_number, title, issue_type FROM issue_entries LIMIT 5")
print("\nIssues (sample 5):")
for row in cursor.fetchall():
    print(f"  {row[0]} #{row[1]} [{row[3]}]: {row[2][:40]}...")
conn.close()

print("\n" + "=" * 60)