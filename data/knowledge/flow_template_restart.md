# 重启流程模板

## 触发关键词
- 重启、restart、重新启动

---

## 执行流程

### Step 1: 停止当前服务
```bash
# Windows
taskkill /PID <pid> /F
# 或
taskkill /IM <process_name> /F

# Linux
kill <pid>
# 或
systemctl stop <service>
```

### Step 2: 等待停止完成
```
等待时间: 2-3秒
确保进程完全停止
```

### Step 3: 检查端口释放
```bash
netstat -ano | findstr :<port>
# 确认端口未被占用
```

### Step 4: 启动新服务
```bash
python <service>.py
# 或
npm start
# 或
systemctl start <service>
```

### Step 5: 检查启动状态
```
1. 端口监听检查
2. 进程运行检查
3. 日志输出检查
```

### Step 6: 验证功能
```
1. API调用测试
2. 响应时间检查
3. 功能确认
```

---

## 注意事项

1. **端口检查**: 启动前确保端口未被占用
2. **等待时间**: 停止后等待足够时间
3. **日志检查**: 启动后检查日志是否有错误
4. **功能验证**: 必须验证服务正常响应

---

## 参考来源
- jwadow/agentic-prompts: Observer模式
- GitHub Agentic Workflows: Developer Experience模板

---

## Pattern-Key
`flow.restart.port_check` - 重启流程端口检查机制