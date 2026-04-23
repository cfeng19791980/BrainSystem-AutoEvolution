# -*- coding: utf-8 -*-
import requests
import time

API_KEY = "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"
BASE = "https://integrate.api.nvidia.com/v1"

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

print("="*60)
print("NVIDIA NIM API - Full Model Test")
print("="*60)

# Correct model IDs from list
test_models = [
    ("meta/llama-3.1-70b-instruct", "英文通用"),
    ("meta/llama-3.1-8b-instruct", "快速响应"),
    ("deepseek-ai/deepseek-v3.2", "DeepSeek V3.2"),
    ("deepseek-ai/deepseek-v3.1-terminus", "DeepSeek Terminus"),
    ("deepseek-ai/deepseek-coder-6.7b-instruct", "代码专用"),
    ("google/codegemma-7b", "Google CodeGemma"),
    ("bigcode/starcoder2-15b", "StarCoder2"),
    ("01-ai/yi-large", "零一万物Yi"),
]

print("\n[1] Chinese Test:")
results_cn = []

for model_id, desc in test_models:
    print(f"\n  {model_id} ({desc})...")
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": "你好，请用中文介绍你自己"}],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        start = time.time()
        r = requests.post(f"{BASE}/chat/completions", headers=headers, json=payload, timeout=30)
        elapsed = time.time() - start
        
        if r.status_code == 200:
            content = r.json()['choices'][0]['message']['content']
            print(f"    OK: {elapsed:.2f}s")
            print(f"    {content[:100]}")
            results_cn.append({'model': model_id, 'desc': desc, 'time': elapsed, 'ok': True})
        else:
            print(f"    FAIL: {r.status_code}")
            results_cn.append({'model': model_id, 'desc': desc, 'time': 0, 'ok': False})
    except Exception as e:
        print(f"    ERROR: {str(e)[:50]}")
        results_cn.append({'model': model_id, 'desc': desc, 'time': 0, 'ok': False})

# Summary
print("\n"+"="*60)
print("Chinese Test Summary:")
print("="*60)

working = [r for r in results_cn if r['ok']]
for r in working:
    print(f"{r['model']:<40} {r['time']:.2f}s")

if working:
    fastest = min(working, key=lambda x: x['time'])
    print(f"\nBest for Chinese: {fastest['model']} ({fastest['time']:.2f}s)")

# Code test
print("\n"+"="*60)
print("[2] Code Test:")
print("="*60)

code_models = [
    "meta/llama-3.1-70b-instruct",
    "deepseek-ai/deepseek-coder-6.7b-instruct",
    "google/codegemma-7b",
]

prompt = "Write a Python function to calculate fibonacci numbers"

results_code = []
for model in code_models:
    print(f"\n  {model}...")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150,
        "temperature": 0.3
    }
    
    try:
        start = time.time()
        r = requests.post(f"{BASE}/chat/completions", headers=headers, json=payload, timeout=30)
        elapsed = time.time() - start
        
        if r.status_code == 200:
            content = r.json()['choices'][0]['message']['content']
            print(f"    OK: {elapsed:.2f}s")
            print(f"    Code preview: {content[:120]}...")
            results_code.append({'model': model, 'time': elapsed, 'ok': True})
        else:
            print(f"    FAIL: {r.status_code}")
            results_code.append({'model': model, 'time': 0, 'ok': False})
    except Exception as e:
        print(f"    ERROR: {str(e)[:50]}")
        results_code.append({'model': model, 'time': 0, 'ok': False})

print("\n"+"="*60)
print("Final Recommendation:")
print("="*60)

all_working = [r for r in results_cn + results_code if r['ok']]
if all_working:
    # Sort by time
    all_working.sort(key=lambda x: x['time'])
    print("\nPerformance Ranking:")
    for i, r in enumerate(all_working[:5], 1):
        print(f"  {i}. {r['model']:<40} {r['time']:.2f}s")