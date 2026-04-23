# 自主研究流程模板

## 触发关键词
- autoresearch, 自主研究, overnight优化, AI实验, 自动优化

---

## 执行流程

### Step 1: 确认目标
```yaml
目标文件: 用户指定或默认brain_entry.py
评估指标: 响应时间/准确率/内存使用
时间预算: 5分钟/实验
最大实验数: 10-100次
```

### Step 2: 准备环境
```bash
# 检查目标文件
ls <target_file>

# 创建备份
copy <target_file> <target_file>.original

# 初始化结果文件
echo "timestamp\texperiment\tmetric\tstatus\tdescription" > autoresearch_results.tsv
```

### Step 3: 测量基线
```python
baseline = evaluate_metric()
print(f"基线指标: {baseline}")
```

### Step 4: 实验循环
```python
LOOP:
    # Agent修改代码
    modification = propose_modification()
    apply_modification(target_file, modification)
    
    # 运行测试
    new_metric = evaluate_metric()
    
    # 决策
    if new_metric < baseline:
        baseline = new_metric
        keep_changes()
        log_result(status="keep")
    else:
        discard_changes()
        log_result(status="discard")
    
    # 继续下一轮
    # NEVER STOP 直到用户打断或达到max_experiments
```

### Step 5: 汇报结果
```
总实验数: X
改进次数: Y
最终指标: Z
总改进率: (baseline - final) / baseline * 100%
```

---

## Karpathy设计原则

### 1. 单文件修改
```
Agent只修改一个文件
保持diff可审查
```

### 2. 固定时间预算
```
每个实验固定时间
不同修改公平对比
```

### 3. 简洁优先
```
简单改进 > 复杂改进
删除代码的改进最值得保留
```

### 4. 永不停止
```
NEVER STOP until human interrupts
适合 overnight autonomous research
约100次实验/晚
```

---

## 评估指标示例

| 指标 | 说明 | 目标 |
|------|------|------|
| response_time | API响应时间(ms) | 越低越好 |
| accuracy | 任务完成率 | 越高越好 |
| memory_usage | 内存使用(MB) | 越低越好 |
| val_bpb | 验证损失 | 越低越好 |

---

## 结果记录格式 (TSV)

```
timestamp    experiment  metric    status     description
17:00:00     1           0.997     baseline   initial
17:05:00     2           0.993     keep       optimize loop
17:10:00     3           1.005     discard    add cache
```

---

## 触发示例

```
用户: "启动autoresearch优化brain_entry.py的响应时间"
Agent: 确认目标 → 开始自主循环 → 汇报结果
```

---

## 注意事项

1. **不要修改固定文件**: setup.py/prepare.py是只读的
2. **不要添加依赖**: 只用现有库
3. **超时处理**: 实验超过10分钟视为失败
4. **崩溃处理**: 简单错误修复，复杂错误跳过

---

## 参考来源

- Karpathy autoresearch: https://github.com/karpathy/autoresearch
- OpenClaw adaptation: brain-system/docs/AUTORESEARCH-ADAPTATION.md