# -*- coding: utf-8 -*-
"""
AutoResearch 实验 #5: 实现embedding缓存
目标：对相同query缓存embedding结果，减少重复计算
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\brain-system\core')

import os
import json
import time
from functools import lru_cache
import hashlib

TEST_CASES_FILE = os.path.join(os.path.dirname(__file__), 'test_cases.json')

def load_test_cases():
    with open(TEST_CASES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)['test_cases']

# 实验：添加embedding缓存层
class CachedEmbedding:
    """带缓存的embedding包装器"""
    
    _cache = {}  # 全局缓存
    
    @classmethod
    def get_embedding(cls, text):
        # 用hash作为key
        key = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        if key in cls._cache:
            return cls._cache[key]
        
        # 调用原始embedding
        import brain_entry
        vector = brain_entry.EmbeddingProvider.get_embedding(text)
        
        # 缓存结果
        cls._cache[key] = vector
        return vector

def experiment_5_cached_embedding():
    """实验5: 测试embedding缓存效果"""
    import brain_entry
    
    test_cases = load_test_cases()
    n = len(test_cases)
    
    print(f"测试 {n} 个case的embedding缓存效果...")
    
    # 预热：建立缓存
    print("\nPhase 1: 建立缓存...")
    build_time = 0
    for case in test_cases:
        t0 = time.time()
        CachedEmbedding.get_embedding(case['content'])
        build_time += time.time() - t0
    print(f"建立缓存耗时: {build_time*1000:.1f}ms (avg: {build_time*1000/n:.1f}ms/case)")
    print(f"缓存条目: {len(CachedEmbedding._cache)}")
    
    # Phase 2: 使用缓存
    print("\nPhase 2: 使用缓存...")
    cached_time = 0
    for case in test_cases:
        t0 = time.time()
        CachedEmbedding.get_embedding(case['content'])
        cached_time += time.time() - t0
    print(f"缓存后耗时: {cached_time*1000:.1f}ms (avg: {cached_time*1000/n:.1f}ms/case)")
    
    # 计算
    improvement = (build_time - cached_time) / build_time * 100
    
    print("\n" + "="*50)
    print("结果:")
    print("="*50)
    print(f"Baseline平均: {build_time*1000/n:.1f}ms")
    print(f"缓存后平均:   {cached_time*1000/n:.1f}ms")
    print(f"改进:         {improvement:.1f}%")
    
    if improvement > 50:
        print("决策:        KEEP ✅ (建议添加到brain_entry.py)")
    else:
        print("决策:        DISCARD ❌")
    print("="*50)
    
    return {
        'baseline_avg_ms': build_time*1000/n,
        'cached_avg_ms': cached_time*1000/n,
        'improvement_pct': improvement
    }

if __name__ == "__main__":
    experiment_5_cached_embedding()