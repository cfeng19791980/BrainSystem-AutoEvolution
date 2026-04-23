# -*- coding: utf-8 -*-
import requests

try:
    r = requests.get('http://localhost:5002/ping', timeout=3)
    print('Server:', r.status_code)
    
    r = requests.get('http://localhost:5002/knowledge/graph')
    graph = r.json()
    nodes = len(graph.get('nodes', {}))
    edges = len(graph.get('edges', []))
    print(f'Knowledge Graph: {nodes} nodes, {edges} edges')
    
    r = requests.get('http://localhost:5002/knowledge/chain/vector_search')
    chain = r.json()
    print(f'Chain: {chain.get("steps", 0)} steps')
    
    print('All OK!')
except Exception as e:
    print(f'Server error: {e}')