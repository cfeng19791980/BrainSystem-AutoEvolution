# Karpathy AutoResearch 导入报告

## 导入时间
2026-04-22 17:55 GMT+8

---

## 项目概述

**原作者**: Andrej Karpathy
**GitHub**: https://github.com/karpathy/autoresearch
**核心概念**: AI Agent自主研究 overnight，约100次实验/晚

### 工作原理

```
┌─────────────────────────────────────────────────────────────┐
│                    AutoResearch Loop                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 测量基线 (baseline metric)                              │
│                                                              │
│  2. Agent修改 train.py                                      │
│      ↓                                                       │
│  3. 运行训练 (5分钟时间预算)                                 │
│      ↓                                                       │
│  4. 检查 val_bpb                                             │
│      ↓                                                       │
│  5. 决策: improved? → keep / worse? → discard               │
│      ↓                                                       │
│  6. 记录 results.tsv                                         │
│      ↓                                                       │
│  7. 回到步骤2 (NEVER STOP)                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 关键文件

| Karpathy原版 | OpenClaw位置 | 作用 |
|--------------|-------------|------|
| `program.md` | `skills/autoresearch-karpathy/program.md` | Agent指令模板 |
| `train.py` | `skills/autoresearch-karpathy/train.py` | 训练代码示例 |
| `prepare.py` | `skills/autoresearch-karpathy/prepare.py` | 固定准备代码 |
| `README.md` | `skills/autoresearch-karpathy/README.md` | 项目说明 |

---

## OpenClaw适配文件

| 文件 | 位置 | 说明 |
|------|------|------|
| AUTORESEARCH-ADAPTATION.md | `brain-system/docs/` | 适配文档 |
| autoresearch_simple.py | `brain-system/scripts/` | 简化版脚本 |
| flow_template_autoresearch.md | `brain-system/data/knowledge/` | Flow模板 |

---

## FLOW_TEMPLATES 配置

```python
'autoresearch': [
    'autoresearch', 
    '自主研究', 
    'overnight优化', 
    'AI实验', 
    '自动优化'
],
```

---

## 测试结果

| 输入 | 检测结果 | 状态 |
|------|---------|------|
| "自主研究实验" | flow_autoresearch | ✅ OK |
| "autoresearch优化代码" | flow_optimize | ⚠️ 关键词冲突 |
| "overnight优化系统" | flow_optimize | ⚠️ 关键词冲突 |
| "运行AI实验循环" | general | ❌ 未匹配 |

**注意**: "优化"关键词被 `optimize` 模板优先匹配

---

## 设计原则（Karpathy）

### 1. 单文件修改
```
Agent只修改 train.py
保持diff可审查
降低复杂度
```

### 2. 固定时间预算
```
每实验5分钟
不同修改公平对比
约12实验/小时
```

### 3. 简洁优先
```
All else being equal, simpler is better
删除代码的改进 → 最值得保留
复杂改进 → 需要更大收益才值得
```

### 4. 永不停止
```
NEVER STOP until human interrupts
用户睡觉时Agent继续工作
约100次实验/晚
```

---

## 预期用途

| 场景 | 目标文件 | 评估指标 |
|------|---------|---------|
| Brain Entry优化 | `brain_entry.py` | 响应时间ms |
| Embedding优化 | embedding相关 | 向量质量 |
| Prompt优化 | system prompts | 任务成功率 |
| 配置优化 | `openclaw.json` | 效率指标 |

---

## 使用示例

### 启动autoresearch
```
用户: "启动自主研究优化brain_entry.py的响应时间"

Brain检测: flow_autoresearch
注入模板: flow_template_autoresearch.md

执行流程:
1. 确认目标文件
2. 测量基线响应时间
3. 开始自主实验循环
4. 汇报改进结果
```

### 简化版脚本
```bash
python autoresearch_simple.py --target brain_entry.py --metric response_time --max 10

# 输出:
# [Baseline] 120.5ms
# [Exp#1] 115.2ms (keep) - optimize loop
# [Exp#2] 118.8ms (discard) - add cache
# [Exp#3] 108.9ms (keep) - parallel process
# ...
# [Summary] Improvement: 9.7%
```

---

## 下一步

1. ✅ 导入完成 - program.md已读取
2. ✅ Flow模板创建 - flow_template_autoresearch.md
3. ✅ 简化脚本 - autoresearch_simple.py
4. ⏳ 实际运行测试 - 需要用户确认目标
5. ⏳ SelfImproving集成 - 添加 `/autoresearch/start` API

---

## 系统状态 (17:55)
- AutoResearch导入: ✅ 完成
- Flow Template: ✅ 已创建
- FLOW_TEMPLATES配置: ✅ 已更新
- 简化脚本: ✅ 已创建
- 触发测试: ⚠️ 部分通过（关键词冲突）

---

## 源码参考

```
C:\Users\Administrator\.openclaw\workspace-工程师\skills\autoresearch-karpathy\
├── program.md      ← Agent指令核心（7KB）
├── train.py        ← 训练代码（26KB）
├── prepare.py      ← 固定代码（15KB）
├── README.md       ← 项目说明（8KB）
└── analysis.ipynb  ← 分析笔记本
```

Generated: 2026-04-22 17:55 GMT+8