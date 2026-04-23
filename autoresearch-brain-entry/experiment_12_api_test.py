# -*- coding: utf-8 -*-
"""
AutoResearch 实验 #12: 真实API性能测试
通过HTTP调用测试缓存效果
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import urllib.request
import json
import time

API_URL = "http://127.0.0.1:5002/entry"
TEST_CASES_FILE = r'C:\Users\Administrator\.openclaw\brain-system\autoresearch-brain-entry\test_cases.json'

def load_test_cases():
    with open(TEST_CASES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)['test_cases']

def call_api(content, user_action='query'):
    data = json.dumps({'content': content, 'userAction': user_action}).encode('utf-8')
    req = urllib.request.Request(API_URL, data=data, headers={'Content-Type': 'application/json'})
    start = time.time()
    response = urllib.request.urlopen(req, timeout=30)
    elapsed = (time.time() - start) * 1000
    result = json.loads(response.read().decode('utf-8'))
    return elapsed, result

def test_real_performance():
    cases = load_test_cases()
    
    print("="*60)
    print("实验 #12: 真实API性能测试")
    print("="*60)
    
    # Phase 1: 预热缓存（10次重复调用）
    print("\nPhase 1: 预热缓存...")
    warmup_cases = cases[:10]
    for i in range(3):  # 每个case调用3次
        for case in warmup_cases:
            call_api(case['content'])
    print("缓存预热完成")
    
    # Phase 2: 测试全部case（首次调用）
    print("\nPhase 2: 测试99个case（首次调用）...")
    times = []
    correct = 0
    total = len(cases)
    
    for case in cases:
        elapsed, result = call_api(case['content'])
        times.append(elapsed)
        
        intent = result.get('brain_context', {}).get('intent', {})
        detected = intent.get('type', 'unknown')
        expected = case['expected_intent']
        
        if detected == expected:
            correct += 1
    
    avg_time = sum(times) / len(times)
    accuracy = correct / total * 100
    
    print(f"\n首次调用结果:")
    print(f"  平均响应时间: {avg_time:.1f}ms")
    print(f"  意图准确率: {accuracy:.2f}% ({correct}/{total})")
    
    # Phase 3: 重复调用（测试结果缓存）
    print("\nPhase 3: 重复调用（测试结果缓存）...")
    repeat_times = []
    for case in cases[:20]:  # 测试前20个case的缓存效果
        elapsed, _ = call_api(case['content'])
        repeat_times.append(elapsed)
    
    cache_avg = sum(repeat_times) / len(repeat_times)
    print(f"  缓存命中平均: {cache_avg:.1f}ms")
    print(f"  缓存改进: {(avg_time - cache_avg) / avg_time * 100:.1f}%")
    
    print("\n" + "="*60)
    print("总结:")
    print("="*60)
    print(f"首次调用: {avg_time:.1f}ms, 准确率{accuracy:.2f}%")
    print(f"缓存命中: {cache_avg:.1f}ms")

if __name__ == "__main__":
    test_real_performance()