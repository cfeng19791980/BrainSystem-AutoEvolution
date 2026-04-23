# Brain V3 自动学习版使用指南

---

## 核心特性

Brain V3 在 V2 基础上新增 **自动学习机制**：

| 特性 | 说明 |
|-----|-----|
| **自动触发学习** | 当知识不足时自动获取 |
| **三渠道集成** | GitHub、AKShare、免费书籍 |
| **置信度评估** | 自动评估解决能力 |
| **学习日志** | 记录每次学习过程 |

---

## 工作流程

```
用户输入 → 
  1. 检索知识库
  2. 评估置信度
  3. 如果 context_count < 2:
       → 自动从GitHub/AKShare获取
       → 导入新知识
       → 重新检索
  4. 返回决策结果
```

---

## 使用方式

```python
from brain_v3 import brain

# 自动学习模式（默认开启）
decision = brain.decide("TensorFlow深度学习")

# 查看是否进行了学习
if decision['learned']:
    print("Brain自动获取了相关知识")

# 禁用自动学习
decision = brain.decide("问题", auto_learn=False)
```

---

## 知识渠道

| 渠道 | 获取内容 | 适用问题类型 |
|-----|---------|-------------|
| **GitHub** | 项目README、代码示例 | React、Python、API等 |
| **AKShare** | 股票API文档 | 股票、量化、基金 |
| **免费书籍** | 技术书籍列表 | 通用知识 |

---

## 决策结果字段

```python
decision = {
    'decision_id': 'd_xxx',
    'action': 'python_code',
    'type': 'python',
    'risk_level': 2,
    'risk_name': '简要说明+执行',
    'need_approval': False,
    'skill': 'code',
    'context': [...],          # 检索到的上下文
    'context_count': 3,        # 上下文数量
    'confidence': 1.0,         # 置信度（0-1）
    'learned': True,           # 是否进行了自动学习
    'timestamp': '...'
}
```

---

## 学习记录

```python
# 查看学习日志
brain.learning_log

# 示例输出
[
    {
        'timestamp': '2026-04-20T01:10:00',
        'channel': 'github-free-books',
        'query': 'TensorFlow深度学习',
        'success': True
    }
]
```

---

## 知识库状态

```
当前知识: 732条长期记忆
决策日志: 31条
学习记录: 2次成功学习
规则数量: 15条
```

---

## 文件列表

```
workspace-工程师/
├── brain_v3.py              # V3自动学习版（推荐）
├── brain_v2.py              # V2风险分级版
├── brain.py                 # V1基础版
├── auto_fetch_knowledge.py  # 知识获取工具
├── import_knowledge.py      # 知识导入工具
└── memory/knowledge/        # 知识文件目录
    ├── python.md
    ├── react-native.md
    ├── akshare_api.md
    └── ...
```

---

## 建议

1. **优先使用 Brain V3** - 自动学习，持续进化
2. **定期检查学习日志** - 了解Brain学了什么
3. **手动补充知识** - 使用 auto_fetch_knowledge.py

---

Last Updated: 2026-04-20