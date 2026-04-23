# 修复流程模板

## 触发关键词
- 修复、fix、bug、改正、解决

---

## 执行流程

### Step 1: 定位问题
```
1. 搜索错误关键词在代码中的位置
2. 检查相关文件和函数
3. 分析调用链和依赖关系
```

### Step 2: 分析问题原因
```
1. 检查代码逻辑
2. 检查数据/参数传递
3. 检查环境配置
4. 检查依赖版本
```

### Step 3: 备份原文件
```bash
# 备份规则（SOUL.md规则6）
copy <file> <file>_backup_<date>
```

### Step 4: 修改代码
```
1. 修改问题代码
2. 保持代码风格一致
3. 不添加多余注释
4. 不创建新文件（Pattern-Key: upgrade.filename_preserve）
```

### Step 5: 测试验证
```
1. 运行测试流程（flow_template_test）
2. 确认修复有效
3. 检查是否引入新问题
```

### Step 6: 记录修复
```
更新 memory/<date>.md:
- 修复内容
- 问题原因
- 解决方案
```

---

## 注意事项

1. **备份优先**: 任何修改前必须备份
2. **原地修改**: 不创建新文件，直接修改原文件
3. **测试验证**: 修改后必须测试
4. **记录memory**: 修复内容记录到当天memory

---

## P级别判断
- P1: 系统崩溃、数据丢失、安全漏洞
- P2: 功能异常、性能问题
- P3: 优化改进、代码重构

---

## 参考来源
- jwadow/agentic-prompts: Gardener模式
- GitHub Agentic Workflows: PR Automation模板

---

## Pattern-Key
`flow.fix.backup_first` - 修复流程先备份机制