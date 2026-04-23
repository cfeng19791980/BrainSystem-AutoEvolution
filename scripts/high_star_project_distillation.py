# -*- coding: utf-8 -*-
"""
五星项目知识蒸馏 - 从顶级项目提取PR Review Pattern
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
print("五星项目知识蒸馏")
print("=" * 60)

# 从抓取的内容提取核心Pattern
patterns = [
    # Vue.js Patterns
    {
        "source": "vuejs/core",
        "pattern": "Vue PR分类原则: Bug fix需clear reproduction, Feature需widely applicable use case. Chore合并多个小改动. 禁止纯stylistic refactor.",
        "star": 48000,
        "category": "pr_classification"
    },
    {
        "source": "vuejs/core",
        "pattern": "Vue性能权衡原则: Feature complexity vs benefit gained. 热路径优化优先, dev-only code放__DEV__分支, runtime比compiler敏感.",
        "star": 48000,
        "category": "performance_tradeoff"
    },
    {
        "source": "vuejs/core",
        "pattern": "Vue分支策略: Feature PR提交minor分支, Bug fix提交main分支. PR标题包含fix #issue编号. Commit message遵循约定生成changelog.",
        "star": 48000,
        "category": "branch_strategy"
    },
    
    # TypeScript Patterns
    {
        "source": "microsoft/typescript",
        "pattern": "TypeScript AI辅助披露: AI工具开发PR必须披露. 未披露AI-authored PR将被关闭. 重复违规视为disruptive conduct可能封禁.",
        "star": 101000,
        "category": "ai_transparency"
    },
    {
        "source": "microsoft/typescript",
        "pattern": "TypeScript Bug Report要求: 版本号(tsc --v), isolated reproduction, expected vs actual behavior. 搜索FAQ和closed issues避免重复.",
        "star": 101000,
        "category": "bug_report_quality"
    },
    {
        "source": "microsoft/typescript",
        "pattern": "TypeScript Feature贡献流程: 需issue approval(labelled help wanted)在Backlog milestone. 语言设计影响或外部工具满足的feature不接受.",
        "star": 101000,
        "category": "feature_approval"
    },
    
    # Node.js Patterns
    {
        "source": "nodejs/node",
        "pattern": "Node.js贡献范围: Code, documentation, answering questions, infrastructure, advocacy. 所有贡献都valued. Open governance, significant contributors成为Collaborators.",
        "star": 110000,
        "category": "contribution_scope"
    },
    {
        "source": "nodejs/node",
        "pattern": "Node.js DCO签名: Developer's Certificate of Origin必需. Sign-off表明有权提交, 理解公开记录永久保存. (a)原创 or (b)基于previous work or (c)他人提供.",
        "star": 110000,
        "category": "legal_signoff"
    },
    
    # React Patterns
    {
        "source": "facebook/react",
        "pattern": "React Semantic Versioning: Patch for critical bugfix, Minor for features, Major for breaking changes. Breaking changes提前minor引入deprecation warning.",
        "star": 230000,
        "category": "semantic_versioning"
    },
    {
        "source": "facebook/react",
        "pattern": "React Branch策略: 所有变更提交main. 不用dev/release分支. Main保持releasable状态. Feature flags控制breaking changes在ReactFeatureFlags.js.",
        "star": 230000,
        "category": "branch_policy"
    },
    {
        "source": "facebook/react",
        "pattern": "React Bug Report: Reduced test case (JSFiddle template), Security bugs通过Facebook bounty program. Discord community支持, filing issue前建议先read FAQ.",
        "star": 230000,
        "category": "bug_reporting"
    },
    
    # Rust Patterns
    {
        "source": "rust-lang/rust",
        "pattern": "Rust贡献引导: #new-members Zulip stream是最佳求助点. rustc-dev-guide必读before贡献. Submodule改动需针对对应repo, subtree优先PR到subtree repo.",
        "star": 100000,
        "category": "onboarding_guide"
    },
    {
        "source": "rust-lang/rust",
        "pattern": "Rust平台选择: Zulip推荐问问题, internals用于讨论. ICE report遵循contributing-bug-reports章节, issue template标准化错误报告.",
        "star": 100000,
        "category": "platform_selection"
    },
    
    # ThorVG Patterns
    {
        "source": "thorvg/thorvg",
        "pattern": "ThorVG Review原则: Core contributor PR无需self-review. External PR需CODEOWNER review. Review聚焦prevent mistakes, 非hinder development. Logical errors必须指出.",
        "star": 4000,
        "category": "review_hierarchy"
    },
    {
        "source": "thorvg/thorvg",
        "pattern": "ThorVG反馈克制: Unsure时不add feedback, observe and learn. Feedback/questions区分. Cleaner code建议欢迎, 但需visibly reduce complexity.",
        "star": 4000,
        "category": "feedback_discipline"
    },
    
    # Django Patterns
    {
        "source": "django/django",
        "pattern": "Django Trac必需: Non-trivial PR无Trac ticket将被关闭. File a ticket before PR. GitHub无adequate tooling, Trac track bugs/feature requests/patches.",
        "star": 80000,
        "category": "ticket_required"
    },
]

print(f"提取Pattern数: {len(patterns)}")

# 导入向量库
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

success = 0
failed = 0

for p in patterns:
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
                    "authority": "high_star_project",
                    "authority_level": "tier1" if p['star'] > 50000 else "tier2"
                }
                
                c.execute('''INSERT INTO embeddings 
                    (content, embedding, source, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (p['pattern'], json.dumps(embedding), p['source'],
                     json.dumps(metadata), datetime.now().isoformat(),
                     datetime.now().isoformat()))
                
                conn.commit()
                success += 1
                print(f"  ✅ 导入成功 (star={p['star']})")
            else:
                failed += 1
                print(f"  ❌ 无embedding数据")
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

# 验证
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM embeddings')
total = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM embeddings WHERE source LIKE "%vue%" OR source LIKE "%typescript%" OR source LIKE "%node%"')
new_count = c.fetchone()[0]
conn.close()

print(f"总向量数: {total}")
print(f"新增五星项目: {new_count}")

print("\n按项目统计:")
for project in ["vue", "typescript", "node", "react", "rust", "django"]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f'SELECT COUNT(*) FROM embeddings WHERE source LIKE "%{project}%"')
    count = c.fetchone()[0]
    conn.close()
    print(f"  {project}: {count}条")