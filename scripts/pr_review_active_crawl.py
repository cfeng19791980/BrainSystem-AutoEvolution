# -*- coding: utf-8 -*-
"""
PR Review Crawl - Active repos with comments
"""
import sqlite3
from pathlib import Path
import requests
import time

DATA_DIR = Path(r"C:\Users\Administrator\.openclaw\brain-system\data")
PR_DB = DATA_DIR / ".pr_review_kb.db"

# Active repos with many PR reviews
REPOS = [
    "pytorch/pytorch",
    "tensorflow/tensorflow",
    "langchain-ai/langchain",
    "microsoft/vscode",
]

print("=" * 60)
print("PR Review Crawl - Active Repos")
print("=" * 60)

conn = sqlite3.connect(str(PR_DB))
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS pr_review_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo TEXT, pr_number INTEGER, title TEXT, comment_type TEXT,
    comment_body TEXT, change_scope TEXT, best_practice TEXT,
    created_at TEXT, url TEXT
)''')
conn.commit()

headers = {'Accept': 'application/vnd.github.v3+json'}
total_comments = 0

for repo in REPOS:
    print(f"\n--- {repo} ---")
    try:
        # Get recent closed PRs
        url = f"https://api.github.com/repos/{repo}/pulls"
        params = {'state': 'closed', 'per_page': 5, 'sort': 'updated'}
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        pulls = resp.json()
        
        if not isinstance(pulls, list):
            print(f"  Error: Not a list")
            continue
        
        for pr in pulls[:5]:
            pr_number = pr['number']
            title = pr['title']
            pr_url = pr['html_url']
            created_at = pr['created_at']
            
            # Get PR review comments
            review_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"
            review_resp = requests.get(review_url, headers=headers, timeout=30)
            reviews = review_resp.json()
            
            if isinstance(reviews, list) and len(reviews) > 0:
                print(f"  PR #{pr_number}: {len(reviews)} review comments")
                
                for review in reviews[:3]:  # First 3 comments
                    body = review.get('body', '')[:300]
                    
                    # Classify comment
                    if 'suggestion' in body.lower():
                        comment_type = 'Suggestion'
                    elif 'review' in body.lower():
                        comment_type = 'Review'
                    elif 'fix' in body.lower() or 'bug' in body.lower():
                        comment_type = 'BugFix'
                    else:
                        comment_type = 'Comment'
                    
                    # Extract best practice
                    best_practice = ''
                    if 'should' in body.lower() or 'recommend' in body.lower():
                        idx = body.lower().find('should')
                        if idx == -1:
                            idx = body.lower().find('recommend')
                        best_practice = body[idx:idx+50] if idx >= 0 else ''
                    
                    cursor.execute('''INSERT INTO pr_review_entries 
                        (repo, pr_number, title, comment_type, comment_body, 
                         change_scope, best_practice, created_at, url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (repo, pr_number, title[:100], comment_type, body,
                         '', best_practice, created_at, pr_url))
                    
                    total_comments += 1
                
                conn.commit()
            else:
                print(f"  PR #{pr_number}: No reviews")
            
            time.sleep(0.5)  # Rate limit
        
        time.sleep(1)  # Rate limit between repos
        
    except Exception as e:
        print(f"  Error: {e}")

conn.close()
print(f"\nTotal PR comments: {total_comments}")
print("=" * 60)