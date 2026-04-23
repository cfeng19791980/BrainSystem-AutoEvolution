# -*- coding: utf-8 -*-
"""
Brain Entry AutoResearch - 评估脚本
客观评估Brain Entry性能：响应时间 + 意图准确率
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import json
import time
import importlib
import subprocess
from datetime import datetime

# 配置
TEST_CASES_FILE = os.path.join(os.path.dirname(__file__), 'test_cases.json')
BRAIN_ENTRY_PATH = r'C:\Users\Administrator\.openclaw\brain-system\core'
TIME_BUDGET = 30  # 秒

def load_test_cases():
    """加载测试数据"""
    with open(TEST_CASES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)['test_cases']

def evaluate_brain_entry():
    """
    评估Brain Entry性能
    
    返回:
    - avg_time_ms: 平均响应时间(毫秒)
    - intent_accuracy: 意图识别准确率
    - keyword_recall: 关键词召回率
    - score: 综合评分(越高越好)
    """
    test_cases = load_test_cases()
    
    # 方法1: subprocess完全隔离（推荐，避免缓存）
    # 创建临时评估脚本
    eval_script = '''
import sys
sys.path.insert(0, r"C:\\Users\\Administrator\\.openclaw\\brain-system\\core")
import brain_entry
import json
import time

test_cases = json.loads(sys.argv[1])
total_time = 0
intent_correct = 0
keyword_found = 0

for case in test_cases:
    t0 = time.time()
    result = brain_entry.brain_entry(case['content'])
    elapsed = time.time() - t0
    total_time += elapsed
    
    # 检查意图
    detected_intent = result.get('intent', {}).get('type', 'unknown')
    if detected_intent == case['expected_intent']:
        intent_correct += 1
    
    # 检查关键词召回
    result_text = json.dumps(result, ensure_ascii=False).lower()
    expected_kw = case.get('expected_keywords', [])
    if expected_kw:
        found = sum(1 for kw in expected_kw if kw.lower() in result_text)
        keyword_found += found / len(expected_kw)

n = len(test_cases)
avg_time_ms = total_time * 1000 / n
intent_accuracy = intent_correct / n
keyword_recall = keyword_found / n

print(f"avg_time_ms:{avg_time_ms:.1f}")
print(f"intent_accuracy:{intent_accuracy:.4f}")
print(f"keyword_recall:{keyword_recall:.4f}")
'''
    
    # 运行评估
    try:
        result = subprocess.run(
            ['python', '-c', eval_script, json.dumps(test_cases)],
            capture_output=True,
            text=True,
            timeout=TIME_BUDGET + 10
        )
        
        # 解析输出
        output = result.stdout
        metrics = {}
        for line in output.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                try:
                    metrics[key] = float(value)
                except:
                    pass
        
        if not metrics:
            # 失败，使用默认值
            metrics = {
                'avg_time_ms': 999.0,
                'intent_accuracy': 0.0,
                'keyword_recall': 0.0
            }
        
        # 计算综合评分
        # 评分 = 准确率权重 - 时间惩罚
        # intent_accuracy 0-1, keyword_recall 0-1, avg_time_ms ms
        score = (metrics['intent_accuracy'] * 60 + metrics['keyword_recall'] * 40) - metrics['avg_time_ms'] * 0.05
        
        metrics['score'] = score
        
        # 输出标准格式
        print("---")
        print(f"avg_time_ms:      {metrics['avg_time_ms']:.1f}")
        print(f"intent_accuracy:  {metrics['intent_accuracy']:.4f}")
        print(f"keyword_recall:   {metrics['keyword_recall']:.4f}")
        print(f"score:            {metrics['score']:.2f}")
        print("---")
        
        return metrics
        
    except subprocess.TimeoutExpired:
        print("---")
        print("avg_time_ms:      999.0")
        print("intent_accuracy:  0.0")
        print("keyword_recall:   0.0")
        print("score:            0.0")
        print("status:           timeout")
        print("---")
        return {'avg_time_ms': 999.0, 'intent_accuracy': 0.0, 'keyword_recall': 0.0, 'score': 0.0}
    
    except Exception as e:
        print(f"评估失败: {e}")
        return {'avg_time_ms': 999.0, 'intent_accuracy': 0.0, 'keyword_recall': 0.0, 'score': 0.0}

if __name__ == "__main__":
    metrics = evaluate_brain_entry()