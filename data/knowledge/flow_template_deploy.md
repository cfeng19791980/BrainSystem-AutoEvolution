# 部署流程模板

## 触发关键词
- 部署、deploy、发布、上线

---

## 执行流程

### Step 1: 检查环境
```bash
# 检查依赖
pip list / npm list

# 检查端口占用
netstat -ano | findstr :<port>

# 检查磁盘空间
df -h / dir
```

### Step 2: 备份当前版本
```bash
# 备份规则
copy <current_file> <current_file>_backup_<version>
```

### Step 3: 执行部署
```bash
# Python部署
pip install -r requirements.txt
python <main>.py

# Node.js部署
npm install
npm start

# 服务部署
systemctl restart <service>
```

### Step 4: 检查部署状态
```
1. 检查端口监听
2. 检查进程运行
3. 检查日志输出
```

### Step 5: 验证功能
```
1. 调用API测试
2. 检查返回结果
3. 确认功能可用
```

### Step 6: 记录部署日志
```
更新 memory/<date>.md:
- 部署版本
- 部署时间
- 验证结果
```

---

## 失败回滚
```
IF deploy_failed:
    1. 停止新服务
    2. 恢复备份版本
    3. 重新启动
    4. 验证回滚成功
```

---

## 参考来源
- jwadow/agentic-prompts: Observer模式
- GitHub Agentic Workflows: Release Management模板

---

## Pattern-Key
`flow.deploy.rollback` - 部署流程失败回滚机制