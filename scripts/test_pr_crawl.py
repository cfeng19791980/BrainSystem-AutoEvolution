# -*- coding: utf-8 -*-
"""
PR Review Crawl Test - Test crawl one repo
"""
import sys
sys.path.insert(0, r"C:\Users\Administrator\.openclaw\brain-system\core")

import sqlite3
from pathlib import Path
import requests

DATA_DIR = Path(r"C:\Users\Administrator\.openclaw\brain-system\data")
PR_DB = DATA_DIR / ".pr_review_kb.db"

print("=" * 60)
print("PR Review Crawl Test - ragas")
print("=" * 60)

# Initialize DB
conn = sqlite3.connect(str(PR_DB))
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS pr_review_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo TEXT, pr_number INTEGER, comment_type TEXT, change_scope TEXT,
    best_practice TEXT, created_at TEXT, url TEXT
)''')
conn.commit()

# Crawl ragas PRs (limit 3 for test)
repo = "explodinggradients/ragas"
url = f"https://api.github.com/repos/{repo}/pulls"
params = {'state': 'closed', 'per_page': 3, 'sort': 'updated'}
headers = {'Accept': 'application/vnd.github.v3+json'}

try:
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    pulls = resp.json()
    
    print(f"\nCrawled {len(pulls)} PRs from {repo}")
    
    for pr in pulls:
        pr_number = pr['number']
        title = pr['title']
        pr_url = pr['html_url']
        created_at = pr['created_at']
        
        # Get PR comments
        comments_url = pr['comments_url']
        comments_resp = requests.get(comments_url, headers=headers, timeout=30)
        comments = comments_resp.json()
        
        if comments:
            for comment in comments[:2]:  # First 2 comments per PR
                body = comment.get('body', '')[:300]
                
                # Classify comment type
                if 'review' in body.lower():
                    comment_type = 'Review'
                elif 'suggest' in body.lower():
                    comment_type = 'Suggestion'
                else:
                    comment_type = 'Comment'
                
                cursor.execute('''INSERT INTO pr_review_entries 
                    (repo, pr_number, comment_type, change_scope, best_practice, created_at, url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (repo, pr_number, comment_type, '', body[:100], created_at, pr_url))
                
                print(f"  PR #{pr_number}: {comment_type} - {body[:30]}...")
        else:
            print(f"  PR #{pr_number}: No comments")
    
    conn.commit()
    print("\n[PASS] PR Reviews saved to DB")
    
except Exception as e:
    print(f"[FAIL] Crawl error: {e}")

conn.close()
print("=" * 60)