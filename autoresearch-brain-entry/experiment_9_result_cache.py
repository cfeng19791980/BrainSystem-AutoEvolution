# -*- coding: utf-8 -*-
"""
AutoResearch 实验 #9: 结果缓存
目标：缓存完整API响应，实现二次访问5ms响应
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\brain-system\core')

import json
import time
import hashlib
import urllib.request

TEST_CASES_FILE = r'C:\Users\Administrator\.openclaw\brain-system\autoresearch-brain-entry\test_cases.json'

def load_test_cases():
    with open(TEST_CASES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)['test_cases']

def test_result_cache():
    """测试结果缓存效果"""
    test_cases = load_test_cases()[:20]
    
    print("="*60)
    print("实验 #9: 结果缓存测试")
    print("="*60)
    
    # Phase 1: 首次调用（无缓存）
    print("\nPhase 1: 首次调用（建立缓存）...")
    first_times = []
    
    for case in test_cases:
        content = case['content']
        data = json.dumps({"content": content}).encode('utf-8')
        
        t0 = time.time()
        req = urllib.request.Request(
            'http://127.0.0.1:5002/entry',
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read().decode('utf-8'))
        elapsed = time.time() - t0
        first_times.append(elapsed * 1000)
    
    avg_first = sum(first_times) / len(first_times)
    print(f"首次平均: {avg_first:.1f}ms")
    
    # Phase 2: 重复调用（使用缓存）
    print("\nPhase 2: 重复调用（使用缓存）...")
    cached_times = []
    
    for case in test_cases:
        content = case['content']
        data = json.dumps({"content": content}).encode('utf-8')
        
        t0 = time.time()
        req = urllib.request.Request(
            'http://127.0.0.1:5002/entry',
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read().decode('utf-8'))
        elapsed = time.time() - t0
        cached_times.append(elapsed * 1000)
    
    avg_cached = sum(cached_times) / len(cached_times)
    print(f"缓存后平均: {avg_cached:.1f}ms")
    
    # 计算
    improvement = (avg_first - avg_cached) / avg_first * 100
    expected_improvement = avg_cached < 10  # 期望<10ms
    
    print("\n" + "="*60)
    print("结果:")
    print("="*60)
    print(f"Baseline: {avg_first:.1f}ms")
    print(f"缓存后:   {avg_cached:.1f}ms")
    print(f"改进:     {improvement:.1f}%")
    
    if expected_improvement:
        print("决策:     KEEP ✅ (结果缓存生效)")
    else:
        print("决策:     需要在API层实现缓存")
    print("="*60)
    
    return {
        'first_avg_ms': avg_first,
        'cached_avg_ms': avg_cached,
        'improvement_pct': improvement
    }

if __name__ == "__main__":
    test_result_cache()