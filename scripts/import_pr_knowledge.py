# -*- coding: utf-8 -*-
"""
导入GitHub PR Review最佳实践到Brain系统
"""
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

# 知识点
knowledge = [
    {
        "id": "pytorch_pr_review_sla",
        "content": "PR Review 24小时SLA规则: 如果请求变更，必须在作者更新后24小时内重新审查。无法承诺则只评论不阻塞。每日检查队列搜索is:open is:pr review-requested",
        "pattern": "workflow_sla",
        "source": "pytorch/pytorch wiki",
        "keywords": ["PR", "review", "SLA", "24小时", "workflow"],
    },
    {
        "id": "pr_security_pattern",
        "content": "PR安全审查Pattern: Never commit secrets (API_KEY, password, token must be masked). SQL Injection Check (use parameterized queries). Input validation (sanitize user input)",
        "pattern": "security_constraint",
        "source": "awesome-reviewers security",
        "keywords": ["security", "secrets", "SQL", "injection", "validation"],
    },
    {
        "id": "pr_performance_pattern",
        "content": "PR性能审查Pattern: Optimize memory access (avoid repeated allocation). Cache optimization (cache hot data). Lazy loading (defer large objects)",
        "pattern": "performance_optimization",
        "source": "awesome-reviewers performance",
        "keywords": ["performance", "memory", "cache", "lazy", "optimization"],
    },
    {
        "id": "knowledge_distillation_method",
        "content": "知识蒸馏方法: 从真实PR评论提取系统提示。每个prompt包含来源repo+出现次数+repo热度。通过验证循环确保实用性",
        "pattern": "knowledge_distillation",
        "source": "baz-scm/awesome-reviewers",
        "keywords": ["knowledge", "distillation", "PR", "prompt", "extraction"],
    },
    {
        "id": "api_design_pattern",
        "content": "API设计Pattern: Parameter validation (check type and range). Return type consistency (always return same structure). Error handling (use explicit error types)",
        "pattern": "api_design",
        "source": "awesome-reviewers api",
        "keywords": ["API", "design", "validation", "return", "error"],
    },
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 创建表（如果不存在）
c.execute('''CREATE TABLE IF NOT EXISTS embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash TEXT,
    content TEXT,
    source TEXT,
    pattern TEXT,
    keywords TEXT,
    created_at TEXT,
    UNIQUE(content_hash)
)''')

count = 0
for k in knowledge:
    content_hash = hashlib.md5(k["content"].encode()).hexdigest()
    
    try:
        c.execute('''INSERT INTO embeddings 
            (content_hash, content, source, pattern, keywords, created_at)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (content_hash, k["content"], k["source"], k["pattern"], 
             json.dumps(k["keywords"]), datetime.now().isoformat()))
        count += 1
        print(f"  导入: {k['id']}")
    except sqlite3.IntegrityError:
        print(f"  跳过: {k['id']} (已存在)")

conn.commit()

# 统计
c.execute("SELECT COUNT(*) FROM embeddings")
total = c.fetchone()[0]

c.execute("SELECT pattern, COUNT(*) FROM embeddings GROUP BY pattern")
patterns = c.fetchall()

conn.close()

print(f"\n导入完成: {count}条新增")
print(f"总embeddings: {total}条")
print("\nPattern分布:")
for p, cnt in patterns:
    print(f"  {p}: {cnt}条")

print("=" * 60)
print("下一步:")
print("  1. 运行向量导入脚本（build_vector_index.py）")
print("  2. 测试匹配效果")
print("=" * 60)