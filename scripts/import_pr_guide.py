# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
import json
from datetime import datetime

print("=" * 60)
print("PR Review Guide高质量知识导入")
print("=" * 60)

DB_PATH = r"C:\Users\Administrator\.openclaw\brain-system\data\.brain_vectors.db"

knowledge = [
    ("PR Review沟通原则: Always be respectful. Don't use imperative, don't judge, don't blame, don't be arrogant, don't use sarcasm. Instead: ask questions, explain your point of view, suggest improvements. Respect and humility remove all frictions.",
     "mawrkus/pull-request-review-guide", "communication_principle"),
    
    ("PR大小原则: Small successive PRs focused on single change are reviewed faster and more thoroughly. 10 lines = 10 issues, 500 lines = looks fine. Break complex task into simpler ones.",
     "mawrkus/pull-request-review-guide", "pr_size_best_practice"),
    
    ("Boy Scout规则: Leave this world a little better than you found it. Always look for opportunities to improve code: rename variables, split long functions, remove duplicates.",
     "mawrkus/pull-request-review-guide", "boy_scout_rule"),
    
    ("PR自我审查: First reviewer is you. Assess your own code before inviting others. Review changes outside IDE to spot inconsistencies, mistakes, missing parts.",
     "mawrkus/pull-request-review-guide", "self_review_practice"),
    
    ("PR评论回复原则: Stop reply hemorrhage. Many replies indicate miscommunication. Offer to talk in person. Post concise summary after conversation.",
     "mawrkus/pull-request-review-guide", "comment_reply_practice"),
    
    ("PR正向反馈: Offer encouragement and appreciation. Say thank you, great, nice when you learn something or see elegant code. Positive feedback makes huge difference.",
     "mawrkus/pull-request-review-guide", "positive_feedback_practice"),
    
    ("Coding Style自动化: Agree on coding style and use automation tools (formatters, linters). Remove personal tastes from review, focus on code quality.",
     "mawrkus/pull-request-review-guide", "coding_style_automation"),
    
    ("Reviewer同理心: Empathize. The other person is you. Avoid selective ownership. It's our code. Don't be gatekeeper. Improvements have threshold.",
     "mawrkus/pull-request-review-guide", "reviewer_empathy"),
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