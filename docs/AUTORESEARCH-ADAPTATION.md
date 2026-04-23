# autoresearch - OpenClaw Brain System Adaptation

> Based on karpathy/autoresearch - Autonomous AI research overnight
> Adapted for OpenClaw Self-Improving Framework

## 核心概念

Karpathy的autoresearch理念：
```
给AI一个实验环境 → 让它自主修改代码 → 运行测试 → 检查结果 → 保留/丢弃 → 无限循环
人类睡觉，AI做研究！约100次实验/晚
```

## 关键文件映射

| Karpathy原版 | OpenClaw适配 | 说明 |
|--------------|-------------|------|
| `program.md` | `skill/program.md` | Agent指令（人类编辑） |
| `train.py` | `target/code.py` | Agent修改的目标文件 |
| `prepare.py` | `setup/fixed.py` | 固定的准备代码 |
| `results.tsv` | `log/results.tsv` | 实验结果记录 |

## 设计原则

### 1. 单文件修改
```
Agent只修改一个文件，保持diff可审查
OpenClaw: target/*.py
```

### 2. 固定时间预算
```
每个实验固定时间（5分钟）
不同修改公平对比
```

### 3. 简洁优先
```
All else being equal, simpler is better
0.001改进 + 20行hacky代码 → 不值得
0.001改进 + 删除代码 → 值得
```

### 4. 无限循环
```
NEVER STOP - 人类打断才停止
适合 overnight autonomous research
```

---

## OpenClaw集成方案

### 方案A: 作为Skill模板

```
skills/
└── autoresearch/
    ├── program.md          ← Agent指令模板
    ├── setup.py            ← 固定环境准备
    ├── target.py           ← Agent修改的文件
    └── results.tsv         ← 实验记录
```

**触发方式**：
```
用户: "启动autoresearch优化brain_entry.py"
Brain: 读取program.md → 开始自主实验循环
```

### 方案B: SelfImprovingManager集成

```python
class AutoResearchManager:
    """自主研究管理器 - 基于Karpathy autoresearch"""
    
    def start_research_loop(self, target_file, metric_func):
        """
        启动自主研究循环
        
        Args:
            target_file: 要优化的目标文件
            metric_func: 评估函数 (返回数值，越低越好)
        """
        while True:  # NEVER STOP
            # 1. 读取当前状态
            current_metric = metric_func()
            
            # 2. Agent修改代码
            modified_code = self.agent_modify(target_file)
            
            # 3. 运行测试
            new_metric = self.run_experiment(target_file)
            
            # 4. 决策
            if new_metric < current_metric:
                self.keep_changes(target_file, modified_code)
            else:
                self.discard_changes(target_file)
            
            # 5. 记录结果
            self.log_result(new_metric, status='keep' if improved else 'discard')
```

### 方案C: 简化版 - 代码优化循环

```python
# 简化版autoresearch
def simple_optimization_loop():
    """
    最简版本：让Agent自主优化代码
    """
    baseline_metric = evaluate()
    
    for experiment in range(100):  # 100次实验
        # 修改代码
        modify_target_file()
        
        # 测试
        new_metric = evaluate()
        
        # 决策
        if new_metric < baseline_metric:
            baseline_metric = new_metric
            commit("improved")
        else:
            revert()
        
        log_result(new_metric)
```

---

## 实验输出格式

```yaml
---
val_metric:      0.997900  # 评估指标（越低越好）
run_seconds:     300.1     # 运行时间
peak_memory_mb:  45060.2   # 内存使用
status:          keep      # keep/discard/crash
description:     increase LR to 0.04
---
```

## results.tsv格式

```
commit  val_metric  memory_gb  status   description
a1b2c3d 0.997900    44.0       keep     baseline
b2c3d4e 0.993200    44.2       keep     increase LR to 0.04
c3d4e5f 1.005000    44.0       discard  switch to GeLU
```

---

## 触发关键词

```
关键词: autoresearch, 自主研究, overnight优化, AI实验
触发: flow_template_autoresearch.md
```

---

## 预期用途

| 场景 | 目标文件 | 评估指标 |
|------|---------|---------|
| Brain Entry优化 | brain_entry.py | 响应时间ms |
| Embedding优化 | embedding相关 | 向量质量 |
| Prompt优化 | system prompts | 任务成功率 |
| 配置优化 | openclaw.json | 效率指标 |

---

## 源码位置

```
C:\Users\Administrator\.openclaw\workspace-工程师\skills\autoresearch-karpathy\
├── program.md      ← 核心Agent指令（已导入）
├── train.py        ← 训练代码模板
├── prepare.py      ← 固定准备代码
└── README.md       ← 项目说明
```

---

## 下一步

1. **创建简化版**: 适配OpenClaw的autoresearch循环
2. **集成到Brain**: 添加 `/autoresearch/start` API
3. **创建flow模板**: flow_template_autoresearch.md
4. **测试**: 让Agent自主优化一个简单函数

Generated: 2026-04-22 17:52 GMT+8