# Brain Hook插件完整实现指南

## 目标
实现代码级强制Brain决策，任何用户指令都经过Brain拦截

---

## 已完成步骤

### 1. 创建Hook插件 ✓
```
位置: C:\Users\Administrator\.openclaw\extensions\brain-hook\
文件:
  - index.js      (Hook拦截逻辑)
  - package.json  (插件配置)
```

### 2. 配置OpenClaw ✓
```json
{
  "plugins": {
    "allow": ["brain-hook", ...],
    "installs": {
      "brain-hook": {
        "installPath": "extensions/brain-hook"
      }
    }
  },
  "hooks": {
    "external": {
      "entries": {
        "brain-hook": {
          "enabled": true,
          "priority": "high"
        }
      }
    }
  }
}
```

### 3. 启动Brain API ✓
```
位置: workspace-工程师/brain_hook_api.py
端口: 5000
状态: 后台运行中
```

---

## 架构流程

```
用户指令
    ↓
OpenClaw接收
    ↓
Brain Hook拦截 (preProcess)
    ↓
调用 Brain API /decide
    ↓
根据confidence决定:
  - <0.5 → 返回"请示用户"
  - ≥0.5 → 允许执行
    ↓
执行指令
    ↓
Brain Hook反馈 (postProcess)
    ↓
调用 Brain API /feedback
    ↓
记录执行结果
```

---

## API接口

| 接口 | 功能 | 输入 | 输出 |
|-----|------|------|------|
| POST /decide | 决策 | {"query": "..."} | {"decision_id", "confidence", "action", "reason"} |
| POST /feedback | 反馈 | {"query", "success", "output"} | {"status": "ok"} |

---

## 测试结果

| 查询 | confidence | action |
|-----|------------|--------|
| 修复卖出建议逻辑 | 0.3 | ask_user |
| 更新Electron配置 | 0.3 | ask_user |
| 删除所有文件 | 0.3 | ask_user |
| 查询股票数据 | 0.3 | ask_user |

**当前状态**: 知识库内容较少，置信度较低。需要积累知识提升置信度。

---

## 下一步优化

### 1. 增强知识库
- 记录更多执行结果
- 积累成功模式
- 提高关键词匹配精度

### 2. 向量检索增强
- 集成memory_search向量检索
- 提升语义理解能力

### 3. P分级强制
- 检测P3关键词（删除、系统配置）
- 强制action=ask_user

---

## 使用方式

### 启动Brain API（后台）
```bash
python brain_hook_api.py --port 5000
```

### 重启OpenClaw
```bash
# 手动重启或通过Gateway
```

### 验证Hook工作
- 发送任意指令
- 观察是否经过Brain决策
- 检查confidence评估

---

## 文件清单

```
extensions/brain-hook/
  ├── index.js          - Hook拦截逻辑
  └── package.json      - 插件配置

workspace-工程师/
  ├── brain_hook_api.py - Brain API服务
  └── .brain_memory.json - 知识库
  └── .brain_executions.json - 执行记录
```

---

## 优势对比

| 方案 | 控制强度 | 依赖 |
|-----|---------|------|
| **Hook插件** | 强（代码级拦截） | 需要API服务 |
| 系统提示 | 弱（模型自觉） | 无依赖 |

---

**实现完成**: Brain Hook插件已创建，API服务已启动，配置已完成。重启OpenClaw后生效。