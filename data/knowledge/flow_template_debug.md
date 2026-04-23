# 调试流程模板

## 触发关键词
- 调试、debug、排查、排查问题

---

## 执行流程

### Step 1: 复现问题
```
1. 执行触发问题的操作
2. 记录问题出现条件
3. 确认问题可稳定复现
```

### Step 2: 添加调试信息
```python
# Python调试代码
print(f"DEBUG: <变量> = {<变量>}")  # 变量值
print(f"DEBUG: 进入函数 <函数名>")  # 执行路径
import logging; logging.debug("<信息>")  # 日志调试
```

### Step 3: 分析日志输出
```
1. 运行程序获取调试输出
2. 分析变量值变化
3. 分析执行路径
4. 定位问题位置
```

### Step 4: 定位问题根因
```
常见根因:
- 变量值异常
- 条件判断错误
- 数据格式问题
- 依赖版本问题
- 环境配置问题
```

### Step 5: 修复问题
```
参考 flow_template_fix:
1. 备份原文件
2. 修改代码
3. 测试验证
```

### Step 6: 清理调试代码
```
⚠️ 调试代码使用后及时清理

删除添加的:
- print调试语句
- DEBUG注释
- 临时日志配置
```

### Step 7: 验证修复效果
```
1. 确认问题不再出现
2. 确认功能正常
3. 确认调试代码已清理
```

---

## 注意事项

1. **调试代码**: 添加调试print/temp日志
2. **及时清理**: 修复后立即清理调试代码
3. **记录原因**: 记录问题根因到memory
4. **验证完整**: 确认清理和修复都完成

---

## 参考来源
- jwadow/agentic-prompts: Test Engineer + Mr. Robot模式
- GitHub Agentic Workflows: Developer Experience模板

---

## Pattern-Key
`flow.debug.cleanup` - 调试流程代码清理机制