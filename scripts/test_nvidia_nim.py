# -*- coding: utf-8 -*-
"""
NVIDIA NIM API 测试脚本
测试热门免费模型性能
"""

import requests
import json
import time

# NVIDIA NIM API配置
NVIDIA_API_BASE = "https://integrate.api.nvidia.com/v1"

# 用户需要提供API Key
# 可以通过环境变量或直接设置
API_KEY = input("请输入您的NVIDIA API Key: ").strip()

if not API_KEY:
    print("错误: 需要API Key才能测试")
    exit(1)

# 热门模型列表
MODELS = [
    "meta/llama-3.1-405b-instruct",
    "meta/llama-3.1-70b-instruct",
    "meta/llama-3.1-8b-instruct",
    "deepseek-ai/deepseek-v3",
    "qwen/qwen2.5-72b-instruct",
    "mistralai/mixtral-8x7b-instruct-v0.1",
    "microsoft/phi-3-mini-128k-instruct",
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def test_model(model_id, test_prompt="你好，请介绍一下你自己"):
    """测试单个模型"""
    print(f"\n{'='*50}")
    print(f"测试模型: {model_id}")
    print(f"{'='*50}")
    
    url = f"{NVIDIA_API_BASE}/chat/completions"
    
    payload = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": test_prompt}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"[OK] 状态码: {response.status_code}")
            print(f"[OK] 响应时间: {elapsed:.2f}秒")
            print(f"[OK] 回复内容:\n{content[:200]}...")
            return True, elapsed, content
        else:
            print(f"[FAIL] 状态码: {response.status_code}")
            print(f"[FAIL] 错误: {response.text[:200]}")
            return False, elapsed, None
            
    except requests.exceptions.Timeout:
        print(f"[FAIL] 超时 (>30秒)")
        return False, 30, None
    except Exception as e:
        print(f"[FAIL] 异常: {str(e)}")
        return False, 0, None

def list_available_models():
    """列出可用模型"""
    print("\n" + "="*50)
    print("获取可用模型列表")
    print("="*50)
    
    url = f"{NVIDIA_API_BASE}/models"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            models = response.json()
            print(f"[OK] 可用模型:")
            for m in models.get('data', []):
                print(f"  - {m.get('id', 'unknown')}")
            return models
        else:
            print(f"[FAIL] 无法获取模型列表: {response.status_code}")
            return None
    except Exception as e:
        print(f"[FAIL] 异常: {str(e)}")
        return None

def run_performance_comparison():
    """性能对比测试"""
    print("\n" + "="*60)
    print("NVIDIA NIM API 模型性能对比测试")
    print("="*60)
    
    # 测试提示
    test_prompts = [
        "简单: 你好",
        "中等: 请用一句话解释什么是人工智能",
        "复杂: 请写一段Python代码实现快速排序算法"
    ]
    
    results = []
    
    for model in MODELS[:3]:  # 先测试前3个模型
        for prompt in test_prompts:
            success, elapsed, content = test_model(model, prompt.split(": ")[1])
            results.append({
                'model': model,
                'prompt_type': prompt.split(": ")[0],
                'success': success,
                'elapsed': elapsed,
                'content_length': len(content) if content else 0
            })
    
    # 打印结果汇总
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    print(f"\n{'模型':<40} {'提示类型':<8} {'成功':<6} {'耗时':<8} {'回复长度':<10}")
    print("-" * 72)
    
    for r in results:
        status = "OK" if r['success'] else "FAIL"
        print(f"{r['model']:<40} {r['prompt_type']:<8} {status:<6} {r['elapsed']:.2f}s  {r['content_length']:<10}")

def main():
    print("="*60)
    print("NVIDIA NIM API 测试工具")
    print("="*60)
    
    # 1. 列出可用模型
    list_available_models()
    
    # 2. 测试推荐模型
    print("\n推荐先测试的模型:")
    print("1. meta/llama-3.1-8b-instruct (最快)")
    print("2. meta/llama-3.1-70b-instruct (性价比高)")
    print("3. deepseek-ai/deepseek-v3 (中文优化)")
    
    choice = input("\n选择测试模式 (1=单模型 2=对比测试): ").strip()
    
    if choice == "1":
        model = input("输入模型ID (如 meta/llama-3.1-8b-instruct): ").strip()
        prompt = input("输入测试提示: ").strip()
        test_model(model, prompt)
    elif choice == "2":
        run_performance_comparison()
    else:
        # 默认测试最快的模型
        test_model("meta/llama-3.1-8b-instruct", "你好，介绍一下你自己")

if __name__ == "__main__":
    main()