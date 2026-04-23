# 流程模板索引

## 来源参考
- jwadow/agentic-prompts (Agent模式 + Commands)
- dontriskit/awesome-ai-system-prompts (944模板)
- GitHub官方56个Agentic Workflows

---

## 模板列表

| 模板文件 | 触发关键词 | 适用场景 |
|----------|-----------|---------|
| flow_template_test.md | 测试、test、检测、验证 | 启动→检测→读日志→发现错误→修复 |
| flow_template_fix.md | 修复、fix、bug、改正、解决 | 定位→备份→修改→验证 |
| flow_template_check.md | 检查、check、查看、诊断 | 读取→分析→报告 |
| flow_template_deploy.md | 部署、deploy、发布、上线 | 检查环境→备份→部署→验证 |
| flow_template_restart.md | 重启、restart | 停止→等待→启动→验证 |
| flow_template_clean.md | 清理、clean、删除 | 识别→备份→清理→统计 |
| flow_template_optimize.md | 优化、optimize、改进 | 分析→方案→实施→验证 |
| flow_template_debug.md | 调试、debug、排查 | 复现→添加日志→分析→修复 |
| flow_template_add.md | 添加、add、新增、创建 | 检查冲突→创建→测试→更新文档 |
| flow_template_update.md | 更新、update、刷新、同步 | 获取→备份→应用→验证 |

---

## 使用方式

Brain系统自动匹配：
1. 用户指令包含关键词
2. Brain搜索匹配模板
3. prependContext注入完整流程
4. LLM执行标准流程

---

## 模板来源详细

### jwadow/agentic-prompts 关键内容

**Agent角色模式：**
- 🧠 Maestro: 项目协调，分解任务
- 🏛️ Principal Engineer: 架构设计
- 💻 Lead Implementer: 代码实现
- 🧪 Test Engineer: 测试验证
- 🌿 Gardener: 代码质量/重构
- 👾 Mr. Robot: 安全审计
- 👁️ Observer: 监控/部署
- 👺 Annihilator: 简化/移除冗余

**Slash Commands：**
- GitHub Release: 自动生成发布说明
- Subtask Analysis: 分析子任务
- Subtask Code: 编码子任务

### dontriskit/awesome-ai-system-prompts 核心原则

```
1. Clear Role Definition - 明确角色
2. Structured Instructions - 结构化指令
3. Explicit Tool Integration - 工具规则
4. Step-by-Step Reasoning - 分步推理
5. Environment Context - 环境信息
6. Domain Constraints - 领域约束
7. Safety/Refusal Protocols - 安全规则
8. Consistent Tone - 一致风格
```

---

## Pattern-Key

`flow.template.match` - 流程模板自动匹配机制