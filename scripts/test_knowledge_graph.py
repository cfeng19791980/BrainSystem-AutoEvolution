# -*- coding: utf-8 -*-
"""知识图谱测试"""
import requests

BASE_URL = 'http://localhost:5002'

print('=' * 60)
print('知识图谱测试')
print('=' * 60)

# 1. 获取完整图谱
r = requests.get(f'{BASE_URL}/knowledge/graph')
print(f'完整图谱: {r.status_code}')
if r.status_code == 200:
    graph = r.json()
    nodes = graph.get('nodes', {})
    edges = graph.get('edges', [])
    print(f'  方法节点: {len(nodes)}个')
    print(f'  关系边: {len(edges)}条')
    print(f'  类别: {graph.get("categories", [])}')

# 2. 查询特定方法
print('\n查询embedding_cache:')
r = requests.get(f'{BASE_URL}/knowledge/method/embedding_cache')
print(f'  状态: {r.status_code}')
if r.status_code == 200:
    detail = r.json()
    method = detail.get('method', {})
    print(f'  名称: {method.get("name", "unknown")}')
    print(f'  效果: {method.get("effect", "unknown")}')
    print(f'  来源: {method.get("source", "unknown")}')

# 3. 查询优化链
print('\n查询优化链(intent_recognition):')
r = requests.get(f'{BASE_URL}/knowledge/chain/intent_recognition')
print(f'  状态: {r.status_code}')
if r.status_code == 200:
    chain = r.json()
    print(f'  步数: {chain.get("steps", 0)}')
    for i, step in enumerate(chain.get('chain', [])):
        print(f'  Step {i+1}: {step.get("name", "unknown")} ({step.get("effect", "")})')

# 4. 搜索知识
print('\n搜索"cache":')
r = requests.get(f'{BASE_URL}/knowledge/search?q=cache')
print(f'  状态: {r.status_code}')
if r.status_code == 200:
    results = r.json()
    print(f'  结果数: {results.get("count", 0)}')

# 5. 查询相关方法
print('\n查询result_cache相关方法:')
r = requests.get(f'{BASE_URL}/knowledge/related/result_cache')
print(f'  状态: {r.status_code}')
if r.status_code == 200:
    related = r.json()
    print(f'  依赖: {related.get("depends_on", [])}')
    print(f'  增强: {related.get("enhances", [])}')

print('\n' + '=' * 60)
print('测试完成')
print('=' * 60)