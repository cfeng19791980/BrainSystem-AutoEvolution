# -*- coding: utf-8 -*-
"""单独测试归一化函数"""
import hashlib
import re

NORMALIZE_KEYWORDS = {
    '测试': ['test', '检测', '验证', '试试', '测试一下', '帮我测试', '系统测试'],
    '修复': ['fix', 'bug', '错误', '改正', '解决', '修复一下', '帮我修复'],
    '检查': ['check', '查看', '诊断', 'inspect', '检查一下', '帮我检查', '看看'],
    '部署': ['deploy', '发布', '上线', '部署一下', '帮我部署'],
    '优化': ['optimize', '改进', '提升', '优化一下', '帮我优化'],
    '调试': ['debug', '排查', '调试一下', '帮我调试'],
    '分析': ['analyze', '分析一下', '帮我分析'],
    '添加': ['add', '新增', '创建', '添加一个', '帮我添加'],
    '更新': ['update', '刷新', '同步', '更新一下', '帮我更新'],
    '重启': ['restart', '重新启动', '重启一下', '帮我重启'],
    '清理': ['clean', '删除', 'remove', '清理一下', '帮我清理'],
}

brain_patterns = ['brain_entry', 'analyzer', 'gateway', 'memory', 'embedding', 'vector']

def normalize_intent_key(text):
    """语义归一化 - 将不同话术收敛到同一缓存key"""
    text_lower = text.lower().strip()
    
    # 1. 关键词归一化
    normalized_keywords = []
    for core_keyword, variants in NORMALIZE_KEYWORDS.items():
        for variant in variants:
            if variant in text_lower:
                normalized_keywords.append(core_keyword)
                break
    
    # 2. 提取目标名词
    english_words = re.findall(r'[a-zA-Z_]+', text)
    chinese_keywords = []
    for pattern in brain_patterns:
        if pattern in text_lower:
            chinese_keywords.append(pattern)
    
    # 3. 合并并排序
    all_keywords = sorted(set(normalized_keywords + english_words + chinese_keywords))
    
    # 4. 生成统一key
    if all_keywords:
        normalized_key = '|'.join(all_keywords)
    else:
        normalized_key = text_lower[:50]
    
    return hashlib.md5(normalized_key.encode('utf-8')).hexdigest()

# 测试
print('语义归一化测试:')
print('='*60)

test_cases = [
    '测试系统',
    '系统测试一下',
    '帮我测试下系统',
    '修复brain_entry',
    'brain_entry修复一下',
    '帮我修复brain_entry',
]

keys = {}
for text in test_cases:
    key = normalize_intent_key(text)
    keys[key] = keys.get(key, 0) + 1
    print(f'{text} -> key={key[:16]}...')

print()
print('归一化效果:')
unique_keys = len(keys)
total_inputs = len(test_cases)
hit_rate = (total_inputs - unique_keys) / total_inputs * 100
print(f'  输入数量: {total_inputs}')
print(f'  缓存key数量: {unique_keys}')
print(f'  去重率: {hit_rate:.1f}%')

if unique_keys == 2:  # 测试类和修复类各一个
    print('  ✅ 语义归一化成功！同类话术收敛到同一key')