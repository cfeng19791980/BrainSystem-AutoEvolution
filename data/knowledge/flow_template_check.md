# 检查流程模板

## 触发关键词
- 检查、check、查看、诊断、inspect

---

## 执行流程

### Step 1: 读取目标
```
读取目标文件/日志/数据/配置
使用 read 工具或 exec 命令
```

### Step 2: 分析内容
```
1. 结构分析：文件结构、代码结构
2. 内容分析：关键数据、配置项
3. 状态分析：运行状态、连接状态
4. 版本分析：版本号、更新时间
```

### Step 3: 发现异常
```
检查以下异常：
- 配置错误
- 数据缺失
- 版本过期
- 状态异常
- 性能问题
```

### Step 4: 报告结果
```markdown
## 检查报告

### 状态
- [正常] / [异常]

### 发现的问题
1. <问题描述>
2. <问题描述>

### 修复建议
1. <建议内容>
2. <建议内容>
```

---

## 输出格式

```json
{
  "target": "<检查对象>",
  "status": "normal|abnormal",
  "issues": ["<问题列表>"],
  "suggestions": ["<建议列表>"]
}
```

---

## 参考来源
- jwadow/agentic-prompts: Principal Engineer模式
- GitHub Agentic Workflows: Issue Management模板

---

## Pattern-Key
`flow.check.report_format` - 检查流程报告格式