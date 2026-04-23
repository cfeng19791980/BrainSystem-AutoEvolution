# 清理流程模板

## 触发关键词
- 清理、clean、删除、remove、整理

---

## 执行流程

### Step 1: 识别清理目标
```
常见清理目标:
- 临时文件: *.tmp, *.temp, *.bak
- 日志文件: logs/*.log (超过30天)
- 缓存文件: __pycache__, node_modules/.cache
- 备份文件: *_backup_* (超过7天)
- 测试文件: test_*.py, test_output.*
```

### Step 2: 确认是否需要备份
```
IF 重要文件:
    创建备份后再清理
ELSE:
    直接清理
```

### Step 3: 执行清理
```bash
# Windows
del <file_pattern>

# Linux
rm <file_pattern>

# Python清理脚本
python cleanup_script.py
```

### Step 4: 验证清理结果
```
1. 检查文件是否已删除
2. 检查磁盘空间变化
3. 检查系统运行正常
```

### Step 5: 报告清理统计
```markdown
## 清理统计

- 清理文件数: X个
- 清理空间: X MB
- 清理时间: X秒
```

---

## 注意事项

1. **重要文件**: 清理前先备份
2. **系统文件**: 不清理Windows系统文件（SOUL.md规则）
3. **日志保留**: 保留最近30天日志
4. **统计报告**: 清理后报告统计

---

## 参考来源
- jwadow/agentic-prompts: Annihilator模式
- GitHub Agentic Workflows: Security模板

---

## Pattern-Key
`flow.clean.backup_important` - 清理流程重要文件备份机制