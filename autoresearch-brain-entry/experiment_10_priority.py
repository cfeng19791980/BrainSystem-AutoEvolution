# -*- coding: utf-8 -*-
"""
AutoResearch 实验 #10: 意图优先级系统
目标：解决关键词重叠导致的误判
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

def test_priority_system():
    """测试意图优先级效果"""
    # debug → fix误判的case
    debug_cases = [
        "debug一下embedding问题",
        "debug意图识别问题",
        "debug向量搜索",
        "debug embedding错误",
        "debug pattern检测"
    ]
    
    # verify → test误判的case
    verify_cases = [
        "验证系统完整性",
        "验证配置正确性",
        "验证数据一致性"
    ]
    
    print("="*60)
    print("实验 #10: 意图优先级测试")
    print("="*60)
    
    # 测试当前识别
    print("\nDebug误判测试:")
    debug_correct = 0
    for case in debug_cases:
        result = brain_entry.analyze_intent(case)
        detected = result.get('type', 'unknown')
        if detected == 'flow_debug':
            debug_correct += 1
            print(f"✅ {case} -> {detected}")
        else:
            print(f"❌ {case} -> {detected} (expected: flow_debug)")
    
    print(f"\nDebug准确率: {debug_correct}/{len(debug_cases)}")
    
    print("\nVerify误判测试:")
    verify_correct = 0
    for case in verify_cases:
        result = brain_entry.analyze_intent(case)
        detected = result.get('type', 'unknown')
        if detected == 'flow_verify':
            verify_correct += 1
            print(f"✅ {case} -> {detected}")
        else:
            print(f"❌ {case} -> {detected} (expected: flow_verify)")
    
    print(f"\nVerify准确率: {verify_correct}/{len(verify_cases)}")
    
    print("\n" + "="*60)
    print("分析:")
    print("="*60)
    
    if debug_correct < len(debug_cases):
        print("Debug误判原因: 'debug'关键词可能不被识别，或被其他关键词覆盖")
        print("建议: 添加'debug'到FLOW_TEMPLATES['debug']关键词列表")
    
    if verify_correct < len(verify_cases):
        print("Verify误判原因: '验证'关键词被FLOW_TEMPLATES['test']匹配")
        print("建议: 将'验证'从test移到verify，或添加优先级")

if __name__ == "__main__":
    test_priority_system()