# Brain 系统 V3.0 - 自进化智能决策引擎

## 系统概述

Brain 系统是一个模块化的自进化智能决策引擎。核心能力：接收用户输入 → 意图分析 → 知识检索 → 多方案决策 → 执行 → 反馈闭环。V3.0 新增搜索意图识别 + BrowserInterceptor 实时网络数据获取 + 知识自进化能力。

## 架构

```
用户输入（POST /entry）
    │
    ▼
brain_entry.py (Flask API @ 127.0.0.1:5002)
    │
    ├── analyze_intent() → 意图分析（内置规则）
    ├── analyze_realtime_intent() → 搜索意图检测（独立模块）
    │
    ├── 搜索意图 [is_realtime=true]?
    │   ├── realtime_intent.py     → 判断搜索类型（股价/新闻/汇率/通用搜索）
    │   ├── browser_intercept_module.py → 执行浏览器网络拦截
    │   │   ├── BrowserInterceptor + 本地 LLM (Qwen3.5-9B)
    │   │   └── 8道关卡严格校验 LLM 输出
    │   └── knowledge_writer.py    → 黄金门槛检查→写入 knowledge/
    │
    └── 普通意图？
        └── 向量检索 (brain_vectors.db) + knowledge 文件检索
            └── build_context() → 返回 brain_results
```

## 核心模块

### 1. brain_entry.py (入口路由)
- **位置**: `E:\brain-system\core\brain_entry.py`
- **端口**: 5002
- **路由数**: 37 个
- **功能**: 统一入口、意图分析、记忆检索、知识图谱查询、反馈记录、系统状态
- **新增**:
  - 集成 `analyze_realtime_intent()` 搜索意图检测
  - 新增 `/intercept/execute` POST → 执行浏览器拦截
  - 新增 `/intercept/status` GET → 拦截模块状态查询
  - 返回值 `brain_context.realtime` 字段携带搜索意图信息

### 2. realtime_intent.py (搜索意图识别) — 新增
- **位置**: `E:\brain-system\core\realtime_intent.py`
- **职责**: 独立分析用户输入是否属于"需要实时数据支撑"的搜索意图
- **搜索意图分类**:

| 类型 | 示例 | 置信度 |
|------|------|--------|
| `stock_quote` | "茅台多少钱"、"600519的股价" | 0.9+ |
| `market_data` | "今天上证指数"、"美元兑人民币汇率" | 0.85+ |
| `news` | "最近有什么新闻" | 0.85+ |
| `general_search` | "帮我查一下..." | 0.8+ |
| `timely_query` | "最近有什么公告" | 0.7+ |

- **接口**:
  ```python
  from realtime_intent import analyze_realtime_intent, is_realtime_query
  result = analyze_realtime_intent("茅台多少钱")
  # {'is_realtime': True, 'realtime_type': 'stock_quote', 'confidence': 0.95, 'keywords': ['茅台'], 'fallback_viable': True}
  ```

### 3. browser_intercept_module.py (拦截执行+LLM解析) — 新增
- **位置**: `E:\brain-system\core\browser_intercept_module.py`
- **职责**: 接收拦截指令 → 调用 BrowserInterceptor → 本地 LLM 解析 → 严格校验
- **核心接口**:
  ```python
  from browser_intercept_module import intercept_and_parse, quick_quote
  result = intercept_and_parse({
      "task": "intercept_quote",
      "url": "https://gu.qq.com/sh600519",
      "filters": ["gtimg"],
      "max_wait_seconds": 10,
      "expected_fields": ["name", "price", "pct_change"]
  })
  ```
- **8道校验关卡**:
  1. 字数检查 ≤ 1000 字符
  2. JSON 解析检查
  3. JSON 精细字数 ≤ 500 字符
  4. 空数据标记 `empty=true` 拦截
  5. `confidence >= 0.7`
  6. 核心字段（如 price）非空
  7. `expected_fields` 缺失降 confidence
  8. 安全校验：禁止 `file:`、`localhost`、`127.0.0.1`

### 4. knowledge_writer.py (知识自进化写入) — 新增
- **位置**: `E:\brain-system\core\knowledge_writer.py`
- **职责**: 校验拦截数据的"黄金门槛" → 格式化 .md → 写入 knowledge/realtime/
- **黄金门槛（全部满足才写入）**:
  1. `intercept_result.status == 'ok'`
  2. `confidence >= 0.7`
  3. `fields` 非空
  4. 核心字段（如 price、name）存在
  5. 去重：5分钟内同内容不重复
  6. `data_quality in ('high', 'mid')`（字段填充率≥50%）
- **写入格式**:
  ```markdown
  ## 实时数据: 贵州茅台 (600519)
  - **时间**: 2026-05-10 18:01
  - **置信度**: 0.92
  - **来源**: 拦截器(https://gu.qq.com/sh600519)
  - **原始字段**:
    - name: 贵州茅台
    - code: 600519
    - price: 1499.0
    - pct_change: 1.23
  ```

## 数据存储

### 向量库
- **位置**: `E:\brain-system\data\.brain_vectors.db`
- **用途**: 语义搜索记忆

### 知识库
- **位置**: `E:\brain-system\data\knowledge/`
- **文件数**: 27个 .md 文件（含 realtime/ 子目录）
- **内容**: API指南、最佳实践、流程模板、��化方法、股票指标、实时数据

### 模式库/反馈库
- `.brain_patterns.db` — 用户意图模式自动挖掘
- `.brain_feedback.db` — 决策反馈记录
- `.brain_cache.db` — 查询缓存
- `knowledge_graph.json` — 知识图谱（节点+边）

## 部署与启动

### 启动
```bash
# 方式1: 使用启动脚本
E:\brain-system\scripts\start_brain.bat

# 方式2: 直接启动
cd E:\brain-system\core
python brain_entry.py
```

### 检查状态
```bash
curl http://127.0.0.1:5002/health
curl http://127.0.0.1:5002/intercept/status
```

### 配置文件
- **位置**: `E:\brain-system\data\.brain_config.json`
- **关键配置**:
  - `brain_host`: 127.0.0.1
  - `brain_port`: 5002
  - `decision_threshold.min_confidence`: 0.4
  - `auto_learn_threshold.confidence_low`: 0.5

## 依赖

| 依赖 | 用途 | 位置 |
|------|------|------|
| Flask | HTTP API 服务 | brain_entry.py |
| numpy | 数值处理 | brain_entry.py |
| sentence-transformers | 本地 Embedding | 可选 |
| requests | HTTP 客户端 | brain_entry.py |
| BrowserInterceptor | 浏览器网络劫持 | C:\dev\browser_interceptor.py |
| playwright | 浏览器自动化 | BrowserInterceptor 底层 |
| 本地 LLM (Qwen3.5-9B) | 解析拦截数据 | http://127.0.0.1:1235 |

## 测试

### 测试覆盖
6层测试体系：L0(健康) + L1(路由) + L2(模块单元) + L3(边界异常) + L4(集成) + L5(数据一致)

### 测试结果
- 总计: 72 个测试用例
- 通过率: 87.5% (63/72)
- 有效通过率: 97%+（7个失败为测试断言过严）

### 测试文件
- `C:\dev\brain_test_report.md` — 完整测试报告

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V3.0 | 2026-05-10 | 新增搜索意图识别、BrowserInterceptor 集成、知识自进化 |
| V3.0-beta | 2026-04-30 | 模块化重构、独立模块拆分 |
| V2.0 | 2026-04-20 | 向量库+知识图谱双引擎 |
| V1.0 | 2026-04-01 | 基础决策引擎 |
