# -*- coding: utf-8 -*-
"""
AutoResearch 实验 #6: 分析意图识别准确率低的原因
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\brain-system\core')

import json
import brain_entry

TEST_CASES_FILE = r'C:\Users\Administrator\.openclaw\brain-system\autoresearch-brain-entry\test_cases.json'

def load_test_cases():
    with open(TEST_CASES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)['test_cases']

def analyze_intent_accuracy():
    """分析意图识别准确率低的case"""
    test_cases = load_test_cases()
    
    correct = 0
    wrong_cases = []
    
    print("分析意图识别错误...")
    
    for case in test_cases:
        content = case['content']
        expected = case['expected_intent']
        
        result = brain_entry.analyze_intent(content)
        detected = result.get('type', 'unknown')
        
        if detected == expected:
            correct += 1
        else:
            wrong_cases.append({
                'content': content[:30],
                'expected': expected,
                'detected': detected
            })
    
    accuracy = correct / len(test_cases)
    
    print(f"\n准确率: {accuracy:.4f} ({correct}/{len(test_cases)})")
    print(f"错误数量: {len(wrong_cases)}")
    
    # 分类错误
    print("\n错误分类:")
    error_patterns = {}
    
    for wc in wrong_cases:
        key = f"{wc['expected']} -> {wc['detected']}"
        if key not in error_patterns:
            error_patterns[key] = []
        error_patterns[key].append(wc['content'])
    
    for pattern, cases in sorted(error_patterns.items(), key=lambda x: -len(x[1])):
        count = len(cases)
        print(f"\n{pattern} ({count}次):")
        for c in cases[:3]:
            print(f"  - {c}")
    
    return {
        'accuracy': accuracy,
        'wrong_count': len(wrong_cases),
        'error_patterns': error_patterns
    }

if __name__ == "__main__":
    analyze_intent_accuracy()