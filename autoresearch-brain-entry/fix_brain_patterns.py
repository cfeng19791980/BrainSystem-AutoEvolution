# -*- coding: utf-8 -*-
"""修改brain_patterns关键词"""

import re

# 读取文件
with open(r'C:\Users\Administrator\.openclaw\brain-system\core\brain_entry.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找brain_patterns定义
pattern = r"brain_patterns\s*=\s*\[[^\]]+\]"
match = re.search(pattern, content)

if match:
    old_text = match.group(0)
    # 新增技术术语关键词
    new_text = """brain_patterns = [r'brain', r'知识', r'智能决策', r'查询.*知识', r'记忆',
                    # AutoResearch优化: 新增技术术语关键词
                    r'embedding', r'向量', r'BGE', r'FAISS', r'M3',
                    r'模型', r'知识库', r'memory', r'pattern',
                    r'feedback', r'索引', r'数据库', r'api', r'配置']"""
    
    content = content.replace(old_text, new_text)
    
    # 写回文件
    with open(r'C:\Users\Administrator\.openclaw\brain-system\core\brain_entry.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('brain_patterns已更新!')
else:
    print('未找到brain_patterns')