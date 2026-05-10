# -*- coding: utf-8 -*-
"""
Initialize all dual KB + dual brain databases
"""
import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(r"C:\Users\Administrator\.openclaw\brain-system")
DATA_DIR = BASE_DIR / "data"
PATCHES_DIR = BASE_DIR / "patches"

DATA_DIR.mkdir(parents=True, exist_ok=True)
PATCHES_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Initializing Dual KB + Dual Brain Databases")
print("=" * 60)

# 1. Issue KB
print("\n[1] Creating Issue KB...")
issue_kb = DATA_DIR / ".issue_kb.db"
conn = sqlite3.connect(str(issue_kb))
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS issue_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo TEXT, issue_number INTEGER, title TEXT, body TEXT,
    issue_type TEXT, core_symptom TEXT, trigger_condition TEXT,
    risk_points TEXT, state TEXT, created_at TEXT, closed_at TEXT, url TEXT, embedding TEXT
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS issue_clusters (
    cluster_id INTEGER PRIMARY KEY, cluster_type TEXT, common_pattern TEXT, issue_ids TEXT, created_at TEXT
)''')
conn.commit()
conn.close()
print("[PASS] Issue KB created")

# 2. PR Review KB
print("\n[2] Creating PR Review KB...")
pr_kb = DATA_DIR / ".pr_review_kb.db"
conn = sqlite3.connect(str(pr_kb))
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS pr_review_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo TEXT, pr_number INTEGER, comment_type TEXT, change_scope TEXT,
    core_controversy TEXT, rejection_reason TEXT, best_practice TEXT,
    hard_constraint TEXT, created_at TEXT, url TEXT, embedding TEXT
)''')
conn.commit()
conn.close()
print("[PASS] PR Review KB created")

# 3. Discussion KB
print("\n[3] Creating Discussion KB...")
disc_kb = DATA_DIR / ".discussion_kb.db"
conn = sqlite3.connect(str(disc_kb))
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS discussion_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo TEXT, discussion_number INTEGER, title TEXT, body TEXT,
    category TEXT, author TEXT, created_at TEXT, url TEXT, design_decision TEXT, embedding TEXT
)''')
conn.commit()
conn.close()
print("[PASS] Discussion KB created")

# 4. Changelog KB
print("\n[4] Creating Changelog KB...")
cl_kb = DATA_DIR / ".changelog_kb.db"
conn = sqlite3.connect(str(cl_kb))
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS changelog_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo TEXT, version TEXT, release_date TEXT, changes TEXT,
    breaking_changes TEXT, architecture_changes TEXT, url TEXT, embedding TEXT
)''')
conn.commit()
conn.close()
print("[PASS] Changelog KB created")

# 5. Patch Registry
print("\n[5] Creating Patch Registry...")
patch_reg = DATA_DIR / "patch_registry.json"
registry = {"approved": [], "applied": [], "rejected": []}
with open(patch_reg, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)
print("[PASS] Patch Registry created")

# 6. Create sample patch
print("\n[6] Creating sample patch...")
sample_patch = PATCHES_DIR / "patch_sample_001.json"
patch_data = {
    "patch_id": "patch_sample_001",
    "created_at": "2026-04-23T18:26:00",
    "target_file": "core/opt_req_001_embedding_cache.py",
    "risk_level": "low",
    "status": "tested",
    "core_module": False
}
with open(sample_patch, "w", encoding="utf-8") as f:
    json.dump(patch_data, f, indent=2)
print("[PASS] Sample patch created")

print("\n" + "=" * 60)
print("All databases initialized successfully!")
print("=" * 60)