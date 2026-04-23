# GitHub模板导入报告

## 导入时间
2026-04-22 16:48 GMT+8

---

## 模板来源

### 1. jwadow/agentic-prompts
**Agent角色模式**:
- 🧠 Maestro: 项目协调，分解任务
- 🏛️ Principal Engineer: 架构设计
- 💻 Lead Implementer: 代码实现
- 🧪 Test Engineer: 测试验证
- 🌿 Gardener: 代码质量/重构
- 👾 Mr. Robot: 安全审计
- 👁️ Observer: 监控/部署
- 👺 Annihilator: 简化/移除冗余

### 2. dontriskit/awesome-ai-system-prompts
**944模板核心原则**:
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

## 导入的模板文件

| 模板 | 文件 | 触发关键词 | 验证 |
|------|------|-----------|------|
| **test** | flow_template_test.md | 测试, test, 检测, 验证 | ✅ |
| **fix** | flow_template_fix.md | 修复, fix, bug, 改正, 解决 | ✅ |
| **check** | flow_template_check.md | 检查, check, 查看, 诊断 | ✅ |
| **deploy** | flow_template_deploy.md | 部署, deploy, 发布, 上线 | ✅ |
| **restart** | flow_template_restart.md | 重启, restart, 重新启动 | ✅ |
| **clean** | flow_template_clean.md | 清理, clean, 删除, remove | ✅ |
| **optimize** | flow_template_optimize.md | 优化, optimize, 改进, 提升 | ✅ |
| **debug** | flow_template_debug.md | 调试, debug, 排查 | ✅ |
| **add** | flow_template_add.md | 添加, add, 新增, 创建 | ✅ |
| **update** | flow_template_update.md | 更新, update, 刷新, 同步 | ✅ |

**验证结果**: 10/10 PASS

---

## 辅助文档

| 文件 | 内容 |
|------|------|
| FLOW_TEMPLATES_INDEX.md | 模板索引、来源参考 |
| TASK-TEMPLATES.md | 任务模板库（代码调试、文件操作等） |

---

## 文件结构

```
C:\Users\Administrator\.openclaw\brain-system\data\knowledge\
├── FLOW_TEMPLATES_INDEX.md    ← 模板索引
├── TASK-TEMPLATES.md          ← 任务模板库
├── flow_template_test.md      ← 测试流程
├── flow_template_fix.md       ← 修复流程
├── flow_template_check.md     ← 检查流程
├── flow_template_deploy.md    ← 部署流程
├── flow_template_restart.md   ← 重启流程
├── flow_template_clean.md     ← 清理流程
├── flow_template_optimize.md  ← 优化流程
├── flow_template_debug.md     ← 调试流程
├── flow_template_add.md       ← 添加流程
└── flow_template_update.md    ← 更新流程
```

---

## 触发机制

```python
FLOW_TEMPLATES = {
    'test': ['测试', 'test', '检测', '验证'],
    'fix': ['修复', 'fix', 'bug', '改正', '解决'],
    'check': ['检查', 'check', '查看', '诊断', 'inspect'],
    'deploy': ['部署', 'deploy', '发布', '上线'],
    'restart': ['重启', 'restart', '重新启动'],
    'clean': ['清理', 'clean', '删除', 'remove', '整理'],
    'optimize': ['优化', 'optimize', '改进', '提升'],
    'debug': ['调试', 'debug', '排查'],
    'add': ['添加', 'add', '新增', '创建', '增加'],
    'update': ['更新', 'update', '刷新', '同步'],
}
```

---

## 使用示例

| 用户输入 | 检测结果 | 注入模板 |
|----------|----------|----------|
| "测试系统功能" | flow_test | flow_template_test.md |
| "修复这个bug" | flow_fix | flow_template_fix.md |
| "检查系统状态" | flow_check | flow_template_check.md |
| "部署到生产" | flow_deploy | flow_template_deploy.md |

---

## 原始模板位置

```
C:\Users\Administrator\.openclaw\workspace-工程师\memory\knowledge\
└── (原始模板文件保留)
```

---

## 扩展建议

### 可选：继续导入更多模板
1. **Agent角色模板** - Maestro/Engineer/Test/Gardener等
2. **Team Workflow** - TEAM-WORKFLOW.md协作流程
3. **Skills模板** - skills目录下的40+技能模板

### GitHub热门模板推荐
| 仓库 | 内容 | Stars |
|------|------|-------|
| jwadow/agentic-prompts | Agent模式+Commands | 高 |
| dontriskit/awesome-ai-system-prompts | 944系统提示模板 | 高 |
| awesome-chatgpt-prompts | ChatGPT提示词合集 | 100k+ |
| prompt-engineering-guide | 提示工程指南 | 高 |

---

## 系统状态 (16:48)
- Flow Templates: ✅ 10个模板已导入
- Template Verification: ✅ 10/10 PASS
- Knowledge目录: ✅ 12个文件
- FLOW_TEMPLATES配置: ✅ 已同步

Generated: 2026-04-22 16:48 GMT+8