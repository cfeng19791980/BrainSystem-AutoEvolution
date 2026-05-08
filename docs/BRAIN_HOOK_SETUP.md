# Brain System + Brain Hook — OpenClaw 智能指令链路

## 概述

OpenClaw × Brain 系统打通了"本地记忆 → Brain 向量数据库 → 意图分析 → 标准规范指令注入"的完整链路。用户无需发送精确的工程指令，用自然语言模糊描述即可。

## 架构

```
用户 (自然语言模糊指令)
  ↓ openclaw-control-ui / Telegram / WhatsApp ...
Gateway (OpenClaw)
  ↓ before_prompt_build 事件
Brain Hook (插件)
  ↓ POST /entry (127.0.0.1:5002)
Brain Entry (Python Flask)
  ├── 意图分析 (LLM: lmstudio / qwen3-vl / glm5)
  ├── 本地记忆搜索 (embeddings: bge-m3 → 1024维)
  └── 构建标准规范指令 (目标/边界/参考案例/建议)
  ↓ return processed_content
Brain Hook
  ↓ inject appendSystemContext / prependContext / prependSystemContext
Gateway LLM
  → 看到 Brain 打包好的标准化指令 → 按流程执行
```

### 组件

| 组件 | 位置 | 端口 | 说明 |
|------|------|------|------|
| OpenClaw Gateway | `~/.openclaw/openclaw.json` | 18789 | 主消息路由器 |
| Brain Entry | `~/.openclaw/brain-system/core/brain_entry.py` | 5002 | 意图分析 + 向量搜索 |
| Brain Hook | `~/.openclaw/extensions/brain-hook/` | - | Gateway 插件 |
| LM Studio | `http://127.0.0.1:1234` | 1234 | bge-m3 embedding |
| 本地记忆 DB | `~/.openclaw/memory/main.sqlite` | - | OpenClaw chunks |
| Brain 向量库 | `~/.openclaw/brain-system/data/.brain_vectors.db` | - | ChromaDB 向量库 |
| 同步脚本 | `~/.openclaw/workspace/sync_memory_to_brain.py` | - | 增量同步 |
| 监控面板 | `~/Desktop/brain_monitor.bat` | - | 系统监控 |

## Brain Hook 安装与配置

### 文件结构

```
~/.openclaw/extensions/brain-hook/
├── index.js              # V9.3 插件主文件 (CommonJS)
├── openclaw.plugin.json  # 插件清单
└── package.json          # npm 包信息
```

### 安装步骤

```bash
# 1. 确保插件在 openclaw.json 的 allow 和 entries 中
openclaw config set plugins.entries.brain-hook.enabled true

# 2. 启用插件
openclaw plugins enable brain-hook

# 3. 重启 Gateway
openclaw gateway restart
```

### 工作流程 (before_prompt_build 事件)

1. Gateway 构建 prompt 前触发 `before_prompt_build` 事件
2. brain-hook 提取最后一条 `user` 角色消息
3. 长度 < 10 字符跳过（短消息不处理）
4. POST `{content: "..."}` 到 `http://127.0.0.1:5002/entry`（超时15秒）
5. Brain 返回 `{success, processed_content, brain_context: {intent, results}}`
6. brain-hook 注入 `prependSystemContext` + `appendSystemContext` + `prependContext`
7. Gateway LLM 看到 Brain 的标准化指令 + 原始指令

### 日志

brain-hook 写文件日志到 `~/.openclaw/logs/brain-hook.log`，同时在 Gateway 控制台输出 `[brain-hook]` 标签。

## Brain Entry 配置

### embedding 模型
使用 LM Studio 本地 bge-m3 模型（1024 维向量）：
```python
# brain_entry.py 中
openai_api_base = "http://127.0.0.1:1234/v1"
openai_model = "text-embedding-bge-reranker-v2-m3"
```

### 意图类型
Brain 返回的 `intent.type` 包括：
- `flow_check` — 检查/查看/诊断
- `flow_fix` — 修复/bug/改正
- `flow_test` — 测试/验证
- `flow_ask` — 提问/咨询
- `flow_operate` — 操作/执行
- `flow_explain` — 解释/分析
- ... 更多类型可自定义

## 记忆同步

### 同步脚本
`sync_memory_to_brain.py`：每小时的 cron job，将 OpenClaw 本地记忆增量同步到 Brain 向量库。

```bash
# cron job (cron ID: e4c9b4cd-...) 每小时执行
0 * * * *  # Asia/Shanghai
```

### 去重机制
- source 格式：`openclaw_memory:{source}:{chunk_id}:{content_hash[:12]}`
- 同步前查询 Brain stats 已有 source，跳过已同步内容
- Brain 的 `/import/batch` 无内置去重，由同步脚本自行处理

### OpenClaw compaction
配置在 `openclaw.json` 中：`agents.defaults.compaction.mode = "safeguard"`，`session.maintenance.pruneAfter = "6h"`。

## 关键技术决策

### 为什么用 before_prompt_build 而不是其他事件
- `message:received` — 太早，没有 session 上下文
- `before_dispatch` — 太晚，指令已经分派
- `before_prompt_build` — 恰好，可以修改 system prompt 和 messages
- return 格式：`{appendSystemContext: string}` 或 `{prependContext: string}`

### 为什么不用 Brain 主动 POST 回 Gateway
- 原方案 Brain 主动回调 Gateway 会增加耦合和复杂度
- Brain Hook 注入方式更轻量，Brain 只需处理好 `/entry` 端点

### 为什么用 CommonJS 而不是 ESM
- OpenClaw 新版插件加载器只支持 CommonJS（`require`/`module.exports`）
- `openclaw.plugin.json` 的 `activation.onStartup` 在新版中不直接生效，需通过 `openclaw plugins enable`

### Hook-only 与 Plugin 格式
- brain-hook 是 hook-only 插件（不注册 tools 或 channels）
- 需在 `installs.json` 中注册，且 `plugins.allow` 中列名
- `openclaw plugins enable` 是关键步骤（不是 install 就够的）

## 调试

### 常用命令

```bash
# 查看 hook 列表
openclaw hooks list

# 查看插件详情
openclaw plugins inspect brain-hook

# 检查插件加载问题
openclaw plugins doctor

# 刷新注册表
openclaw plugins registry --refresh

# 测试 Brain entry
curl -X POST http://127.0.0.1:5002/entry \
  -H "Content-Type: application/json" \
  -d '{"content": "今天股市大跌，帮我分析原因"}'

# 查看 Brain 状态
curl http://127.0.0.1:5002/health

# 查看向量库统计
curl http://127.0.0.1:5002/stats
```

### 日志文件

| 日志 | 路径 | 说明 |
|------|------|------|
| brain-hook | `~/.openclaw/logs/brain-hook.log` | 插件触发/注入 |
| Brain | `~/.openclaw/logs/brain_entry.out` | Brain API 调用记录 |
| Gateway | `~/.openclaw/logs/` | Gateway 启动/运行时 |
| 监控面板 | `~/Desktop/brain_monitor.bat` | 一键诊断 |

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| V9.0 | - | ESM 格式，sidecar 模式，只注入 intent type |
| V9.1 | - | 改为 CommonJS + sidecar |
| V10.0-V10.2 | - | 各种返回格式尝试 |
| **V9.3** | 2026-05-08 | **最终稳定版：sidecar + hook pack 折中方案** |

## Q&A

**Q: 用户发指令后没被加工怎么办？**
A: 查 brain-hook.log 看 `before_prompt_build triggered` 是否有输出。如果没有，说明插件未加载，运行 `openclaw plugins enable brain-hook` 后重启。

**Q: Brain 返回乱码怎么办？**
A: Brain 已经用 `ensure_ascii=False` 处理中文，检查 brain_entry.py 中 `/entry` 分支是否都用了 `np_jsonify()`。

**Q: 消息长度超过限制？**
A: brain-hook 截断到 80000 字符；Brain 的 `/entry` 对 `content` 有最小长��� 10 的校验。
