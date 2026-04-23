# -*- coding: utf-8 -*-
"""豆包增强功能测试"""
import requests

BASE = 'http://localhost:5002'

print('=' * 60)
print('豆包增强功能测试')
print('=' * 60)

# 1. 方案推荐
print('\n[Test 1] 方案推荐 - intent_recognition')
r = requests.get(f'{BASE}/knowledge/recommend/intent_recognition')
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    top = data.get('top_pick')
    if top:
        print(f'  Top Pick: {top.get("name", "")}')
        print(f'  Score: {top.get("recommendation_score", 0)}')
        print(f'  Grade: {top.get("grade", "")}')

# 2. 语义检索
print('\n[Test 2] 语义检索 - "缓存优化"')
r = requests.get(f'{BASE}/knowledge/semantic?q=缓存')
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'  Results: {data.get("total", 0)}')
    for item in data.get('results', [])[:3]:
        print(f'    - {item.get("name", "")} ({item.get("type", "")})')

# 3. 冲突检测
print('\n[Test 3] 冲突检测')
r = requests.post(f'{BASE}/knowledge/conflict', json={'methods': ['embedding_cache', 'result_cache']})
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'  Safe: {data.get("safe", False)}')
    print(f'  Conflicts: {len(data.get("conflicts", []))}')

# 4. 知识图谱统计
print('\n[Test 4] 知识图谱统计')
r = requests.get(f'{BASE}/knowledge/graph')
print(f'Status: {r.status_code}')
if r.status_code == 200:
    graph = r.json()
    print(f'  Node Types: {graph.get("node_types", [])}')
    print(f'  Relations: {len(graph.get("relations", []))} kinds')
    print(f'  Lifecycle States: {graph.get("lifecycle_states", [])}')

print('\n' + '=' * 60)
print('豆包增强功能测试完成')
print('=' * 60)