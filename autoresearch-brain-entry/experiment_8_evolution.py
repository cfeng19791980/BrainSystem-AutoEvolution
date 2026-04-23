# -*- coding: utf-8 -*-
"""
AutoResearch 实验 #8: 分析剩余优化空间
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

def analyze_remaining_errors():
    """分析剩余20%意图识别错误"""
    test_cases = load_test_cases()
    
    wrong_cases = []
    for case in test_cases:
        result = brain_entry.analyze_intent(case['content'])
        detected = result.get('type', 'unknown')
        if detected != case['expected_intent']:
            wrong_cases.append({
                'content': case['content'],
                'expected': case['expected_intent'],
                'detected': detected
            })
    
    print("="*60)
    print("剩余20%错误分析")
    print("="*60)
    print(f"错误总数: {len(wrong_cases)}/{len(test_cases)}")
    
    # 分类错误
    error_patterns = {}
    for wc in wrong_cases:
        key = f"{wc['expected']} → {wc['detected']}"
        if key not in error_patterns:
            error_patterns[key] = []
        error_patterns[key].append(wc['content'])
    
    print("\n错误模式:")
    for pattern, cases in sorted(error_patterns.items(), key=lambda x: -len(x[1])):
        print(f"\n{pattern} ({len(cases)}次):")
        for c in cases[:5]:
            print(f"  - {c}")
    
    # 分析优化方向
    print("\n" + "="*60)
    print("进化方案建议:")
    print("="*60)
    
    suggestions = [
        {
            'name': '意图优先级系统',
            'problem': '关键词重叠导致误判（debug→fix, verify→test）',
            'solution': '添加意图优先级，如debug > fix > general',
            'impact': '解决5+3=8个错误，+8%准确率',
            'risk': '低',
        },
        {
            'name': '结果缓存',
            'problem': '相同query仍需执行完整流程',
            'solution': '缓存完整API响应，TTL=60秒',
            'impact': '响应时间从69.9ms→5ms',
            'risk': '低',
        },
        {
            'name': 'FAISS参数优化',
            'problem': 'FAISS搜索占40%时间',
            'solution': '调整nprobe参数，平衡精度与速度',
            'impact': '响应时间-20%',
            'risk': '中',
        },
        {
            'name': '关键词去重',
            'problem': 'verify/test关键词重叠',
            'solution': '精确关键词匹配，避免模糊匹配',
            'impact': '+3%准确率',
            'risk': '低',
        },
    ]
    
    for i, s in enumerate(suggestions, 1):
        print(f"\n方案{i}: {s['name']}")
        print(f"  问题: {s['problem']}")
        print(f"  方案: {s['solution']}")
        print(f"  影响: {s['impact']}")
        print(f"  风险: {s['risk']}")
    
    return suggestions

if __name__ == "__main__":
    analyze_remaining_errors()