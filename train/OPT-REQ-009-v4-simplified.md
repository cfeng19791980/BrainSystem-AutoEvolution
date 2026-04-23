# OPT-REQ-009-v4: 简化方案 - 利用现有存储优化筛选

## 用户洞察（关键）

**memory\engineer.sqlite 是 OpenClaw 自动生成的**

这说明：
- ✅ 系统本来就在存储会话记录
- ✅ 已有完整的分块+向量化+FTS机制
- ✅ 只需优化筛选，而非新建系统

---

## OpenClaw原生存储机制

| 数据库 | 大小 | 记录数 | 功能 |
|--------|------|--------|------|
| **engineer.sqlite** | 36MB | 658 chunks | 向量化存储 |
| **chunks_vec** | sqlite-vec | - | 向量搜索 |
| **chunks_fts** | FTS5 | 658 | 全文搜索 |
| **embedding_cache** | - | 1946 | 向量缓存 |

### Meta配置（系统元数据）

```json
{
  "model": "text-embedding-nomic-embed-text-v1.5@q6_k",
  "provider": "lmstudio",
  "chunkTokens": 400,
  "chunkOverlap": 80,
  "ftsTokenizer": "unicode61",
  "vectorDims": 768
}
```

### 数据流

```
memory/*.md → OpenClaw自动 → engineer.sqlite
                              ↓
                         chunks_vec（向量）
                         chunks_fts（FTS）
```

---

## 简化方案

### 原方案 vs 简化方案

| 项目 | 原方案 | 简化方案 |
|------|--------|----------|
| **新建数据库** | .session_screening.db | ❌ **删除** |
| **新建表** | screened_sessions | ❌ **不需要** |
| **采集机制** | 新建采集脚本 | ❌ **不需要** |
| **筛选逻辑** | 新建筛选系统 | ✅ **优化现有** |
| **改动范围** | 大重构 | **小步优化** |

---

## 实际优化方向

### 优化点：memory/*.md 写入前筛选

```python
# 现有流程
会话 → memory/*.md → engineer.sqlite（全量入库）

# 优化流程
会话 → 篮选(黑名单跳过+脱敏) → memory/*.md → engineer.sqlite（筛选入库）
```

### 具体改动

| 改动项 | 内容 |
|--------|------|
| **黑名单跳过** | 天气/闲聊等内容不写入memory |
| **脱敏规则** | API_KEY/密码/邮箱脱敏 |
| **重要性标记** | P0/P1/P2分级（可选） |

---

## 下一步建议

| 选项 | 说明 |
|------|------|
| **选项A** | 暂不改动，观察现有效果 |
| **选项B** | 在memory写入处添加黑名单过滤 |
| **选项C** | 添加脱敏规则 |

---

## Git记录

| Tag | 说明 |
|-----|------|
| `opt-req-009-phase1-4` | Phase 1-4完成（已删除） |
| `opt-req-009-complete` | 回归测试通过（已删除） |
| `opt-req-009-simplified` | 简化方案确认 |

---

## 总结

**用户洞察正确**：系统已有完整存储，只需优化筛选，无需新建系统。

**删除项**：
- ❌ .session_screening.db（冗余）
- ❌ session_screening.py（冗余）

**保留项**：
- ✅ engineer.sqlite（原生存储）
- ✅ 方案文档（记录思考过程）

---

**署名**: 付郁 (cfeng19791980, 10341731@qq.com)
**确认时间**: 2026-04-23 22:10