# -*- coding: utf-8 -*-
"""测试语义归一化缓存命中率"""
import requests
import json

test_cases = [
    '测试系统',
    '系统测试一下',
    '帮我测试下系统',
    '修复brain_entry',
    'brain_entry修复一下',
    '帮我修复brain_entry',
]

print('测试语义归一化缓存命中率:')
print('='*60)

url = 'http://localhost:5002/brain_entry'

for i, text in enumerate(test_cases):
    response = requests.post(url, json={'content': text, 'userAction': 'query'})
    result = response.json()
    intent = result.get('brain_context', {}).get('intent', {})
    elapsed_ms = response.elapsed.total_seconds() * 1000
    cache_hit = 'CACHE HIT' if elapsed_ms < 10 else 'CACHE MISS'
    intent_type = intent.get('type', 'unknown')
    print(f'{i+1}. {text}')
    print(f'   Intent: {intent_type}, Time: {elapsed_ms:.1f}ms, {cache_hit}')
    print()