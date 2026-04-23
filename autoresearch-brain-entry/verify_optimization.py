# -*- coding: utf-8 -*-
"""
AutoResearch 验证优化效果
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\brain-system\core')

import json
import time
import urllib.request

TEST_CASES_FILE = r'C:\Users\Administrator\.openclaw\brain-system\autoresearch-brain-entry\test_cases.json'

def load_test_cases():
    with open(TEST_CASES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)['test_cases']

def test_api_optimization():
    """测试API响应时间优化"""
    test_cases = load_test_cases()[:20]  # 测试20个
    
    print("Phase 1: 首次调用（建立缓存）...")
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
    
    print("\n" + "="*50)
    print("优化验证结果:")
    print("="*50)
    print(f"Baseline (首次): {avg_first:.1f}ms")
    print(f"优化后 (缓存):   {avg_cached:.1f}ms")
    print(f"改进:            {improvement:.1f}%")
    
    if improvement > 20:
        print("状态:           ✅ 优化成功!")
    else:
        print("状态:           ⚠️ 效果有限")
    print("="*50)
    
    # 检查缓存统计
    req = urllib.request.Request('http://127.0.0.1:5002/embedding_status')
    response = urllib.request.urlopen(req, timeout=5)
    status = json.loads(response.read().decode('utf-8'))
    print(f"\n缓存条目: {status.get('cache_size', 'N/A')}")
    print(f"缓存命中: {status.get('cache_hits', 'N/A')}")

if __name__ == "__main__":
    test_api_optimization()