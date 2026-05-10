# -*- coding: utf-8 -*-
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(r"C:\Users\Administrator\.openclaw\brain-system\data")
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
VECTOR_DB = DATA_DIR / ".brain_vectors.db"

print("=" * 60)
print("Simple Vector Import")
print("=" * 60)

conn = sqlite3.connect(str(VECTOR_DB))
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS vectors (id INTEGER PRIMARY KEY, content TEXT, source TEXT, content_hash TEXT, created_at TEXT)")
conn.commit()
print("Vector DB initialized")

import_count = 0
md_files = list(KNOWLEDGE_DIR.glob("*.md"))

for md_file in md_files:
    try:
        content = md_file.read_text(encoding="utf-8")
        if len(content) < 50:
            continue
        content_hash = hashlib.md5(content.encode()).hexdigest()[:16]
        source = md_file.name
        cursor.execute("INSERT INTO vectors (content, source, content_hash, created_at) VALUES (?, ?, ?, ?)",
            (content[:8000], source, content_hash, datetime.now().isoformat()))
        import_count += 1
        print(f"  Imported: {source} ({len(content)} chars)")
    except Exception as e:
        print(f"  Error: {md_file.name} - {e}")

conn.commit()
conn.close()
print(f"\nTotal imported: {import_count} files")