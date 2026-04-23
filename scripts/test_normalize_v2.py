# -*- coding: utf-8 -*-
"""改进的语义归一化测试"""
import hashlib
import re

NORMALIZE_KEYWORDS = {
    '测试': ['test', '检测', '验证', '试试', '测试一下', '帮我测试', '系统测试', '测试系统'],
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

# 扩展目标词映射
TARGET_NORMALIZE = {
    '系统': ['系统', 'system', 'sys'],
    'brain_entry': ['brain_entry', 'brainentry', 'brain-entry'],
    'gateway': ['gateway', 'gw'],
}

def normalize_intent_key_v2(text):
    """语义归一化V2 - 更强的收敛能力"""
    text_lower = text.lower().strip()
    
    # 1. 关键词归一化（意图词）
    intent_keywords = []
    for core_keyword, variants in NORMALIZE_KEYWORDS.items():
        for variant in variants:
            if variant.lower() in text_lower:
                intent_keywords.append(core_keyword)
                break
    
    # 2. 目标词归一化
    target_keywords = []
    for core_target, variants in TARGET_NORMALIZE.items():
        for variant in variants:
            if variant.lower() in text_lower:
                target_keywords.append(core_target)
                break
    
    # 3. 英文单词提取（作为补充）
    english_words = re.findall(r'[a-zA-Z_]+', text)
    for word in english_words:
        if word.lower() not in [v.lower() for vs in TARGET_NORMALIZE.values() for v in vs]:
            target_keywords.append(word)
    
    # 4. 合并排序生成key
    all_keywords = sorted(set(intent_keywords + target_keywords))
    
    if all_keywords:
        normalized_key = '|'.join(all_keywords)
    else:
        normalized_key = text_lower[:50]
    
    return hashlib.md5(normalized_key.encode('utf-8')).hexdigest(), normalized_key

# 测试
print('语义归一化V2测试:')
print('='*70)

test_cases = [
    '测试系统',
    '系统测试一下',
    '帮我测试下系统',
    '修复brain_entry',
    'brain_entry修复一下',
    '帮我修复brain_entry',
    '优化gateway',
    '帮我优化gateway',
]

results = {}
for text in test_cases:
    key, normalized_text = normalize_intent_key_v2(text)
    results[key] = results.get(key, {'texts': [], 'normalized': normalized_text})
    results[key]['texts'].append(text)
    print(f'{text} -> "{normalized_text}" -> {key[:16]}...')

print()
print('归一化效果分析:')
print('='*70)
for key, data in results.items():
    texts = data['texts']
    normalized = data['normalized']
    if len(texts) > 1:
        print(f'✅ 收敛成功: "{normalized}"')
        for t in texts:
            print(f'   - {t}')
    else:
        print(f'⚠️ 未收敛: "{normalized}"')
        print(f'   - {texts[0]}')

print()
unique_keys = len(results)
total_inputs = len(test_cases)
hit_rate = (total_inputs - unique_keys) / total_inputs * 100
print(f'统计: 输入{total_inputs}个 → 缓存key{unique_keys}个 → 去重率{hit_rate:.1f}%')