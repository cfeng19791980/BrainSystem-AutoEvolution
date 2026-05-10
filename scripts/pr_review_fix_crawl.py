# -*- coding: utf-8 -*-
"""
Fix PR Review DB Schema and Crawl
"""
import sqlite3
from pathlib import Path
import requests

DATA_DIR = Path(r"C:\Users\Administrator\.openclaw\brain-system\data")
PR_DB = DATA_DIR / ".pr_review_kb.db"

print("=" * 60)
print("PR Review Crawl - Fix Schema + Active PRs")
print("=" * 60)

conn = sqlite3.connect(str(PR_DB))
cursor = conn.cursor()

# Drop and recreate with correct schema
cursor.execute("DROP TABLE IF EXISTS pr_review_entries")
cursor.execute('''CREATE TABLE pr_review_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo TEXT, pr_number INTEGER, title TEXT, comment_type TEXT,
    comment_body TEXT, change_scope TEXT, best_practice TEXT,
    created_at TEXT, url TEXT
)''')
conn.commit()
print("DB schema fixed")

headers = {'Accept': 'application/vnd.github.v3+json'}

# Target PRs with known reviews
TARGET_PRS = [
    ("tensorflow/tensorflow", 113),
    ("microsoft/vscode", 30210),
    ("pytorch/pytorch", 1520),
    ("langchain-ai/langchain", 36961),
]

total_comments = 0

for repo, pr_number in TARGET_PRS:
    print(f"\n--- {repo} PR #{pr_number} ---")
    try:
        # Get PR info
        pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
        pr_resp = requests.get(pr_url, headers=headers, timeout=30)
        pr_data = pr_resp.json()
        
        title = pr_data.get('title', '')[:100]
        created_at = pr_data.get('created_at', '')
        
        # Get review comments
        review_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"
        review_resp = requests.get(review_url, headers=headers, timeout=30)
        reviews = review_resp.json()
        
        if isinstance(reviews, list) and len(reviews) > 0:
            print(f"  Found {len(reviews)} review comments")
            
            for review in reviews[:5]:
                body = review.get('body', '')[:300]
                
                if len(body) < 10:
                    continue
                
                # Classify
                if 'suggestion' in body.lower():
                    comment_type = 'Suggestion'
                elif 'fix' in body.lower():
                    comment_type = 'BugFix'
                elif 'review' in body.lower():
                    comment_type = 'Review'
                else:
                    comment_type = 'Comment'
                
                # Extract best practice
                best_practice = ''
                for kw in ['should', 'recommend', 'better', 'please']:
                    if kw in body.lower():
                        idx = body.lower().find(kw)
                        best_practice = body[idx:idx+60]
                        break
                
                cursor.execute('''INSERT INTO pr_review_entries 
                    (repo, pr_number, title, comment_type, comment_body, 
                     best_practice, created_at, url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (repo, pr_number, title, comment_type, body,
                     best_practice, created_at, pr_url))
                
                total_comments += 1
                print(f"    [{comment_type}] {body[:40]}...")
            
            conn.commit()
        else:
            print(f"  No review comments")
            
    except Exception as e:
        print(f"  Error: {e}")

conn.close()
print(f"\nTotal saved: {total_comments} PR comments")
print("=" * 60)