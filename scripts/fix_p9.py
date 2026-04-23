# -*- coding: utf-8 -*-
"""修复P9函数"""
with open(r'C:\Users\Administrator\.openclaw\brain-system\core\brain_entry.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到P9函数并替换
old_func = '''def autoresearch_pre_check(proposed_experiment):
    """P9: 新实验立项前检索，避免重复造轮子"""
    similar_experiments = []
    for node_id, node_data in KNOWLEDGE_GRAPH['nodes'].items():
        if node_data.get('type') == 'experiment':
            exp_name = node_data.get('name', '').lower()
            if proposed_experiment.lower() in exp_name:
                similar_experiments.append({
                    'id': node_id,
                    'name': node_data.get('name'),
                    'conclusion': node_data.get('conclusion', 'PENDING')
                })

    existing = scheme_recommendation(proposed_experiment.replace('实验', '').replace('测试', '').strip())

    recommendation = 'PROCEED'
    reasons = []

    for exp in similar_experiments:
        if exp['conclusion'] == 'KEEP':
            recommendation = 'SKIP'
            reasons.append(f"已有成功实验: {exp['name']}")
        elif exp['conclusion'] == 'DISCARD':
            recommendation = 'AVOID'
            reasons.append(f"已有失败实验: {exp['name']}")

    if existing.get('top_pick'):
        recommendation = 'REUSE'
        reasons.append(f"已有方案: {existing['top_pick']['name']}")

    return {
        'proposed': proposed_experiment,
        'similar': similar_experiments,
        'solutions': existing.get('recommended', []),
        'recommendation': recommendation,
        'reasons': reasons,
        'safe': recommendation in ['PROCEED', 'REUSE']
    }'''

new_func = '''def autoresearch_pre_check(proposed_experiment):
    """P9: 新实验立项前检索"""
    similar_experiments = []
    for node_id, node_data in KNOWLEDGE_GRAPH['nodes'].items():
        if node_data.get('type') == 'experiment':
            exp_name = node_data.get('name', '').lower()
            proposed_kw = proposed_experiment.lower()
            if proposed_kw in exp_name or any(kw in exp_name for kw in proposed_kw.split()):
                similar_experiments.append({
                    'id': node_id,
                    'name': node_data.get('name'),
                    'conclusion': node_data.get('conclusion', 'PENDING')
                })
    
    # 清理关键词
    clean_kw = proposed_experiment.lower()
    for word in ['实验', '测试', 'experiment', 'test']:
        clean_kw = clean_kw.replace(word, '')
    clean_kw = clean_kw.strip()
    
    existing = scheme_recommendation(clean_kw) if clean_kw else {'recommended': []}

    recommendation = 'PROCEED'
    reasons = []

    for exp in similar_experiments:
        if exp['conclusion'] == 'KEEP':
            recommendation = 'SKIP'
            reasons.append(f"Existing success: {exp['name']}")
        elif exp['conclusion'] == 'DISCARD':
            recommendation = 'AVOID'
            reasons.append(f"Existing failure: {exp['name']}")

    if existing.get('top_pick'):
        recommendation = 'REUSE'
        reasons.append(f"Existing solution: {existing['top_pick']['name']}")

    return {
        'proposed': proposed_experiment,
        'similar': similar_experiments,
        'solutions': existing.get('recommended', []),
        'recommendation': recommendation,
        'reasons': reasons,
        'safe': recommendation in ['PROCEED', 'REUSE']
    }'''

# 替换（使用更宽松的匹配）
import re
pattern = r'def autoresearch_pre_check\(proposed_experiment\):.*?return \{[^}]+\}'
match = re.search(pattern, content, re.DOTALL)
if match:
    content = content[:match.start()] + new_func + content[match.end():]
    print('P9 function replaced')
else:
    print('Pattern not found, trying manual fix')
    # 直接替换函数体
    content = content.replace("proposed_experiment.replace('实验', '').replace('测试', '').strip()", 
                              "proposed_experiment.lower().replace('experiment', '').replace('test', '').strip()")

with open(r'C:\Users\Administrator\.openclaw\brain-system\core\brain_entry.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed P9 function')