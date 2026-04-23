# -*- coding: utf-8 -*-
"""
NVIDIA NIM API 快速测试
"""
import requests
import time
import os

# API配置
NVIDIA_API_BASE = "https://integrate.api.nvidia.com/v1"

def test_nvidia_api(api_key, model="meta/llama-3.1-8b-instruct"):
    """测试NVIDIA NIM API"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 测试1: 获取模型列表
    print("\n[1] 获取可用模型列表...")
    try:
        r = requests.get(f"{NVIDIA_API_BASE}/models", headers=headers, timeout=10)
        if r.status_code == 200:
            models = r.json().get('data', [])
            print(f"    OK: 发现 {len(models)} 个模型")
            for m in models[:10]:
                print(f"    - {m.get('id')}")
        else:
            print(f"    FAIL: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        print(f"    ERROR: {e}")
    
    # 测试2: Chat Completion
    print(f"\n[2] 测试Chat Completion (模型: {model})...")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "你好，请用一句话介绍你自己"}],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        start = time.time()
        r = requests.post(f"{NVIDIA_API_BASE}/chat/completions", 
                          headers=headers, json=payload, timeout=30)
        elapsed = time.time() - start
        
        if r.status_code == 200:
            result = r.json()
            content = result['choices'][0]['message']['content']
            print(f"    OK: 响应时间 {elapsed:.2f}s")
            print(f"    回复: {content}")
            return True, elapsed, content
        else:
            print(f"    FAIL: {r.status_code}")
            print(f"    错误: {r.text[:200]}")
            return False, 0, None
    except Exception as e:
        print(f"    ERROR: {e}")
        return False, 0, None

if __name__ == "__main__":
    print("="*50)
    print("NVIDIA NIM API 测试")
    print("="*50)
    
    # 从命令行或环境变量获取key
    import sys
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = os.environ.get("NVIDIA_API_KEY", "")
    
    if not api_key:
        print("\n使用方法:")
        print("  python test_nvidia_quick.py <your_api_key>")
        print("  或设置环境变量 NVIDIA_API_KEY")
        print("\n推荐模型:")
        print("  - meta/llama-3.1-8b-instruct (最快)")
        print("  - meta/llama-3.1-70b-instruct (高性价比)")
        print("  - deepseek-ai/deepseek-v3 (中文)")
        print("  - qwen/qwen2.5-72b-instruct (代码)")
        sys.exit(1)
    
    # 运行测试
    test_nvidia_api(api_key)