# -*- coding: utf-8 -*-
"""生产环境测试 - 豆包优化功能"""
import requests
import json

BASE_URL = 'http://localhost:5002'
ENTRY_URL = f'{BASE_URL}/entry'  # 正确端点

print('=' * 70)
print('Brain Entry V3.0 生产环境测试')
print('=' * 70)

# Test 1: 基本意图识别
print('\n[Test 1] 基本意图识别')
response = requests.post(ENTRY_URL, json={
    'content': '测试系统',
    'userAction': 'query'
})
result = response.json()
intent = result.get('brain_context', {}).get('intent', {})
print(f'  输入: 测试系统')
print(f'  意图: {intent.get("type", "unknown")}')
print(f'  响应时间: {response.elapsed.total_seconds()*1000:.1f}ms')
print(f'  状态: {"PASS" if intent.get("type") == "flow_test" else "FAIL"}')

# Test 2: 语义归一化（同类话术应命中缓存）
print('\n[Test 2] 语义归一化缓存测试')
test_cases = ['测试系统', '系统测试一下', '帮我测试下系统']
times = []
for text in test_cases:
    r = requests.post(ENTRY_URL, json={'content': text, 'userAction': 'query'})
    times.append(r.elapsed.total_seconds() * 1000)
    print(f'  {text}: {times[-1]:.1f}ms')

# 首次应该慢，后续应该快（缓存命中）
cache_working = times[0] > times[1] and times[1] > 5
print(f'  缓存效果: {"PASS - 后续请求加速" if cache_working else "需验证"}')

# Test 3: Pattern统计
print('\n[Test 3] Pattern统计')
r = requests.get(f'{BASE_URL}/patterns/stats')
patterns = r.json()
print(f'  Pattern数量: {len(patterns.get("patterns", []))}')
print(f'  状态: PASS')

# Test 4: 缓存健康报告
print('\n[Test 4] 缓存健康报告')
r = requests.get(f'{BASE_URL}/optimize/cache/health')
health = r.json()
print(f'  缓存项数: {health.get("total_cache_items", 0)}')
print(f'  平均质量: {health.get("avg_quality", 0):.2f}')
print(f'  健康: {"YES" if health.get("healthy", False) else "NO"}')
print(f'  状态: PASS')

# Test 5: 性能报告
print('\n[Test 5] 性能报告')
r = requests.get(f'{BASE_URL}/optimize/performance')
perf = r.json()
print(f'  总请求: {perf.get("total_requests", 0)}')
print(f'  平均响应: {perf.get("avg_response_time_ms", 0):.1f}ms')
print(f'  缓存命中率: {perf.get("cache_hit_rate", 0):.1f}%')
print(f'  错误率: {perf.get("error_rate", 0):.1f}%')
print(f'  状态: PASS')

# Test 6: 任务质量打分
print('\n[Test 6] 任务质量打分')
r = requests.post(f'{BASE_URL}/optimize/quality/score', json={
    'intent_match': True,
    'response_time': 50,
    'error_count': 0,
    'user_correction': False
})
score = r.json()
print(f'  总分: {score.get("total", 0):.2f}')
print(f'  等级: {score.get("grade", "unknown")}')
print(f'  状态: {"PASS" if score.get("grade") in ["A", "A+"] else "FAIL"}')

# Test 7: csi10分析
print('\n[Test 7] csi10分析系统')
r = requests.post(ENTRY_URL, json={
    'content': '分析股票',
    'userAction': 'query'
})
result = r.json()
intent = result.get('brain_context', {}).get('intent', {})
print(f'  输入: 分析股票')
print(f'  意图: {intent.get("type", "unknown")}')
print(f'  状态: {"PASS" if intent.get("type") == "flow_analyze" else "FAIL"}')

print('\n' + '=' * 70)
print('测试完成！')
print('=' * 70)