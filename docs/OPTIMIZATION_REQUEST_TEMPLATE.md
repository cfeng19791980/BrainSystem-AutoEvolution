# GitHub Issue Training - Optimization Request Template (v2.0)

## Safety Constraint (Added 2026-04-23 16:19)

**用户约束**: 发现有用项目/Issue，先提交优化申请，经过审批后再执行代码优化。

**目的**: 防止恶意代码或自判断失误带来的风险。

---

## Optimization Request Template v2.0 (豆包方案增强版)

### Template ID: `OPT-REQ-XXX`

```markdown
# 优化申请单 OPT-REQ-XXX

## 1. Issue/项目来源

| 字段 | 内容 |
|------|------|
| Issue URL | https://github.com/XXX/XXX/issues/XXX |
| 项目名称 | XXX |
| Issue标题 | XXX |
| 发现时间 | 2026-XX-XX |

---

## 2. Issue分类标签 (豆包方案)

- [ ] **Bug** - 代码错误、异常、崩溃
- [ ] **功能需求** - 新功能、增强
- [ ] **边界用例** - 边界条件、极端输入
- [ ] **性能问题** - 响应慢、资源占用高
- [ ] **环境兼容** - 版本冲突、平台差异
- [ ] **安全漏洞** - 权限、注入、泄露
- [ ] **文档完善** - 文档缺失、说明不清

**标签判定依据**: `[在此说明为什么选择该标签]`

---

## 3. 核心要素抽取 (豆包方案)

| 要素 | 内容 |
|------|------|
| **报错栈** | `` (如有报错，粘贴关键报错栈) |
| **复现步骤** | 1. XXX 2. XXX 3. XXX |
| **触发条件** | XXX (什么情况下会触发) |
| **预期行为** | XXX (正确应该是什么行为) |
| **实际行为** | XXX (现在是什么行为) |

---

## 4. 模块适配判断 (豆包方案)

**是否命中BrainSystem模块**:

| 模块 | 是否命中 | 说明 |
|------|----------|------|
| 调度层 | [ ] | 核心调度逻辑 |
| 工具调用 | [ ] | Tool调用、参数解析 |
| Hook拦截 | [ ] | 钩子、拦截器 |
| 缓存层 | [ ] | Embedding缓存、结果缓存 |
| Embedding层 | [ ] | 向量计算、索引 |
| 知识图谱 | [ ] | KG构建、查询 |
| Gateway集成 | [ ] | API接口、决策 |
| 其他 | [ ] | 其他模块 |

---

## 5. 问题分析

**问题描述**:
- 核心问题是什么？
- 影响范围是什么？

**风险评估**:
- [ ] **低风险**：纯优化、注释、日志完善 → **自动放行**
- [ ] **中风险**：逻辑微调、参数阈值调整 → **简易审批**
- [ ] **高风险**：核心调度、架构改动、依赖变更 → **强人工终审**

---

## 6. 建议方案

**优化内容**:
- 添加什么功能？
- 修改什么模块？
- 影响什么文件？

**代码预览**:
```python
# 预览修改的代码片段
```

**收益预估**:
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| XXX | XX | XX | XX% |

---

## 7. 回归测试计划 (豆包方案)

**新增回归测试**: `test/regression/test_OPT_REQ_XXX.py`

| 测试项 | 方法 |
|------|------|
| 功能测试 | XXX |
| 边界测试 | XXX |
| 回归测试 | 自动跑run_regression.py |

---

## 8. 备份计划

| 备项 | 方案 |
|------|------|
| Git Branch | backup-before-OPT-REQ-XXX |
| File Backup | 相关文件.backup |
| DB Backup | 相关数据库.backup |

**回滚命令**:
```bash
git checkout backup-before-OPT-REQ-XXX
```

---

## 9. 等待审批 (按风险级别)

### 低风险 → 自动放行
- 状态: ✅ AUTO_APPROVED
- 执行: 自动执行，通知用户

### 中风险 → 简易审批
- 状态: 🔄 PENDING_QUICK
- 请用户确认: [ ] ✅ 同意 [ ] ❌ 拒绝

### 高风险 → 强人工终审
- 状态: 🔄 PENDING_FULL
- 请用户详细审查:
  - [ ] ✅ 执行优化
  - [ ] ❌ 拒绝优化
  - [ ] 🔄 需要更多信息

---
**申请时间**: 2026-XX-XX
**风险级别**: 低/中/高
**审批类型**: 自动/简易/强审
**申请者**: BrainSystem Self-Evolution Agent
**署名**: 付郁 (cfeng19791980, 10341731@qq.com)
```

---

## Approval Flow v2.0 (豆包方案增强)

```
发现Issue → 结构化分析 → 风险分级 → 按级别审批 → 执行优化 → 回归测试 → 记录结果
    ↓           ↓           ↓           ↓           ↓           ↓           ↓
  1.搜索     2.标签抽取   3.定级别   4.审批流程   5.实施修改   6.跑回归    7.Memory记录
```

---

## Risk Level & Approval Type (豆包方案)

| 级别 | 定义 | 审批类型 | 审批要求 |
|------|------|----------|----------|
| **低风险** | 注释优化、报错提示、文案、日志完善 | **自动放行** | 执行后通知用户 |
| **中风险** | 逻辑微调、参数阈值、缓存策略调整 | **简易审批** | 用户确认即可 |
| **高风险** | 核心调度、架构改动、依赖变更、Hook底层修改 | **强人工终审** | 用户详细审查后同意 |

---

## Regression Test Integration (豆包方案)

每次优化执行后，自动运行回归测试:

```python
# scripts/run_post_optimization_regression.py
from test.regression.run_regression import run_all_regression_tests

def post_optimization_check():
    results = run_all_regression_tests()
    if results["failed"] > 0:
        # Rollback automatically
        print("Regression failed! Rolling back...")
        return False
    return True
```

---

## Version Snapshot (豆包方案)

每次优化前记录快照:

```json
{
  "version": "v1.0.X",
  "snapshot_time": "2026-XX-XX",
  "modifications": [
    {"file": "XXX.py", "change": "Added XXX"}
  ],
  "issue_link": "https://github.com/XXX/issues/XXX",
  "performance_metrics": {
    "latency_ms": 5.2,
    "cache_hit_rate": 0.5,
    "error_rate": 0.01
  }
}
```

---

## Previous Training Records

| 申请单 | Issue | Pattern | 风险 | 结果 |
|--------|-------|---------|------|------|
| OPT-REQ-001 | typesense #1932 | embedding_auto_cache | 低 | ✅ PASS |
| OPT-REQ-002 | ragflow #8587 | graph_entity_linkage | 中 | ✅ PASS |
| OPT-REQ-003 | milvus #20687 | vector_result_cache | 低 | ✅ PASS |
| OPT-REQ-004 | csi10内部 | zz500_history_fetch | 低 | ✅ PASS |

---

## Constraint Enforcement Checklist

**每次发现有用Issue时**:

1. ✅ 填写优化申请单（OPT-REQ-XXX）
2. ✅ 添加Issue分类标签
3. ✅ 抽取核心要素（报错栈、复现步骤）
4. ✅ 判断模块适配
5. ✅ 评估风险级别（低/中/高）
6. ✅ 确定审批类型（自动/简易/强审）
7. ✅ 提供备份方案
8. ✅ 添加回归测试
9. ✅ 执行审批流程
10. ✅ 记录结果到Memory

---

**模板升级时间**: 2026-04-23 17:58
**升级来源**: 豆包方案建议
**版本**: v2.0
**署名**: 付郁 (cfeng19791980, 10341731@qq.com)