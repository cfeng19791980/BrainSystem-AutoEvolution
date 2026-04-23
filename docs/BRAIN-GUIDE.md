# Brain系统使用指南

## 自动调用机制

Brain系统设计为**全自动调用**，无需关键词或触发词。每次Agent处理任务时自动调用。

### 集成方式

在Agent入口处添加一行代码：

```python
from brain_v2 import brain

# 每次处理任务时自动调用（无需条件判断）
decision = brain.decide(user_input)

# 根据风险等级决定执行方式
if decision['need_approval']:
    # P3级别 - 需要批准
    print(f"[Brain] P3风险 - 需批准: {decision['risk_name']}")
    # 等待用户批准...
elif decision['risk_level'] == 0:
    # P0级别 - 立即执行
    print(f"[Brain] P0紧急 - 立即执行")
    # 立即执行...
else:
    # P1-P2级别 - 正常执行
    print(f"[Brain] {decision['risk_name']} - 技能: {decision['skill']}")
    # 执行任务...

# 执行后自动记忆
brain.remember(user_input, result, decision['decision_id'])
```

## 风险分级（P0-P3）

| 等级 | 名称 | 关键词 | 执行方式 |
|-----|-----|-----|-----|
| P0 | 立即执行 | 紧急、故障、崩溃、死机 | 无需说明，立即执行 |
| P1 | 立即执行+记录 | 调试、修复、报错、bug | 立即执行，记录日志 |
| P2 | 简要说明+执行 | 创建、修改、更新、开发 | 简要说明，然后执行 |
| P3 | 详细说明+等待批准 | 删除、系统、配置、权限 | 详细说明，等待批准 |

## 技能路由

Brain会自动匹配技能路径：

| 技术栈 | 技能 | 关键词 |
|-----|-----|-----|
| React Native | code | react native, rn, android, ios |
| Python | code | python, py, django, flask |
| JavaScript | code | javascript, js, node, npm |
| Database | code | sql, sqlite, mysql, 数据库 |
| Git | code | git, commit, push, pull |
| Stock | stock-analysis | 股票, 量化, 回测 |
| Browser | browser-job-automation | browser, 浏览器, 自动化 |
| API | code | api, 接口, http, rest |
| Debug | code-debug | 调试, bug, 报错, 异常 |

## 文件结构

```
workspace/
├── brain_v2.py              # 主入口（风险分级+技能路由）
├── brain_auto.py            # 全自动集成器
├── brain_decision_engine.py # 决策引擎
├── brain_knowledge_base.py  # 知识库
├── brain_api_server.py      # HTTP API服务
├── .brain_memory.json       # 记忆存储
└── .brain_decisions.json    # 决策日志
```

## 已部署工作区

- workspace（主工作区）
- workspace-工程师
- workspace-架构师
- workspace-数据专家
- workspace-资深架构师

---

Last Updated: 2026-04-20