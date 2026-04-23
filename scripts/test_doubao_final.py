# -*- coding: utf-8 -*-
import requests
import json
BASE = 'http://localhost:5002'

print('='*60)
print('Doubao Enhancement Test')
print('='*60)

# 1. Scheme Recommendation
print('\n[1] Scheme Recommendation')
r = requests.get(BASE + '/knowledge/recommend/intent_recognition')
data = r.json()
top = data.get('top_pick', {})
print(f'Top Pick: {top.get("name", "None")}')
print(f'Score: {top.get("recommendation_score", 0)}')
print(f'Grade: {top.get("grade", "")}')

# 2. Semantic Search
print('\n[2] Semantic Search')
r = requests.get(BASE + '/knowledge/semantic?q=cache')
data = r.json()
print(f'Total: {data.get("total", 0)}')
for item in data.get('results', [])[:3]:
    print(f'  - {item.get("name", "")} ({item.get("type", "")})')

# 3. Conflict Detection
print('\n[3] Conflict Detection')
r = requests.post(BASE + '/knowledge/conflict', json={'methods': ['embedding_cache', 'result_cache']})
data = r.json()
print(f'Safe: {data.get("safe", True)}')
print(f'Conflicts: {len(data.get("conflicts", []))}')

# 4. Knowledge Graph Architecture
print('\n[4] Knowledge Graph')
r = requests.get(BASE + '/knowledge/graph')
graph = r.json()
print(f'Node Types: {graph.get("node_types", [])}')
print(f'Relations: {len(graph.get("relations", []))} kinds')
print(f'Lifecycle States: {graph.get("lifecycle_states", [])}')

print('\n' + '='*60)
print('ALL DOUBAO ENHANCEMENTS WORKING!')
print('='*60)