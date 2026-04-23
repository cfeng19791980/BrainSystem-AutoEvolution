# -*- coding: utf-8 -*-
"""
AutoResearch 实验 #2: 分析性能瓶颈
找出哪个步骤最耗时
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

def analyze_bottleneck():
    """分析性能瓶颈"""
    import brain_entry
    
    test_cases = load_test_cases()[:10]  # 只测10个，快速分析
    
    intent_total = 0
    search_total = 0
    
    print("分析10个测试case的耗时分布...")
    
    for case in test_cases:
        content = case['content']
        
        # 测analyze_intent
        t0 = time.time()
        intent = brain_entry.analyze_intent(content)
        intent_time = time.time() - t0
        intent_total += intent_time
        
        # 测search_memory
        t0 = time.time()
        search = brain_entry.search_memory(content)
        search_time = time.time() - t0
        search_total += search_time
        
        print(f"  {content[:20]:20s} intent:{intent_time*1000:.1f}ms search:{search_time*1000:.1f}ms")
    
    print("\n" + "="*50)
    print("瓶颈分析结果:")
    print("="*50)
    print(f"analyze_intent平均: {intent_total*1000/len(test_cases):.1f}ms")
    print(f"search_memory平均:  {search_total*1000/len(test_cases):.1f}ms")
    print(f"search占比:         {search_total/(intent_total+search_total)*100:.1f}%")
    print("="*50)
    
    return {
        'intent_avg_ms': intent_total*1000/len(test_cases),
        'search_avg_ms': search_total*1000/len(test_cases),
        'search_pct': search_total/(intent_total+search_total)*100
    }

if __name__ == "__main__":
    analyze_bottleneck()