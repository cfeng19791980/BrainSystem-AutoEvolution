# -*- coding: utf-8 -*-
"""
AutoResearch 实验 #7: 优化brain_command识别
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

def test_brain_command_patterns():
    """测试brain_command识别优化"""
    # 当前误判的brain_command案例
    brain_command_cases = [
        "BGE-M3 embedding模型",
        "向量数据库索引方法",
        "memory search流程",
        "FAISS向量搜索原理",
        "embedding模型参数",
        "向量维度设置",
        "知识库结构",
        "memory文件格式",
        "pattern检测原理",
        "feedback学习机制"
    ]
    
    print("测试brain_command识别...")
    
    # 测试当前识别
    correct = 0
    for case in brain_command_cases:
        result = brain_entry.analyze_intent(case)
        detected = result.get('type', 'unknown')
        if detected == 'brain_command':
            correct += 1
            print(f"✅ {case} -> {detected}")
        else:
            print(f"❌ {case} -> {detected} (expected: brain_command)")
    
    accuracy = correct / len(brain_command_cases)
    print(f"\n准确率: {accuracy:.2%} ({correct}/{len(brain_command_cases)})")
    
    # 分析：这些case缺少关键词"brain"、"知识"、"记忆"等
    # 需要添加技术术语关键词
    
    print("\n建议新增关键词:")
    suggestions = [
        "embedding", "向量", "BGE", "FAISS",
        "模型", "知识库", "memory", "pattern",
        "feedback", "索引", "数据库"
    ]
    for kw in suggestions:
        print(f"  - {kw}")

if __name__ == "__main__":
    test_brain_command_patterns()