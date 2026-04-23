# -*- coding: utf-8 -*-
"""分析剩余28%意图识别误差"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import urllib.request
import json

API_URL = "http://127.0.0.1:5002/entry"
TEST_CASES = r'C:\Users\Administrator\.openclaw\brain-system\autoresearch-brain-entry\test_cases.json'

def load_cases():
    with open(TEST_CASES, 'r', encoding='utf-8') as f:
        return json.load(f)['test_cases']

def call_api(content):
    data = json.dumps({'content': content}).encode('utf-8')
    req = urllib.request.Request(API_URL, data=data, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read().decode('utf-8'))

def analyze_errors():
    cases = load_cases()
    errors = []
    
    # 清空缓存确保准确测试
    for case in cases:
        result = call_api(case['content'])
        intent = result.get('brain_context', {}).get('intent', {})
        detected = intent.get('type', 'unknown')
        expected = case['expected_intent']
        
        if detected != expected:
            errors.append({
                'content': case['content'],
                'expected': expected,
                'detected': detected,
                'confidence': intent.get('confidence', 0)
            })
    
    # 分类统计
    print("="*60)
    print(f"误差分析: {len(errors)}/{len(cases)} ({len(errors)/len(cases)*100:.1f}%)")
    print("="*60)
    
    # 按expected分类
    by_expected = {}
    for e in errors:
        key = e['expected']
        if key not in by_expected:
            by_expected[key] = []
        by_expected[key].append(e)
    
    print("\n按预期意图分类:")
    for exp, errs in sorted(by_expected.items(), key=lambda x: -len(x[1])):
        print(f"\n{exp} (误判{len(errs)}次):")
        for e in errs[:5]:  # 只显示前5个
            print(f"  ❌ '{e['content']}' → {e['detected']} (conf:{e['confidence']:.2f})")
    
    # 按detected分类
    by_detected = {}
    for e in errors:
        key = e['detected']
        if key not in by_detected:
            by_detected[key] = []
        by_detected[key].append(e)
    
    print("\n\n按实际检测结果分类:")
    for det, errs in sorted(by_detected.items(), key=lambda x: -len(x[1])):
        print(f"\n{det} (误判{len(errs)}次):")
        for e in errs[:5]:
            print(f"  ❌ '{e['content']}' (应为{e['expected']})")

if __name__ == "__main__":
    analyze_errors()