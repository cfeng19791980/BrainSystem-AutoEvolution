# -*- coding: utf-8 -*-
import requests
import time

API_KEY = "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"
BASE = "https://integrate.api.nvidia.com/v1"

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

print("="*60)
print("NVIDIA NIM Embedding Test")
print("="*60)

# Test embedding models
embedding_models = [
    "baai/bge-m3",
    "nvidia/nv-embedqa-e5-v5",
    "nvidia/llama-3.1-nv-embedqa-1b-v1",
]

test_text = "这是一段中文测试文本，用于测试向量嵌入模型的性能"

results = []

for model in embedding_models:
    print(f"\nTesting {model}...")
    
    payload = {
        "model": model,
        "input": test_text,
        "encoding_format": "float"
    }
    
    try:
        start = time.time()
        r = requests.post(f"{BASE}/embeddings", headers=headers, json=payload, timeout=30)
        elapsed = time.time() - start
        
        if r.status_code == 200:
            result = r.json()
            embedding = result.get('data', [{}])[0].get('embedding', [])
            dim = len(embedding)
            print(f"  OK: {elapsed:.2f}s")
            print(f"  Vector dim: {dim}")
            print(f"  Sample: [{embedding[0]:.4f}, {embedding[1]:.4f}, ...]")
            results.append({'model': model, 'time': elapsed, 'dim': dim, 'ok': True})
        else:
            print(f"  FAIL: {r.status_code}")
            print(f"  Error: {r.text[:100]}")
            results.append({'model': model, 'time': 0, 'dim': 0, 'ok': False})
    except Exception as e:
        print(f"  ERROR: {str(e)[:50]}")
        results.append({'model': model, 'time': 0, 'dim': 0, 'ok': False})

# Compare with local BGE-M3
print("\n"+"="*60)
print("Comparison with Local BGE-M3:")
print("="*60)

# Local embedding test
try:
    from sentence_transformers import SentenceTransformer
    local_model = SentenceTransformer("C:/Users/Administrator/.cache/modelscope/Xorbits/bge-m3")
    
    start = time.time()
    local_emb = local_model.encode(test_text)
    local_time = time.time() - start
    local_dim = len(local_emb)
    
    print(f"Local BGE-M3: {local_time:.2f}s, dim={local_dim}")
except Exception as e:
    print(f"Local test error: {e}")

# Summary
print("\n"+"="*60)
print("Embedding Summary:")
print("="*60)

working = [r for r in results if r['ok']]
if working:
    print(f"\n{'Model':<40} {'Time':<10} {'Dim':<10}")
    for r in working:
        print(f"{r['model']:<40} {r['time']:.2f}s    {r['dim']}")
    
    fastest = min(working, key=lambda x: x['time'])
    print(f"\nRecommendation: {fastest['model']} ({fastest['time']:.2f}s)")
else:
    print("No embedding models available via NVIDIA NIM API")