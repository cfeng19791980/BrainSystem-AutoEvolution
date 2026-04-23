# 测试流程模板

## 触发关键词
- 测试、test、检测、验证

---

## 执行流程

### Step 1: 启动目标程序
```bash
# 根据目标类型启动
python <target>.py    # Python程序
npm start            # Node.js程序
```

### Step 2: 检测端口/服务状态
```bash
# Windows端口检测
netstat -ano | findstr :<port>

# Linux端口检测
netstat -tlnp | grep <port>
```

### Step 3: 读取运行日志
```
# 优先读取最后100行
日志路径: ~/.openclaw/logs/<target>.log
或项目目录: logs/<target>.log
```

### Step 4: 检测错误信息
检查以下错误类型：
- ERROR / Exception
- 404 / 500 (HTTP错误)
- Connection refused
- Timeout
- Import Error
- Syntax Error

### Step 5: 自动修复（如果发现错误）
```
IF error_found:
    1. 分析错误类型和原因
    2. 定位问题文件和位置
    3. 备份原文件（*_backup）
    4. 修改代码
    5. 重新测试验证
```

---

## 注意事项

1. **启动等待**: 程序启动后等待3-5秒让服务稳定
2. **日志优先**: 最后100行，如果不足则读取全部
3. **修复规则**: 先备份再修改（SOUL.md规则6）
4. **验证循环**: 修复后必须重新测试确认

---

## 参考来源
- jwadow/agentic-prompts: Test Engineer模式
- GitHub Agentic Workflows: Code Quality模板

---

## Pattern-Key
`flow.test.auto_fix` - 测试流程自动修复机制