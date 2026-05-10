# -*- coding: utf-8 -*-
"""
Issue Crawl Test - Test crawl one repo
"""
import sys
sys.path.insert(0, r"C:\Users\Administrator\.openclaw\brain-system\core")

import sqlite3
from pathlib import Path
from datetime import datetime
import requests

DATA_DIR = Path(r"C:\Users\Administrator\.openclaw\brain-system\data")
ISSUE_DB = DATA_DIR / ".issue_kb.db"

print("=" * 60)
print("Issue Crawl Test - ragas")
print("=" * 60)

# Initialize DB
conn = sqlite3.connect(str(ISSUE_DB))
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS issue_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo TEXT, issue_number INTEGER, title TEXT, body TEXT,
    issue_type TEXT, core_symptom TEXT, state TEXT, created_at TEXT, url TEXT
)''')
conn.commit()

# Crawl ragas issues (limit 5 for test)
repo = "explodinggradients/ragas"
url = f"https://api.github.com/repos/{repo}/issues"
params = {'state': 'closed', 'per_page': 5, 'sort': 'updated'}
headers = {'Accept': 'application/vnd.github.v3+json'}

try:
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    data = resp.json()
    
    print(f"\nCrawled {len(data)} issues from {repo}")
    
    for issue in data:
        issue_number = issue['number']
        title = issue['title']
        body = issue.get('body', '') or ''
        state = issue['state']
        created_at = issue['created_at']
        url_link = issue['html_url']
        
        # Classify type
        if 'bug' in title.lower() or 'error' in title.lower():
            issue_type = 'Bug'
        elif 'feature' in title.lower():
            issue_type = 'Feature'
        else:
            issue_type = 'Other'
        
        cursor.execute('''INSERT INTO issue_entries 
            (repo, issue_number, title, body, issue_type, state, created_at, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (repo, issue_number, title[:200], body[:500], issue_type, state, created_at, url_link))
        
        print(f"  Issue #{issue_number}: {title[:50]}... [{issue_type}]")
    
    conn.commit()
    print("\n[PASS] Issues saved to DB")
    
except Exception as e:
    print(f"[FAIL] Crawl error: {e}")

conn.close()
print("=" * 60)