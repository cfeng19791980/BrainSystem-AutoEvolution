# Brain系统集成状态报告

> 时间: 2026-04-20 17:27
> 状态: 未自动集成，需要手动激活

---

## 一、当前状态

### ❌ 未自动集成

目前Brain V6 Lite已创建并测试通过，但**不会自动处理每个任务**。

**原因**:
- SOUL.md未配置Brain调用
- DECISION.md未包含Brain决策流程
- HEARTBEAT.md为空（无定期检查）

**现状**:
```
用户任务 → Agent直接处理（不经过Brain）
```

---

## 二、自动集成方案

### 方案A: SOUL.md集成（推荐）

在SOUL.md添加Brain调用规则：

```markdown
## 4. Brain规则（强制）

### 任务流程
所有任务必须经过Brain系统：

1. **感知阶段**: Brain.decide(query)
2. **决策阶段**: Brain输出行动方案
3. **执行阶段**: 按Brain方案执行
4. **反馈阶段**: Brain.feedback(success)

### 自动触发条件
- 每个用户请求
- 每个工具调用前
- 每个决策点

### Brain文件位置
- brain_v6_lite.py (主系统)
- .brain_decisions.json (决策日志)
- .brain_feedback.json (反馈日志)
```

### 方案B: HEARTBEAT.md集成

添加定期Brain状态检查：

```markdown
# Heartbeat任务

## 每5分钟检查
- Brain决策日志增长
- RL策略变化
- 系统健康评分

## 每小时汇总
- 决策成功率统计
- 知识召回率
- 上下文使用率
```

---

## 三、观察Brain表现的方法

### 方法1: 日志文件监控

**Brain运行时自动生成日志**:

```bash
# 查看决策日志
cat .brain_decisions.json

# 查看反馈日志  
cat .brain_feedback.json

# 查看RL策略
cat .brain_reinforcement.json

# 查看任务DAG
cat .brain_task_dag.json
```

### 方法2: 实时监控脚本

创建监控脚本 `brain_monitor.py`:

```python
import json, time
from datetime import datetime

def monitor_brain():
    while True:
        # 读取决策日志
        try:
            decisions = json.load(open('.brain_decisions.json'))
            latest = decisions[-1] if decisions else {}
            
            print(f"[{datetime.now()}]")
            print(f"  最新决策: {latest.get('id', 'N/A')}")
            print(f"  行动: {latest.get('action', 'N/A')}")
            print(f"  得分: {latest.get('score', 0):.2f}")
            
            # 统计
            total = len(decisions)
            successes = sum(1 for d in decisions if d.get('success'))
            rate = successes / total * 100 if total > 0 else 0
            
            print(f"  成功率: {rate:.1f}% ({successes}/{total})")
            
        except:
            print("等待Brain数据...")
        
        time.sleep(30)  # 30秒刷新

monitor_brain()
```

### 方法3: Dashboard可视化

在Dashboard添加Brain状态卡片：

```html
<!-- Brain Status Card -->
<div class="brain-status">
  <h3>🧠 Brain V6 Lite</h3>
  <div class="metrics">
    <div>决策总数: <span id="decision-count">0</span></div>
    <div>成功率: <span id="success-rate">0%</span></div>
    <div>RL策略: <span id="rl-policy">-</span></div>
    <div>上下文: <span id="context-size">0</span></div>
    <div>评分: <span id="brain-score">90</span>/100</div>
  </div>
  <div class="latest-decision">
    <h4>最新决策</h4>
    <pre id="latest-decision-json">-</pre>
  </div>
</div>

<script>
// 每10秒刷新
setInterval(async () => {
  const decisions = await fetch('.brain_decisions.json').then(r => r.json());
  const feedback = await fetch('.brain_feedback.json').then(r => r.json());
  
  document.getElementById('decision-count').textContent = decisions.length;
  
  const successes = feedback.filter(f => f.success).length;
  const rate = (successes / feedback.length * 100).toFixed(1);
  document.getElementById('success-rate').textContent = rate + '%';
  
  if (decisions.length > 0) {
    document.getElementById('latest-decision-json').textContent = 
      JSON.stringify(decisions[-1], null, 2);
  }
}, 10000);
</script>
```

### 方法4: 决策追踪输出

在Brain.decide()时打印详细过程：

```python
def decide(self, query):
    print("=" * 50)
    print("🧠 Brain决策开始")
    print("=" * 50)
    
    # Step 1-8详细输出
    print(f"[Step 1] 感知: {perception}")
    print(f"[Step 2] 意图: {intent}")
    print(f"[Step 3] 召回: {recalled}条知识")
    print(f"[Step 4] ReAct: {thought}")
    print(f"[Step 5] 方案: {len(plans)}个")
    print(f"[Step 6] 选择: {selected_plan}")
    print(f"[Step 7] 执行准备: {steps}步")
    print(f"[Step 8] 反馈准备: {track_id}")
    
    print("=" * 50)
    print(f"✅ 决策完成: {decision_id}")
    print("=" * 50)
    
    return decision
```

---

## 四、推荐集成步骤

### Step 1: 启用Brain自动调用

更新SOUL.md，添加Brain规则：

```markdown
## 4. Brain规则（强制）

### 任务流程
**每个任务必须经过Brain系统**：

1. 用户请求 → Brain感知
2. Brain决策 → 选择行动
3. 执行行动 → 工具调用
4. 结果反馈 → Brain学习

### Brain文件
- brain_v6_lite.py
- .brain_decisions.json（自动更新）
```

### Step 2: 添加监控脚本

```bash
# 启动监控
python brain_monitor.py

# 输出示例
[17:30:00]
  最新决策: dec_abc123
  行动: search
  得分: 0.85
  成功率: 92.5% (37/40)
```

### Step 3: Dashboard集成

在autoclaw-gui的index.html添加Brain状态卡片。

---

## 五、测试Brain是否工作

### 测试方法

```python
# 1. 手动调用Brain
from brain_v6_lite import BrainV6Lite
brain = BrainV6Lite()

# 2. 发起决策
decision = brain.decide("测试任务：分析Python性能")

# 3. 查看日志
# 自动生成 .brain_decisions.json

# 4. 反馈闭环
brain.feedback(decision['id'], success=True)

# 5. 查看更新
# .brain_feedback.json 已更新
```

---

## 六、当前建议

### 立即可做

1. **手动调用测试**: 运行 `test_sim_simple.py` 观察Brain行为
2. **查看日志**: 检查 `.brain_sim_report.json`
3. **添加监控**: 创建 `brain_monitor.py`

### 长期集成

1. **更新SOUL.md**: 添加Brain规则
2. **Dashboard集成**: 添加Brain状态卡片
3. **HEARTBEAT定期检查**: 每5分钟统计Brain表现

---

**当前状态**: Brain已就绪，但未自动集成
**下一步**: 选择集成方案（推荐方案A）