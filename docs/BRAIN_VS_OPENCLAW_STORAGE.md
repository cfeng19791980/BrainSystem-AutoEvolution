# Brain系统 vs OpenClaw核心 存储对比

## 发现：两个独立系统

| 系统 | 向量库 | 记录数 | 来源 | 调用者 |
|------|--------|--------|------|--------|
| **BrainSystem（插件）** | .brain_vectors.db | 77条(embeddings) | knowledge/*.md | brain_entry.py |
| **OpenClaw核心** | engineer.sqlite | 661条(chunks) | memory/*.md | Gateway |

---

## Brain系统数据库详情

| 数据库 | 大小 | 表 | 记录数 |
|--------|------|------|--------|
| .brain_vectors.db | 2MB | embeddings | **77条** |
| .brain_feedback.db | 135KB | feedback | 368条 |
| .brain_patterns.db | 12KB | patterns | 2条 |
| .brain_kb.db | 20KB | kb | 4条 |
| .brain_cache.db | 24KB | cache | 2条 |

---

## 数据流向

### BrainSystem（插件层）

```
knowledge/*.md → brain_entry.py → .brain_vectors.db
                                      ↓
                              embeddings表（77条）
                              vec0虚拟表（sqlite-vec）
```

### OpenClaw核心（系统层）

```
memory/*.md → Gateway → engineer.sqlite
                          ↓
                    chunks表（661条）
                    chunks_vec（sqlite-vec）
                    chunks_fts（FTS5）
```

---

## 关键区别

| 维度 | BrainSystem | OpenClaw核心 |
|------|-------------|--------------|
| **位置** | brain-system/data | memory |
| **调用者** | brain_entry.py（插件） | Gateway（核心） |
| **内容** | 知识库、流程模板 | 会话记录 |
| **维度** | 知识向量 | 会话向量 |
| **入库触发** | 手动导入/爬取 | 自动（会话结束） |

---

## OPT-REQ-009的正确范围

| 问题 | 答案 |
|------|------|
| **Brain系统需要会话筛选吗？** | ❌ 不需要，它存储的是知识库 |
| **Brain系统有会话记录吗？** | ❌ 没有，只有feedback(368条) |
| **OpenClaw核心有会话记录吗？** | ✅ 有，engineer.sqlite(661条) |
| **筛选应该在哪里做？** | ✅ OpenClaw核心（Gateway层） |

---

## 结论

**用户的洞察仍然正确，但范围需要修正：**

- **BrainSystem** = 知识库系统（不存储会话）
- **OpenClaw核心** = 会话存储系统（已有筛选入库）

**OPT-REQ-009不需要实施，因为：**
1. Brain系统只存储知识库，不存储会话
2. OpenClaw核心已有完整会话存储机制
3. 两个系统独立运行，各司其职

---

## 可选优化（如果需要）

| 优化点 | 系统 | 改动位置 |
|--------|------|----------|
| **会话筛选** | OpenClaw核心 | Gateway配置 |
| **知识筛选** | BrainSystem | brain_entry.py |

**建议：观察现效果，暂不改动**

---

**分析时间**: 2026-04-23 22:13
**署名**: 付郁 (cfeng19791980)