# -*- coding: utf-8 -*-
"""P7-P9功能测试"""
import requests
import json

BASE = 'http://localhost:5002'

print('='*60)
print('P7-P9功能测试')
print('='*60)

# P7-1: experiment_parser
print('\n[P7-1] experiment_parser')
r = requests.post(BASE + '/knowledge/parse')
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'Parsed: {data.get("parsed", 0)} experiments')
    for exp in data.get('experiments', [])[:5]:
        print(f'  - exp_{exp["id"]}: {exp["conclusion"]}')

# P7-2: brain_rule_miner
print('\n[P7-2] brain_rule_miner')
r = requests.post(BASE + '/knowledge/mine')
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'Mined: {data.get("mined", 0)} rules')
    for rule in data.get('rules', [])[:5]:
        print(f'  - {rule["keyword"]} -> {rule["intent"]}')

# P8: brain_hook
print('\n[P8] brain_hook')
r = requests.post(BASE + '/brain/hook', json={'query': 'cache优化'})
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'Query: {data.get("query")}')
    print(f'Related: {len(data.get("related_methods", []))}')
    print(f'Recommendation: {data.get("recommendation")}')

# P9: autoresearch_hook
print('\n[P9] autoresearch_hook')
r = requests.post(BASE + '/autoresearch/check', json={'experiment': 'embedding缓存实验'})
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'Proposed: {data.get("proposed")}')
    print(f'Similar: {len(data.get("similar", []))} experiments')
    print(f'Recommendation: {data.get("recommendation")}')
    print(f'Safe: {data.get("safe")}')

# 知识图谱统计
print('\n[Knowledge Graph Stats]')
r = requests.get(BASE + '/knowledge/graph')
if r.status_code == 200:
    graph = r.json()
    nodes = graph.get('nodes', {})
    types = {}
    for node_id, node_data in nodes.items():
        t = node_data.get('type', 'unknown')
        types[t] = types.get(t, 0) + 1
    print(f'Total nodes: {len(nodes)}')
    for t, count in types.items():
        print(f'  - {t}: {count}')

print('\n' + '='*60)
print('测试完成!')
print('='*60)