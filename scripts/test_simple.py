# -*- coding: utf-8 -*-
"""简化生产测试"""
import requests

BASE_URL = 'http://localhost:5002'

print('=' * 60)
print('简化生产测试')
print('=' * 60)

# 1. Ping测试
r = requests.get(f'{BASE_URL}/ping')
print(f'Ping: {r.status_code} - {r.json()}')

# 2. Health测试
r = requests.get(f'{BASE_URL}/health')
print(f'Health: {r.status_code} - {r.json()}')

# 3. Entry测试
r = requests.post(f'{BASE_URL}/entry', json={'content': 'test', 'userAction': 'query'}, timeout=10)
print(f'Entry: {r.status_code}')
if r.status_code == 200:
    result = r.json()
    intent = result.get('brain_context', {}).get('intent', {})
    print(f'  Intent: {intent.get("type", "unknown")}')

# 4. Pattern统计测试
r = requests.get(f'{BASE_URL}/patterns/stats')
print(f'Patterns: {r.status_code}')
if r.status_code == 200:
    patterns = r.json()
    print(f'  Count: {len(patterns.get("patterns", []))}')

# 5. 新端点测试
print('\n[Test 4] 缓存健康报告')
r = requests.get(f'{BASE_URL}/optimize/cache/health')
print(f'  状态: {r.status_code}')
if r.status_code == 200:
    health = r.json()
    print(f'  缓存项数: {health.get("total_cache_items", 0)}')
    print(f'  平均质量: {health.get("avg_quality", 0):.2f}')
    print(f'  健康: {"YES" if health.get("healthy", False) else "NO"}')

print('\n[Test 5] 性能报告')
r = requests.get(f'{BASE_URL}/optimize/performance')
print(f'  状态: {r.status_code}')
if r.status_code == 200:
    perf = r.json()
    if 'total_requests' in perf:
        print(f'  总请求: {perf.get("total_requests", 0)}')
        print(f'  平均响应: {perf.get("avg_response_time_ms", 0):.1f}ms')
        print(f'  缓存命中率: {perf.get("cache_hit_rate", 0):.1f}%')
    else:
        print(f'  消息: {perf.get("message", "unknown")}')

print('\n[Test 6] 任务质量打分')
r = requests.post(f'{BASE_URL}/optimize/quality/score', json={
    'intent_match': True,
    'response_time': 50,
    'error_count': 0,
    'user_correction': False
})
print(f'  状态: {r.status_code}')
if r.status_code == 200:
    score = r.json()
    print(f'  总分: {score.get("total", 0):.2f}')
    print(f'  等级: {score.get("grade", "unknown")}')

print('\n[Test 7] Pattern自动沉淀')
r = requests.post(f'{BASE_URL}/optimize/patterns/auto')
print(f'  状态: {r.status_code}')
if r.status_code == 200:
    result = r.json()
    print(f'  新Pattern: {result.get("count", 0)}个')

print('=' * 60)
print('测试完成')
print('=' * 60)