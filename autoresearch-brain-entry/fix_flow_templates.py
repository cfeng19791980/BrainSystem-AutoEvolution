# -*- coding: utf-8 -*-
"""修改FLOW_TEMPLATES"""

import re

# 读取文件
with open(r'C:\Users\Administrator\.openclaw\brain-system\core\brain_entry.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找FLOW_TEMPLATES位置
pattern = r"FLOW_TEMPLATES\s*=\s*\{[^\}]+\}"
match = re.search(pattern, content)

if match:
    old_text = match.group(0)
    new_text = """FLOW_TEMPLATES = {
    'test': ['测试', 'test', '检验', '验证'],
    'fix': ['修复', 'fix', 'bug', '错误', '解决'],
    'check': ['检查', 'check', '查看', '状态', 'inspect'],
    'deploy': ['部署', 'deploy', '发布', '上线'],
    'restart': ['重启', 'restart', '重新启动'],
    'clean': ['清理', 'clean', '删除', 'remove', '清除'],
    'optimize': ['优化', 'optimize', '改进', '提升'],
    'debug': ['调试', 'debug', '排查'],
    'add': ['添加', 'add', '新增', '增加', '创建'],
    'update': ['更新', 'update', '刷新', '同步'],
    'autoresearch': ['autoresearch', '自主研究', 'overnight优化', 'AI实验', '自动优化'],
    # AutoResearch优化: 新增5个意图类型
    'analyze': ['分析', 'analyze', '统计', '趋势', '瓶颈'],
    'import': ['导入', 'import', '载入', '加载'],
    'export': ['导出', 'export', '输出', '保存'],
    'sync': ['同步', 'sync', '对齐', '一致性'],
    'verify': ['验证', 'verify', '确认', '完整性'],
}"""
    
    content = content.replace(old_text, new_text)
    
    # 写回文件
    with open(r'C:\Users\Administrator\.openclaw\brain-system\core\brain_entry.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('FLOW_TEMPLATES已更新!')
else:
    print('未找到FLOW_TEMPLATES')