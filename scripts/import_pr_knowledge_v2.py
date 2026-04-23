# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
import json
import hashlib
from datetime import datetime

print("=" * 60)
print("GitHub PR知识导入Brain系统")
print("=" * 60)

DB_PATH = r"C:\Users\Administrator\.openclaw\brain-system\data\.brain_vectors.db"

knowledge = [
    ("PR Review 24小时SLA规则: 如果请求变更，必须在作者更新后24小时内重新审查。无法承诺则只评论不阻塞。每日检查队列搜索is:open is:pr review-requested",
     "pytorch/wiki", "workflow_sla"),
    ("PR安全审查Pattern: Never commit secrets (API_KEY, password, token must be masked). SQL Injection Check (use parameterized queries). Input validation (sanitize user input)",
     "awesome-reviewers/security", "security_constraint"),
    ("PR性能审查Pattern: Optimize memory access (avoid repeated allocation). Cache optimization (cache hot data). Lazy loading (defer large objects)",
     "awesome-reviewers/performance", "performance_optimization"),
    ("知识蒸馏方法: 从真实PR评论提取系统提示。每个prompt包含来源repo+出现次数+repo热度。通过验证循环确保实用性",
     "baz-scm/awesome-reviewers", "knowledge_distillation"),
    ("API设计Pattern: Parameter validation (check type and range). Return type consistency (always return same structure). Error handling (use explicit error types)",
     "awesome-reviewers/api", "api_design"),
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

count = 0
for content, source, pattern in knowledge:
    content_hash = hashlib.md5(content.encode()).hexdigest()
    metadata = json.dumps({"pattern": pattern, "keywords": source.split("/")})
    
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