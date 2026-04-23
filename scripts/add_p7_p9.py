# -*- coding: utf-8 -*-
"""
P8/P9功能追加脚本
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

# P8: brain_hook代码
p8_code = '''
# ============================================================
# P8: brain_hook - 与Gateway决策联动
# ============================================================

def brain_pre_decision_hook(user_query):
    """P8: 模型决策前自动调取知识图谱参考"""
    # 查询相关优化方案
    related = semantic_search_methods(user_query, top_k=3)
    
    # 查询相关规则
    matched_rules = []
    for node_id, node_data in KNOWLEDGE_GRAPH['nodes'].items():
        if node_data.get('type') == 'rule' and node_data.get('keyword'):
            if node_data['keyword'] in user_query.lower():
                matched_rules.append({
                    'keyword': node_data['keyword'],
                    'intent': node_data.get('intent'),
                    'flow': node_data.get('flow')
                })
    
    reference = {
        'query': user_query,
        'related_methods': related.get('results', []),
        'matched_rules': matched_rules[:5],
        'recommendation': None,
        'confidence': 0
    }
    
    top = related.get('results', [])
    if top:
        first = top[0]
        reference['recommendation'] = first
        reference['confidence'] = 1
    
    return reference

# ============================================================
# P9: autoresearch_hook - 新实验立项前检索
# ============================================================

def autoresearch_pre_check(proposed_experiment):
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
    }
'''

# API端点代码
api_code = '''
# ============================================================
# P7-P9 API端点
# ============================================================

@app.route('/knowledge/parse', methods=['POST'])
def parse_experiments_endpoint():
    """P7-1: 自动解析实验"""
    result = experiment_parser()
    return jsonify(result)

@app.route('/knowledge/mine', methods=['POST'])
def mine_patterns_endpoint():
    """P7-2: 扫描brain_patterns"""
    result = brain_rule_miner()
    return jsonify(result)

@app.route('/brain/hook', methods=['POST'])
def brain_hook_endpoint():
    """P8: Gateway决策联动"""
    query = request.json.get('query', '') if request.is_json else ''
    result = brain_pre_decision_hook(query)
    return jsonify(result)

@app.route('/autoresearch/check', methods=['POST'])
def autoresearch_check_endpoint():
    """P9: 实验立项前检索"""
    proposed = request.json.get('experiment', '') if request.is_json else ''
    result = autoresearch_pre_check(proposed)
    return jsonify(result)
'''

# 读取原文件
with open(r'C:\Users\Administrator\.openclaw\brain-system\core\brain_entry.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到插入位置 (在NORMALIZE_KEYWORDS之前)
if 'def brain_pre_decision_hook' not in content:
    # 在NORMALIZE_KEYWORDS之前插入P8/P9函数
    insert_pos = content.find('NORMALIZE_KEYWORDS = {')
    if insert_pos > 0:
        content = content[:insert_pos] + p8_code + '\n' + content[insert_pos:]

# 在最后@app.route之前插入API端点
if '@app.route(\'/knowledge/parse\'' not in content:
    # 找到@app.route('/ping')位置
    ping_pos = content.find('@app.route(\'/ping\'')
    if ping_pos > 0:
        content = content[:ping_pos] + api_code + '\n' + content[ping_pos:]

# 写回文件
with open(r'C:\Users\Administrator\.openclaw\brain-system\core\brain_entry.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('P7-P9 functions and APIs added successfully!')