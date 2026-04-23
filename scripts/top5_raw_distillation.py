# -*- coding: utf-8 -*-
"""
Top 5 五星项目Raw原始文件高质量蒸馏
只提取规则、模式、最佳实践，去重、精简、不冗余
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
print("Top 5 五星项目Raw原始文件高质量蒸馏")
print("=" * 60)

# 检查已有pattern，避免重复
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''SELECT source, content FROM embeddings 
    WHERE source IN ("facebook/react", "nodejs/node", "microsoft/typescript", 
                    "rust-lang/rust", "django/django")''')
existing = c.fetchall()
conn.close()

existing_keywords = set()
for source, content in existing:
    # 提取关键词避免重复
    keywords = content.split(':')[0] if ':' in content else content[:30]
    existing_keywords.add(keywords.lower())

print(f"已有pattern关键词: {len(existing_keywords)}个")
print(f"避免重复关键词: {list(existing_keywords)[:10]}...")

# Top 5项目核心规则（去重后新增）
new_patterns = [
    # React (230K) - 已有3条，补充2条新规则
    {
        "source": "facebook/react",
        "pattern": "React PR Checklist: Run yarn test, yarn prettier, yarn lint, yarn flow. Tests must pass before submit. Commit messages follow convention for changelog generation.",
        "star": 230000,
        "category": "pr_checklist",
        "priority": "high"
    },
    {
        "source": "facebook/react",
        "pattern": "React CLA Requirement: Submit CLA once for all Facebook projects. First-time PR must complete CLA and cross-check GitHub username. https://code.facebook.com/cla",
        "star": 230000,
        "category": "legal_requirement",
        "priority": "high"
    },
    
    # Node.js (110K) - 已有2条，补充3条新规则
    {
        "source": "nodejs/node",
        "pattern": "Node.js PR Guidelines: Dependencies changes need approval. Local environment setup required. Review process detailed in doc/contributing/pull-requests.md.",
        "star": 110000,
        "category": "pr_process",
        "priority": "high"
    },
    {
        "source": "nodejs/node",
        "pattern": "Node.js Issue Triaging: Use GitHub Issues for public bugs. Before filing, search existing issues (including closed). Security bugs go through private process.",
        "star": 110000,
        "category": "issue_triage",
        "priority": "medium"
    },
    {
        "source": "nodejs/node",
        "pattern": "Node.js Governance: Open governance model. Significant contributors become Collaborators with commit-access. See GOVERNANCE.md for details.",
        "star": 110000,
        "category": "governance",
        "priority": "medium"
    },
    
    # TypeScript (101K) - 已有3条，补充2条新规则
    {
        "source": "microsoft/typescript",
        "pattern": "TypeScript Coding Agent Rule: All code changes submit to typescript-go repo. Current repo winding down. PRs only merged for critical 6.0 issues. SECURITY issues accepted.",
        "star": 101000,
        "category": "repo_migration",
        "priority": "high"
    },
    {
        "source": "microsoft/typescript",
        "pattern": "TypeScript Automated Comments: Repo configured with automation. Automated PR/issue summaries NOT allowed. Violation results in immediate block for inauthentic activity.",
        "star": 101000,
        "category": "automation_policy",
        "priority": "high"
    },
    
    # Rust (100K) - 已有2条，补充2条新规则
    {
        "source": "rust-lang/rust",
        "pattern": "Rust Submodule Rule: Changes to submodules must target corresponding repo, NOT main rust-lang/rust. Subtrees prefer PR to subtree repo unless compiler change required.",
        "star": 100000,
        "category": "submodule_policy",
        "priority": "high"
    },
    {
        "source": "rust-lang/rust",
        "pattern": "Rust ICE Report: Compiler error pointing to CONTRIBUTING.md? Create ICE report following contributing-bug-reports section. Use issue template for standardized reports.",
        "star": 100000,
        "category": "error_reporting",
        "priority": "medium"
    },
    
    # Django (80K) - 已有1条，补充3条新规则
    {
        "source": "django/django",
        "pattern": "Django Contribution Types: Code patches, documentation improvements, bug reports, patch reviews. All contributions welcome regardless of size.",
        "star": 80000,
        "category": "contribution_scope",
        "priority": "medium"
    },
    {
        "source": "django/django",
        "pattern": "Django Documentation: Extensive contributing guidelines in docs/internals/contributing/ or online at docs.djangoproject.com/en/dev/internals/contributing/",
        "star": 80000,
        "category": "documentation_location",
        "priority": "low"
    },
    {
        "source": "django/django",
        "pattern": "Django Code of Conduct: Contributors must keep community open and inclusive. Read and follow Code of Conduct at djangoproject.com/conduct/",
        "star": 80000,
        "category": "community_standards",
        "priority": "medium"
    },
]

print(f"\n待导入pattern数: {len(new_patterns)}条")

# 过滤已存在的pattern
filtered_patterns = []
for p in new_patterns:
    keyword = p['pattern'].split(':')[0].lower()
    if keyword not in existing_keywords:
        filtered_patterns.append(p)
        print(f"  ✅ 新增: {p['source']} - {p['category']}")
    else:
        print(f"  ⏭️ 跳过(已存在): {keyword}")

print(f"\n实际导入: {len(filtered_patterns)}条 (去重后)")

# 导入向量库
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

success = 0
failed = 0

for p in filtered_patterns:
    print(f"\n处理: {p['source']} - {p['category']}")
    print(f"  Pattern: {p['pattern'][:60]}...")
    
    # 获取embedding
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
                    "authority": "tier1_top5",
                    "distillation_method": "raw_file_high_quality"
                }
                
                c.execute('''INSERT INTO embeddings 
                    (content, embedding, source, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (p['pattern'], json.dumps(embedding), p['source'],
                     json.dumps(metadata), datetime.now().isoformat(),
                     datetime.now().isoformat()))
                
                conn.commit()
                success += 1
                print(f"  ✅ 导入成功")
            else:
                failed += 1
        else:
            failed += 1
            print(f"  ❌ API错误: {resp.status_code}")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        failed += 1

conn.close()

print("\n" + "=" * 60)
print(f"导入完成: {success}成功, {failed}失败")
print("=" * 60)

# 统计
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM embeddings')
total = c.fetchone()[0]

for project in ["react", "node", "typescript", "rust", "django"]:
    c.execute(f'SELECT COUNT(*) FROM embeddings WHERE source LIKE "%{project}%"')
    count = c.fetchone()[0]
    print(f"  {project}: {count}条")

conn.close()

print(f"\n总向量数: {total}")