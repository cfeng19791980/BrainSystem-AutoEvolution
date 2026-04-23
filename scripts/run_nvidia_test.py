# -*- coding: utf-8 -*-
import requests
import time

API_KEY = "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"
BASE = "https://integrate.api.nvidia.com/v1"

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

print("="*60)
print("NVIDIA NIM API Test")
print("="*60)

# 1. List models
print("\n[1] Available Models:")
try:
    r = requests.get(f"{BASE}/models", headers=headers, timeout=10)
    if r.status_code == 200:
        models = r.json().get('data', [])
        for m in models[:15]:
            print(f"  {m.get('id')}")
except Exception as e:
    print(f"  Error: {e}")

# 2. Test top models
test_models = [
    "meta/llama-3.1-8b-instruct",
    "meta/llama-3.1-70b-instruct",
    "deepseek-ai/deepseek-v3",
    "qwen/qwen2.5-72b-instruct",
]

print("\n[2] Performance Test:")
results = []

for model in test_models:
    print(f"\n  Testing {model}...")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hello, introduce yourself briefly"}],
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
            print(f"    Response: {content[:80]}...")
            results.append({'model': model, 'time': elapsed, 'ok': True, 'content': content})
        else:
            print(f"    FAIL: {r.status_code} - {r.text[:100]}")
            results.append({'model': model, 'time': 0, 'ok': False})
    except Exception as e:
        print(f"    ERROR: {str(e)[:50]}")
        results.append({'model': model, 'time': 0, 'ok': False})

# Summary
print("\n"+"="*60)
print("Summary:")
print("="*60)
for r in results:
    status = "OK" if r['ok'] else "FAIL"
    print(f"{r['model']:<35} {status:<6} {r['time']:.2f}s")

print("\nRecommendation:")
working = [r for r in results if r['ok']]
if working:
    fastest = min(working, key=lambda x: x['time'])
    print(f"Fastest: {fastest['model']} ({fastest['time']:.2f}s)")