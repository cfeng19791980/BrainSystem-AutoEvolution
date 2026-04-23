# -*- coding: utf-8 -*-
"""
AutoResearch 实验 #3: 优化search_memory
策略：FTS预筛选 + embedding缓存
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\brain-system\core')

import os
import json
import time

TEST_CASES_FILE = os.path.join(os.path.dirname(__file__), 'test_cases.json')

def load_test_cases():
    with open(TEST_CASES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)['test_cases']

def experiment_3_fts_first():
    """实验3: FTS预筛选后再embedding"""
    import brain_entry
    
    test_cases = load_test_cases()[:10]
    
    print("测试策略：先FTS筛选，再embedding精确匹配...")
    
    # 模拟优化后的流程
    total_time = 0
    
    for case in test_cases:
        content = case['content']
        
        t0 = time.time()
        
        # Step 1: 快速FTS预筛选（假设10ms）
        # 这里我们测实际FTS时间
        # brain_entry已经有FTS fallback
        
        # Step 2: embedding search
        result = brain_entry.search_memory(content)
        
        elapsed = time.time() - t0
        total_time += elapsed
    
    avg_time = total_time * 1000 / len(test_cases)
    
    print(f"\n当前平均时间: {avg_time:.1f}ms")
    print(f"Baseline: 172.6ms")
    
    return avg_time

def experiment_4_embedding_cache():
    """实验4: 测试embedding是否可缓存"""
    import brain_entry
    
    print("\n测试embedding缓存效果...")
    
    # 同一个query重复调用
    query = "brain hook是如何实现的"
    
    times = []
    for i in range(5):
        t0 = time.time()
        result = brain_entry.search_memory(query)
        elapsed = time.time() - t0
        times.append(elapsed * 1000)
        print(f"  第{i+1}次: {elapsed*1000:.1f}ms")
    
    print(f"\n首次: {times[0]:.1f}ms")
    print(f"后续平均: {sum(times[1:])/len(times[1:]):.1f}ms")
    
    if times[-1] < times[0] * 0.5:
        print("✅ embedding有缓存效果！")
    else:
        print("❌ embedding无缓存，每次都重新计算")

def analyze_search_internal():
    """分析search_memory内部耗时"""
    import brain_entry
    
    print("\n分析search_memory内部瓶颈...")
    
    query = "brain hook是如何实现的"
    
    # 测embedding时间
    t0 = time.time()
    vector = brain_entry.EmbeddingProvider.get_embedding(query)
    embed_time = time.time() - t0
    print(f"embedding耗时: {embed_time*1000:.1f}ms")
    
    # 测FAISS搜索时间
    t0 = time.time()
    results = brain_entry.vector_engine.search(vector, top_k=5)
    faiss_time = time.time() - t0
    print(f"FAISS搜索耗时: {faiss_time*1000:.1f}ms")
    
    print(f"\nembedding占比: {embed_time/(embed_time+faiss_time)*100:.1f}%")
    print(f"FAISS占比: {faiss_time/(embed_time+faiss_time)*100:.1f}%")

if __name__ == "__main__":
    print("="*50)
    print("AutoResearch 实验 #3-4: 深度瓶颈分析")
    print("="*50)
    
    experiment_4_embedding_cache()
    analyze_search_internal()