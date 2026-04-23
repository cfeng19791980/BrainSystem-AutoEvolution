# -*- coding: utf-8 -*-
"""
Brain Entry AutoResearch - 简化评估脚本
评估核心组件: analyze_intent + search_memory
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

def evaluate():
    """评估Brain Entry核心组件"""
    import brain_entry
    
    test_cases = load_test_cases()
    n = len(test_cases)
    
    total_time = 0
    intent_correct = 0
    keyword_found = 0
    
    print(f"开始评估 {n} 个测试case...")
    
    for i, case in enumerate(test_cases):
        if i % 20 == 0:
            print(f"进度: {i}/{n}")
        
        content = case['content']
        
        t0 = time.time()
        # 评估两个核心函数
        intent_result = brain_entry.analyze_intent(content)
        search_result = brain_entry.search_memory(content)
        elapsed = time.time() - t0
        total_time += elapsed
        
        # 检查意图
        detected_intent = intent_result.get('type', 'unknown')
        if detected_intent == case['expected_intent']:
            intent_correct += 1
        
        # 检查关键词召回
        result_text = json.dumps(search_result, ensure_ascii=False).lower()
        expected_kw = case.get('expected_keywords', [])
        if expected_kw:
            found = sum(1 for kw in expected_kw if kw.lower() in result_text)
            keyword_found += found / len(expected_kw)
    
    avg_time_ms = total_time * 1000 / n
    intent_accuracy = intent_correct / n
    keyword_recall = keyword_found / n
    
    # 综合评分
    score = (intent_accuracy * 60 + keyword_recall * 40) - avg_time_ms * 0.05
    
    print("\n" + "="*50)
    print("评估结果 (Baseline):")
    print("="*50)
    print(f"avg_time_ms:      {avg_time_ms:.1f}")
    print(f"intent_accuracy:  {intent_accuracy:.4f}")
    print(f"keyword_recall:   {keyword_recall:.4f}")
    print(f"score:            {score:.2f}")
    print("="*50)
    
    # 保存baseline
    baseline_file = os.path.join(os.path.dirname(__file__), 'results', 'baseline.json')
    with open(baseline_file, 'w', encoding='utf-8') as f:
        json.dump({
            'avg_time_ms': avg_time_ms,
            'intent_accuracy': intent_accuracy,
            'keyword_recall': keyword_recall,
            'score': score,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }, f, indent=2)
    print(f"Baseline已保存: {baseline_file}")
    
    return {
        'avg_time_ms': avg_time_ms,
        'intent_accuracy': intent_accuracy,
        'keyword_recall': keyword_recall,
        'score': score
    }

if __name__ == "__main__":
    evaluate()