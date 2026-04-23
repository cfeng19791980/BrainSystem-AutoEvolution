# -*- coding: utf-8 -*-
"""
Awesome-Reviewers补充蒸馏 - 基于已有数据去重补充
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import sqlite3
import json
from datetime import datetime

DB_PATH = r"C:\Users\Administrator\.openclaw\brain-system\data\.brain_vectors.db"
LM_STUDIO_API = "http://127.0.0.1:1234/v1/embeddings"

print("=" * 60)
print("Awesome-Reviewers补充蒸馏")
print("=" * 60)

# 检查已有关键词，避免重复
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('SELECT content FROM embeddings WHERE source LIKE "%awesome%"')
existing = c.fetchall()
conn.close()

existing_keywords = set()
for content in existing:
    keyword = content[0].split(':')[0].lower()
    existing_keywords.add(keyword)

print(f"已有关键词: {existing_keywords}")

# 补充新pattern（去重）
new_patterns = [
    {
        "source": "andreisiteru/awesome-reviewers",
        "pattern": "PR代码质量审查Pattern: Code readability (meaningful names, clear logic). Function length (<50 lines preferred). DRY principle (avoid duplication). Comments quality (explain why not what).",
        "star": 8000,
        "category": "code_quality",
        "priority": "high"
    },
    {
        "source": "andreisiteru/awesome-reviewers",
        "pattern": "PR测试覆盖Pattern: Unit tests for new features. Edge cases coverage (null, empty, boundary). Integration tests for APIs. Test naming convention (describe_expected_behavior). Mock usage guidelines.",
        "star": 8000,
        "category": "test_coverage",
        "priority": "high"
    },
    {
        "source": "andreisiteru/awesome-reviewers",
        "pattern": "PR文档规范Pattern: README updates for new features. API documentation (parameters, returns, examples). Inline comments for complex logic. Changelog entry for user-facing changes.",
        "star": 8000,
        "category": "documentation",
        "priority": "medium"
    },
    {
        "source": "andreisiteru/awesome-reviewers",
        "pattern": "PR依赖管理Pattern: Dependency version pinning (avoid wildcards). Security audit (check known vulnerabilities). License compatibility (GPL caution). Minimal dependencies principle.",
        "star": 8000,
        "category": "dependency_management",
        "priority": "medium"
    },
    {
        "source": "andreisiteru/awesome-reviewers",
        "pattern": "PR可维护性Pattern: Modular design (single responsibility). Interface segregation (small interfaces). Configuration externalization (env vars, config files). Logging strategy (structured logs).",
        "star": 8000,
        "category": "maintainability",
        "priority": "high"
    },
    {
        "source": "andreisiteru/awesome-reviewers",
        "pattern": "PR错误处理Pattern: Explicit error types (don't use generic Exception). Error context preservation (stack trace, user message). Graceful degradation (fallback behavior). Error logging guidelines.",
        "star": 8000,
        "category": "error_handling",
        "priority": "high"
    },
]

print(f"\n待导入: {len(new_patterns)}条")

# 过滤已存在的
filtered = []
for p in new_patterns:
    keyword = p['pattern'].split(':')[0].lower()
    if keyword not in existing_keywords:
        filtered.append(p)
        print(f"  ✅ 新增: {p['category']}")
    else:
        print(f"  ⏭️ 跳过: {keyword}")

print(f"\n实际导入: {len(filtered)}条")

# 导入向量库
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

success = 0
failed = 0

for p in filtered:
    print(f"\n导入: {p['category']}")
    
    try:
        resp = requests.post(LM_STUDIO_API,
            json={"input": p['pattern'], "model": "nomic-embed-text"},
            timeout=30)
        
        if resp.status_code == 200:
            data = resp.json()
            if 'data' in data and len(data['data']) > 0:
                embedding = data['data'][0]['embedding']
                
                metadata = {
                    "source": p['source'],
                    "star": p['star'],
                    "category": p['category'],
                    "priority": p['priority'],
                    "authority": "awesome_reviewers",
                    "distillation": "补充蒸馏"
                }
                
                c.execute('''INSERT INTO embeddings 
                    (content, embedding, source, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (p['pattern'], json.dumps(embedding), p['source'],
                     json.dumps(metadata), datetime.now().isoformat(),
                     datetime.now().isoformat()))
                
                conn.commit()
                success += 1
                print(f"  ✅ 成功")
        else:
            failed += 1
            print(f"  ❌ API错误")
    except Exception as e:
        print(f"  ❌ {e}")
        failed += 1

conn.close()

print("\n" + "=" * 60)
print(f"完成: {success}成功, {failed}失败")
print("=" * 60)

# 统计
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM embeddings')
total = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM embeddings WHERE source LIKE "%awesome%"')
awesome_total = c.fetchone()[0]
conn.close()

print(f"总向量: {total}")
print(f"awesome-reviewers: {awesome_total}条")