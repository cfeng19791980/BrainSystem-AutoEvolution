# -*- coding: utf-8 -*-
"""
Issue Batch Crawl - Expand to more repos
"""
import sqlite3
from pathlib import Path
import requests
import time

DATA_DIR = Path(r"C:\Users\Administrator\.openclaw\brain-system\data")
ISSUE_DB = DATA_DIR / ".issue_kb.db"

REPOS = [
    "explodinggradients/ragas",
    "langchain-ai/langchain",
    "run-llama/llama_index",
    "microsoft/typesense",
]

print("=" * 60)
print("Issue Batch Crawl")
print("=" * 60)

conn = sqlite3.connect(str(ISSUE_DB))
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS issue_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo TEXT, issue_number INTEGER, title TEXT, body TEXT,
    issue_type TEXT, state TEXT, created_at TEXT, url TEXT
)''')
conn.commit()

headers = {'Accept': 'application/vnd.github.v3+json'}
total_issues = 0

for repo in REPOS:
    print(f"\n--- {repo} ---")
    try:
        url = f"https://api.github.com/repos/{repo}/issues"
        params = {'state': 'closed', 'per_page': 10, 'sort': 'updated'}
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        data = resp.json()
        
        if isinstance(data, list):
            for issue in data[:10]:
                issue_number = issue['number']
                title = issue['title']
                body = (issue.get('body') or '')[:500]
                state = issue['state']
                created_at = issue['created_at']
                url_link = issue['html_url']
                
                if 'bug' in title.lower() or 'error' in title.lower():
                    issue_type = 'Bug'
                elif 'feature' in title.lower():
                    issue_type = 'Feature'
                else:
                    issue_type = 'Other'
                
                cursor.execute('''INSERT OR IGNORE INTO issue_entries 
                    (repo, issue_number, title, body, issue_type, state, created_at, url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (repo, issue_number, title[:200], body, issue_type, state, created_at, url_link))
                
                total_issues += 1
                print(f"  #{issue_number}: {title[:40]}... [{issue_type}]")
            
            conn.commit()
            time.sleep(1)  # Rate limit
        
    except Exception as e:
        print(f"  Error: {e}")

conn.close()
print(f"\nTotal crawled: {total_issues} issues")
print("=" * 60)