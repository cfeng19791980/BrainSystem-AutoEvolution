# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

DB_PATH = r"C:\Users\Administrator\.openclaw\brain-system\data\.brain_vectors.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute('SELECT source, content FROM embeddings WHERE source LIKE "%awesome%"')
rows = c.fetchall()

conn.close()

print(f"现有awesome-reviewers数据: {len(rows)}条")
print("=" * 60)

for i, row in enumerate(rows):
    source = row[0]
    content = row[1]
    print(f"\n[{i+1}] {source}")
    print(f"    {content[:150]}...")
    
print("\n" + "=" * 60)
print(f"总计: {len(rows)}条")