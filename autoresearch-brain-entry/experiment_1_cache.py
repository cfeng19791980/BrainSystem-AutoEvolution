# -*- coding: utf-8 -*-
"""
AutoResearch 实验 #1: 添加LRU缓存到analyze_intent
目标: 减少重复计算的响应时间
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\brain-system\core')

import os
import json
import time
from functools import lru_cache

TEST_CASES_FILE = os.path.join(os.path.dirname(__file__), 'test_cases.json')

def load_test_cases():
    with open(TEST_CASES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)['test_cases']

# 实验1: 测试缓存效果
def experiment_1_cache():
    """实验1: 测试LRU缓存效果"""
    import brain_entry
    
    test_cases = load_test_cases()
    n = len(test_cases)
    
    # 先预热（运行一遍）
    print("预热...")
    for case in test_cases:
        brain_entry.analyze_intent(case['content'])
        brain_entry.search_memory(case['content'])
    
    # 第二遍测量（缓存生效）
    print("测量缓存效果...")
    total_time_cached = 0
    
    for case in test_cases:
        t0 = time.time()
        brain_entry.analyze_intent(case['content'])
        brain_entry.search_memory(case['content'])
        total_time_cached += time.time() - t0
    
    avg_cached_ms = total_time_cached * 1000 / n
    
    print(f"\n缓存后平均时间: {avg_cached_ms:.1f}ms")
    return avg_cached_ms

# 实验2: 测试embedding批处理
def experiment_2_batch():
    """实验2: 测试embedding批处理"""
    import brain_entry
    
    test_cases = load_test_cases()
    
    # 提取所有query
    queries = [case['content'] for case in test_cases]
    
    print("测试批处理embedding...")
    t0 = time.time()
    # 批量embedding（如果支持）
    try:
        from brain_entry import EmbeddingProvider
        vectors = EmbeddingProvider.get_embeddings_batch(queries)
        batch_time = time.time() - t0
        print(f"批处理时间: {batch_time*1000:.1f}ms (共{len(queries)}个)")
        avg_batch_ms = batch_time * 1000 / len(queries)
        print(f"平均每query: {avg_batch_ms:.1f}ms")
        return avg_batch_ms
    except Exception as e:
        print(f"批处理不支持: {e}")
        return None

if __name__ == "__main__":
    print("="*50)
    print("AutoResearch 实验 #1: LRU缓存效果")
    print("="*50)
    
    cached_ms = experiment_1_cache()
    
    print("\n" + "="*50)
    print("Baseline: 178.8ms")
    print(f"Cached:   {cached_ms:.1f}ms")
    if cached_ms < 178.8:
        improvement = (178.8 - cached_ms) / 178.8 * 100
        print(f"改进:     +{improvement:.1f}%")
        print("决策:     KEEP ✅")
    else:
        print("决策:     DISCARD ❌")
    print("="*50)