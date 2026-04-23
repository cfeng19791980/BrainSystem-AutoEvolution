# Brain V4工具集成设计

## 目标
让Brain能够调用非破坏性工具，扩展知识获取能力

## 可用工具（安全级别）

### ✅ 允许调用（无破坏性）
1. **web_search / tavily_search** - 搜索外部知识
2. **browser.snapshot** - 截图查看页面
3. **browser.open** - 打开网页（只读）
4. **wiki_get/wiki_search** - 查询Wiki知识
5. **memory_search** - 搜索内部记忆
6. **web_fetch** - 获取网页内容

### ❌ 禁止调用（有破坏性）
1. **exec** - 执行命令
2. **edit/write** - 修改文件
3. **browser.act** - 操作页面元素
4. **gateway.restart** - 重启系统

## 工具调用流程

```
用户消息 → Brain Hook → 识别意图 → 选择工具 → 调用工具 → 返回结果
```

## 意图-工具映射

| 意图 | 工具 | 示例 |
|------|------|------|
| `search` | web_search / tavily_search | "brain 搜索最新AI新闻" |
| `browse` | browser.open + snapshot | "brain 打开GitHub项目页" |
| `fetch` | web_fetch | "brain 获取文档内容" |
| `wiki` | wiki_search | "brain 查询React知识" |
| `query` | memory_search (现有) | "brain python教程" |

## 实现方案

### 方案1: Brain API调用工具
- Brain API内部调用工具API
- 需要导入工具SDK
- 复杂度高

### 方案2: Hook返回工具指令
- Brain返回 `{ tool: "web_search", params: {...} }`
- OpenClaw执行工具调用
- Brain第二次Hook接收工具结果
- 更安全，由OpenClaw控制

### 方案3: 混合方案
- 知识库查询：直接返回
- 需要外部工具：返回提示 + 工具建议
- 用户确认后，Agent调用工具

## 推荐方案：方案3（最安全）

Brain返回：
```markdown
🧠 Brain已接收请求

📚 内部知识：找到5条结果...

🔍 **建议使用外部工具**:
- `web_search`: 搜索GitHub最新热门项目
- `browser.open`: 打开项目页面查看详情

是否需要我调用这些工具？
```

用户回复"是"后，Agent调用工具，Brain第二次处理结果。

## 下一步
1. 实现工具意图识别
2. 设计工具调用格式
3. 测试安全边界