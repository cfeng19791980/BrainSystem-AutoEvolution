# GitHub PR Review最佳实践 - 蒸馏知识

## 来源1: PyTorch PR Review Etiquette

### 核心规则

| 规则 | 说明 |
|------|------|
| **24小时SLA** | 如果请求变更，必须在作者更新后24小时内重新审查 |
| **不阻塞原则** | 如果无法承诺24小时响应，只评论不请求变更 |
| **队列管理** | 使用搜索"is:open is:pr review-requested:$USERNAME"追踪待审PR |
| **每日检查** | 每天检查一次队列，重新审查所有有更新的PR |

### Pattern提取

```yaml
Pattern_ID: pr_review_sla
Category: workflow
Rules:
  - request_changes → must_re_review_within_24h
  - cant_commit → leave_comments_only
  - track_queue → search_filter + daily_check
Impact: 保持PR流程高效，避免阻塞
```

---

## 来源2: Awesome Reviewers (8000+真实PR评论蒸馏)

### 核心特性

| 特性 | 说明 |
|------|------|
| **8K+ Prompts** | 从真实PR评论提取的系统提示 |
| **真实OSS洞察** | 每个reviewer包含来源repo + 出现次数 + repo热度 |
| **一键部署** | 可直接粘贴到VS Code/Cursor/Claude |
| **验证循环** | 通过maintainer反馈验证prompts |

### Pattern类型分布

| Category | 示例 |
|----------|------|
| **Security** | Never commit secrets, SQL Injection Check |
| **Performance** | Optimize memory access, Cache optimization |
| **Documentation** | Documentation consistency standards |
| **Testing** | Unit test coverage, Integration test patterns |
| **API Design** | Parameter validation, Return type consistency |

---

## Brain系统导入方案

### 知识点提取

```yaml
Knowledge_001:
  ID: pytorch_pr_review_sla
  Title: PyTorch PR Review 24小时SLA规则
  Content: |
    如果你请求变更，必须24小时内重新审查。
    无法承诺则只评论不阻塞。
    每日检查队列"is:open is:pr review-requested:$USERNAME"
  Pattern: workflow_sla
  Source: pytorch/pytorch wiki
  Confidence: 95%

Knowledge_002:
  ID: awesome_reviewers_methodology
  Title: Awesome Reviewers提取方法论
  Content: |
    从8000+真实PR评论提取系统提示。
    每个prompt包含: 来源repo + 出现次数 + repo热度。
    通过验证循环确保实用性。
  Pattern: knowledge_distillation
  Source: baz-scm/awesome-reviewers
  Confidence: 90%

Knowledge_003:
  ID: pr_review_security_pattern
  Title: PR安全审查Pattern
  Content: |
    Never commit secrets (API_KEY, password, token)
    SQL Injection Check (参数化查询)
    Input validation (sanitize user input)
  Pattern: security_constraint
  Source: awesome-reviewers security category
  Confidence: 95%

Knowledge_004:
  ID: pr_review_performance_pattern
  Title: PR性能审查Pattern
  Content: |
    Optimize memory access (避免重复分配)
    Cache optimization (缓存热点数据)
    Lazy loading (延迟加载大对象)
  Pattern: performance_optimization
  Source: awesome-reviewers performance category
  Confidence: 90%
```

---

## 导入脚本

```python
# 导入到.brain_vectors.db
import sqlite3
import json

DB_PATH = "data/.brain_vectors.db"
knowledge = [
    {
        "id": "pytorch_pr_review_sla",
        "content": "PR Review 24小时SLA规则...",
        "pattern": "workflow_sla",
        "source": "pytorch/wiki",
    },
    ...
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for k in knowledge:
    c.execute('''INSERT INTO embeddings 
        (content, source, pattern, created_at)
        VALUES (?, ?, ?, ?)''',
        (k["content"], k["source"], k["pattern"], datetime.now()))
    
conn.commit()
```

---

## 预期效果

| 维度 | 当前 | 导入后 |
|------|------|--------|
| **embeddings数** | 77条 | +4条=81条 |
| **Pattern覆盖** | workflow缺失 | ✅ 补充 |
| **Security知识** | 基础 | ✅ 增强 |
| **Performance知识** | 基础 | ✅ 增强 |

---

## 下一步

1. 运行导入脚本 → 向量化
2. brain_entry.py自动匹配新知识
3. 测试匹配效果（PR review类指令）

---

**爬取时间**: 2026-04-23 22:37
**来源**: PyTorch Wiki + Awesome Reviewers
**署名**: 付郁 (cfeng19791980)