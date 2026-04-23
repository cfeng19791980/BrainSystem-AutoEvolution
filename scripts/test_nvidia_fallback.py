# -*- coding: utf-8 -*-
import requests
import time

API_KEY = "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"
BASE = "https://integrate.api.nvidia.com/v1"

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

print("="*60)
print("NVIDIA BGE-M3 Embedding Fallback Test")
print("="*60)

test_texts = [
    "这是一段中文测试",
    "Hello, this is a test for embedding",
    "测试向量搜索性能",
]

print("\n[1] Single Text Test:")
payload = {
    "model": "baai/bge-m3",
    "input": test_texts[0],
    "encoding_format": "float"
}

start = time.time()
r = requests.post(f"{BASE}/embeddings", headers=headers, json=payload, timeout=10)
elapsed = time.time() - start

if r.status_code == 200:
    result = r.json()
    embedding = result['data'][0]['embedding']
    print(f"  Status: OK")
    print(f"  Response Time: {elapsed:.3f}s")
    print(f"  Vector Dim: {len(embedding)}")
    print(f"  Sample: [{embedding[0]:.4f}, {embedding[1]:.4f}, {embedding[2]:.4f}]")
else:
    print(f"  FAIL: {r.status_code} - {r.text[:100]}")

print("\n[2] Batch Test (3 texts):")
payload = {
    "model": "baai/bge-m3",
    "input": test_texts,
    "encoding_format": "float"
}

start = time.time()
r = requests.post(f"{BASE}/embeddings", headers=headers, json=payload, timeout=15)
elapsed = time.time() - start

if r.status_code == 200:
    result = r.json()
    embeddings = result['data']
    print(f"  Status: OK")
    print(f"  Response Time: {elapsed:.3f}s")
    print(f"  Batch Size: {len(embeddings)}")
    print(f"  Avg Time per Text: {elapsed/len(test_texts):.3f}s")
else:
    print(f"  FAIL: {r.status_code}")

print("\n[3] Compare with Local:")
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("C:/Users/Administrator/.cache/modelscope/Xorbits/bge-m3")
    
    start = time.time()
    local_emb = model.encode(test_texts[0])
    local_time = time.time() - start
    print(f"  Local BGE-M3: {local_time:.3f}s")
    
    print(f"\n  Speed Comparison:")
    print(f"  Local:  {local_time:.3f}s (baseline)")
    print(f"  NVIDIA: {elapsed:.3f}s (cloud)")
    print(f"  Diff:   +{(elapsed/local_time):.1f}x slower")
    
    if elapsed < 1.5:
        print(f"\n  Conclusion: NVIDIA embedding ({elapsed:.3f}s) is acceptable for fallback!")
    else:
        print(f"\n  Conclusion: Too slow for fallback (>1.5s)")
except Exception as e:
    print(f"  Local test skipped: {e}")

print("\n"+"="*60)
print("Recommendation:")
print("="*60)
print("Add NVIDIA BGE-M3 as fallback provider in brain_entry.py")