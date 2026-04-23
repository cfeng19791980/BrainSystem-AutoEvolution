# AutoResearch 最大化应用指南

## 概念理解

**AutoResearch = AI自主 overnight研究**
- Agent自主修改代码 → 测试 → 评估 → keep/discard
- 约100次实验/晚（5分钟/实验）
- 核心：**客观指标 + 自主循环 + 持续优化**

---

## 关键洞察

### ❌ 之前的错误实验
```
目标: analyzer.py 响应时间
方法: 测量 import time
结果: "99.6%改进" ← 假的！Python模块缓存
```

### ✅ 正确的评估方法
```python
# 错误：只测import时间
import time
t0 = time.time()
import analyzer  # ← 第二次会从cache加载
print(time.time() - t0)  # 假优化

# 正确：测真正的函数执行
import importlib
importlib.reload(analyzer)  # 清除缓存
result = analyzer.process_query("test query")  # ← 实际执行
print(result.time_ms)
```

---

## 应用场景设计

### 场景1：Brain Entry API优化
| 项目 | 设置 |
|------|------|
| **目标文件** | `brain_entry.py` |
| **修改范围** | 搜索逻辑、意图识别、流程模板 |
| **评估指标** | 端到端响应时间（API → 结果返回） |
| **测试数据** | 100个预定义query（标准化测试集） |
| **时间预算** | 30秒/实验（100个query × 0.3秒/query） |

**评估函数设计**：
```python
def evaluate_brain_entry():
    """客观评估Brain Entry性能"""
    test_queries = load_test_dataset()  # 100个标准化query
    
    # 强制清除缓存
    importlib.reload(brain_entry)
    
    total_time = 0
    correct_count = 0
    
    for q in test_queries:
        t0 = time.time()
        result = brain_entry.process_entry(q['content'])
        total_time += time.time() - t0
        
        # 检查意图识别准确率
        if result['intent']['type'] == q['expected_intent']:
            correct_count += 1
    
    avg_time_ms = total_time * 1000 / len(test_queries)
    accuracy = correct_count / len(test_queries)
    
    return {
        'avg_time_ms': avg_time_ms,
        'accuracy': accuracy,
        'score': accuracy * 100 - avg_time_ms  # 综合评分
    }
```

### 场景2：向量搜索优化
| 项目 | 设置 |
|------|------|
| **目标文件** | `embedding_provider.py` |
| **修改范围** | 相似度算法、阈值、查询策略 |
| **评估指标** | 召回率 + 响应时间 |
| **测试数据** | Memory搜索测试集（已知答案的query） |

**评估函数**：
```python
def evaluate_vector_search():
    test_cases = [
        {'query': 'brain hook', 'expected_ids': ['brain-entry-api']},
        {'query': 'AutoResearch', 'expected_ids': ['autoresearch-karpathy']},
        # ... 50个测试case
    ]
    
    recall_total = 0
    time_total = 0
    
    for case in test_cases:
        t0 = time.time()
        results = search_memory(case['query'])
        time_total += time.time() - t0
        
        # 计算召回率：是否找到预期的文档
        found = sum(1 for exp in case['expected_ids'] 
                   if exp in [r['id'] for r in results])
        recall_total += found / len(case['expected_ids'])
    
    return {
        'recall': recall_total / len(test_cases),
        'avg_time_ms': time_total * 1000 / len(test_cases)
    }
```

### 场景3：SelfImproving Pattern检测优化
| 项目 | 设置 |
|------|------|
| **目标文件** | `self_improving.py` |
| **修改范围** | Pattern提取逻辑、阈值、分类算法 |
| **评估指标** | Pattern检测准确率 |
| **测试数据** | 历史反馈数据（已知pattern） |

### 场景4：CSI10 股票分析优化
| 项目 | 设置 |
|------|------|
| **目标文件** | `analyzer_v4.py` |
| **修改范围** | 模型参数、评分算法、买卖信号逻辑 |
| **评估指标** | 预测准确率（模拟回测） |
| **测试数据** | 历史30天数据（已知涨跌） |

---

## 防坑指南

### 1. 模块缓存陷阱 ⚠️
```python
# 解决方案：每次实验前强制reload
import importlib
importlib.reload(target_module)

# 或使用subprocess运行（完全隔离）
result = subprocess.run(['python', 'test_evaluate.py'], capture_output=True)
```

### 2. 评估指标陷阱 ⚠️
```
❌ 错误指标：代码行数减少（不等于性能提升）
❌ 错误指标：import时间（受缓存影响）
✅ 正确指标：实际函数执行时间 + 准确率
```

### 3. 修改范围陷阱 ⚠️
```
❌ 过大范围：修改整个系统 → 难追踪、易崩溃
✅ 单文件范围：如 train.py 或 brain_entry.py
✅ 保持依赖稳定：prepare.py 不修改
```

### 4. 时间预算陷阱 ⚠️
```
❌ 过短预算：< 10秒 → 数据不足、波动大
❌ 过长预算：> 10分钟 → 实验/晚数量减少
✅ 合理预算：30秒 ~ 5分钟（根据任务复杂度）
```

---

## 最佳实践

### 1. 设计标准化测试集
```python
# 创建 brain_test_cases.json
{
    "test_cases": [
        {"content": "brain hook", "expected_intent": "query", "expected_docs": ["brain-hook"]},
        {"content": "optimize brain", "expected_intent": "optimize", "expected_docs": []},
        # ... 100个case，覆盖各种场景
    ]
}
```

### 2. Git版本控制
```bash
# 每个实验一个commit
git checkout -b autoresearch/brain-entry-v1
# 实验1: 修改brain_entry.py
git commit -am "experiment: add cache layer"
# 测试评估
python evaluate_brain.py
# 记录results.tsv
echo "a1b2c3d\t85.2ms\t0.92\tkeep\tcache layer" >> results.tsv
```

### 3. 结果记录（results.tsv）
```
commit	time_ms	accuracy	status	description
a1b2c3d	85.2	0.92	keep	baseline
b2c3d4e	82.1	0.93	keep	add query cache
c3d4e5f	90.5	0.91	discard	remove cache (worse)
d4e5f6g	78.3	0.94	keep	optimize intent detection
```

### 4. NEAR STOP原则
```
✅ 持续运行：约100次实验/晚
✅ 自主决策：improved → keep, worse → discard
✅ 多角度尝试：架构、算法、参数、策略
❌ 不要中途停止询问用户
```

---

## Brain System AutoResearch 架构

```
brain-system/autoresearch/
├── prepare.py          ← 固定：测试数据、评估函数
├── target.py           ← 修改：brain_entry.py 或其他目标
├── evaluate.py         ← 评估脚本（客观指标）
├── program.md          ← Agent指令
├── results.tsv         ← 实验记录
└── test_cases.json     ← 标准化测试数据
```

### prepare.py（固定，不修改）
```python
# -*- coding: utf-8 -*-
"""
Brain Entry AutoResearch - prepare.py
固定配置和评估函数
"""

import json
import time
import importlib

# 测试数据路径
TEST_CASES_FILE = 'test_cases.json'
TIME_BUDGET = 30  # 30秒/实验

# 加载测试数据
def load_test_cases():
    with open(TEST_CASES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)['test_cases']

# 评估函数（核心）
def evaluate_brain_entry():
    """评估Brain Entry性能"""
    test_cases = load_test_cases()
    
    # 强制reload（清除缓存）
    import brain_entry
    importlib.reload(brain_entry)
    
    total_time = 0
    correct_intent = 0
    correct_recall = 0
    
    for case in test_cases:
        t0 = time.time()
        result = brain_entry.process_entry(case['content'])
        total_time += time.time() - t0
        
        if result['intent']['type'] == case['expected_intent']:
            correct_intent += 1
        
        # 召回率检查
        found_ids = [r.get('id', r.get('path', '')) for r in result.get('results', [])]
        expected_found = sum(1 for exp in case['expected_docs'] if exp in found_ids)
        correct_recall += expected_found / max(len(case['expected_docs']), 1)
    
    n = len(test_cases)
    avg_time_ms = total_time * 1000 / n
    intent_accuracy = correct_intent / n
    recall_accuracy = correct_recall / n
    
    # 综合评分：准确率优先，时间惩罚
    score = (intent_accuracy * 50 + recall_accuracy * 50) - avg_time_ms * 0.1
    
    print("---")
    print(f"avg_time_ms:      {avg_time_ms:.1f}")
    print(f"intent_accuracy:  {intent_accuracy:.4f}")
    print(f"recall_accuracy:  {recall_accuracy:.4f}")
    print(f"score:            {score:.2f}")
    
    return score

if __name__ == "__main__":
    evaluate_brain_entry()
```

---

## 推荐应用顺序

### Phase 1：基础设施
1. 创建 `test_cases.json`（100个标准化测试case）
2. 创建 `evaluate.py`（客观评估函数）
3. 建立 Git 分支 `autoresearch/brain-entry-v1`

### Phase 2：首次实验
1. 运行 baseline（当前代码）
2. 记录 `results.tsv`
3. 确认评估系统正常

### Phase 3：overnight运行
1. 启动Agent自主循环
2. 约100次实验/晚
3. 检查 `results.tsv` 结果

### Phase 4：应用最佳改进
1. 查看 `results.tsv` 中最高 score
2. Checkout 对应 commit
3. 合并到主分支

---

## 预期效果

| 场景 | 预期改进 | 时间 |
|------|---------|------|
| Brain Entry响应时间 | -20%~50% | overnight |
| 向量搜索召回率 | +5%~15% | overnight |
| Pattern检测准确率 | +10%~30% | overnight |
| CSI10预测准确率 | +3%~10% | overnight |

---

## 总结

**AutoResearch最大化效果的关键**：

1. ✅ **客观评估指标**：实际函数执行 + 准确率
2. ✅ **标准化测试集**：100个预定义case
3. ✅ **清除缓存**：importlib.reload 或 subprocess
4. ✅ **单文件修改**：范围可控、易追踪
5. ✅ **持续运行**：100次实验/晚，自主决策
6. ✅ **Git版本控制**：每个实验可追溯
7. ✅ **结果记录**：results.tsv 完整历史

**不要**：
- ❌ 只测import时间
- ❌ 过大修改范围
- ❌ 中途停止询问
- ❌ 使用主观指标