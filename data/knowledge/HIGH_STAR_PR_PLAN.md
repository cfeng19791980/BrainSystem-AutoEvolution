# 高Star项目PR评论爬取计划

## Top高Star项目（PR评论质量高）

| 排名 | 项目 | Stars | 语言 | PR特点 | 优先级 |
|------|------|-------|------|--------|--------|
| 27 | **microsoft/vscode** | 184K | TypeScript | 架构决策详细 | ⭐⭐⭐ 已爬4条 |
| 50 | **vercel/next.js** | 139K | JavaScript | React框架设计 | ⭐⭐⭐ 待爬 |
| 56 | **golang/go** | 133K | Go | 语言设计讨论 | ⭐⭐⭐ 待爬 |
| - | **facebook/react** | 125K+ | JavaScript | UI框架设计 | ⭐⭐ 待爬 |
| - | **vuejs/vue** | 高 | TypeScript | 框架设计 | ⭐⭐ 待爬 |
| - | **pytorch/pytorch** | 高 | Python | 深度学习框架 | ⭐ 已爬wiki |
| - | **tensorflow/tensorflow** | 高 | Python | ML框架 | ⭐ 已爬1条 |

---

## 爬取策略

### 阶段1: 补充已爬项目

| 项目 | 已有 | 目标 | Gap |
|------|------|------|-----|
| **vscode** | 4条 | 30条 | +26 |
| **tensorflow** | 1条 | 20条 | +19 |

### 阶段2: 新增高Star项目

| 项目 | 目标 | 重点 |
|------|------|------|
| **next.js** | 30条 | React框架设计Pattern |
| **golang/go** | 20条 | 语言设计Pattern |
| **react** | 20条 | UI框架Pattern |

---

## 知识点预期

| Pattern类型 | 来源 | 预期 |
|-------------|------|------|
| **架构设计** | vscode, next.js | 20+ |
| **语言设计** | golang/go | 10+ |
| **UI框架** | react, vue | 15+ |
| **性能优化** | 各项目 | 15+ |
| **API设计** | 各项目 | 20+ |

**总预期**: 80+高质量Pattern

---

## 执行方式

由于GitHub API限速，采用替代方案：

### 方案A: Web页面抓取（当前）

```
web_fetch → 提取PR评论 → 蒸馏Pattern → 入库
```

### 方案B: 使用tavily_extract

```
tavily_extract(urls) → 提取内容 → 蒫馏
```

### 方案C: GitHub Token（需要用户提供）

```
带Token的API → 高限速 → 批量爬取
```

---

**计划时间**: 2026-04-23 22:42
**署名**: 付郁 (cfeng19791980)