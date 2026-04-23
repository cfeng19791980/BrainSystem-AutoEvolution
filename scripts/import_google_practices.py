# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
import json
from datetime import datetime

print("=" * 60)
print("Google Engineering Practices导入")
print("=" * 60)

DB_PATH = r"C:\Users\Administrator\.openclaw\brain-system\data\.brain_vectors.db"

knowledge = [
    ("Google Code Review核心原则: Reviewers should favor approving CL once it definitely improves overall code health, even if not perfect. No such thing as perfect code, only better code. Seek continuous improvement, not perfection.",
     "google/eng-practices", "google_core_principle"),
    
    ("Google Review审查清单: Design well-designed? Functionality behaves correctly? Complexity could be simpler? Tests correct and automated? Naming clear? Comments useful? Style follows guide? Documentation updated?",
     "google/eng-practices", "google_review_checklist"),
    
    ("Google Reviewer原则: Technical facts overrule opinions. Style guide is authority. Software design based on principles not preferences. If no rule applies, be consistent with codebase.",
     "google/eng-practices", "google_reviewer_principles"),
    
    ("Google CL大小原则: Small CLs reviewed faster. Break complex changes into smaller CLs. If need big refactoring, create new task. Long review = more changes + merge conflicts + demotivation.",
     "google/eng-practices", "google_cl_size"),
    
    ("Google冲突解决: First step: developer and reviewer try consensus. If difficult: face-to-face meeting or video call. Record discussion in comment. If unresolved: escalate to Tech Lead or Maintainer.",
     "google/eng-practices", "google_conflict_resolution"),
    
    ("Google Nit评论: Prefix non-critical comments with Nit: to indicate polish point author can ignore. Educational comments should be Nit unless critical to standards.",
     "google/eng-practices", "google_nit_comments"),
    
    ("Google最佳Reviewer: Find best reviewer who can respond in reasonable time. Best reviewer gives most thorough and correct review. Usually code owner. If unavailable, at least CC them.",
     "google/eng-practices", "google_best_reviewer"),
    
    ("Google Mentor功能: Code review teaches developers new language, framework, design principles. Sharing knowledge improves code health. Mark educational comments as Nit.",
     "google/eng-practices", "google_mentor_function"),
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

count = 0
for content, source, pattern in knowledge:
    metadata = json.dumps({"pattern": pattern, "source": source})
    
    try:
        c.execute('''INSERT INTO embeddings 
            (content, source, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)''',
            (content, source, metadata, datetime.now().isoformat(), datetime.now().isoformat()))
        count += 1
        print(f"  导入: {pattern}")
    except Exception as e:
        print(f"  跳过: {pattern} ({e})")

conn.commit()

c.execute("SELECT COUNT(*) FROM embeddings")
total = c.fetchone()[0]

conn.close()

print(f"\n导入完成: {count}条新增")
print(f"总embeddings: {total}条")
print("=" * 60)