# -*- coding: utf-8 -*-
"""
测试五星项目搜索效果
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
import json
import numpy as np
import requests

DB_PATH = r"C:\Users\Administrator\.openclaw\brain-system\data\.brain_vectors.db"
LM_STUDIO_API = "http://127.0.0.1:1234/v1/embeddings"

def get_embedding(text):
    try:
        resp = requests.post(LM_STUDIO_API,
            json={"input": text[:8000], "model": "nomic-embed-text"},
            timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if 'data' in data and len(data['data']) > 0:
                return np.array(data['data'][0]['embedding'])
    except Exception as e:
        print(f"API错误: {e}")
    return None

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def search(query_text, top_k=5):
    print(f"\n{'='*60}")
    print(f"查询: {query_text}")
    print(f"{'='*60}")
    
    query_vec = get_embedding(query_text)
    if query_vec is None:
        print("无法获取查询向量")
        return
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, content, source, embedding FROM embeddings WHERE embedding IS NOT NULL')
    records = c.fetchall()
    conn.close()
    
    results = []
    for id, content, source, embedding_json in records:
        embedding = np.array(json.loads(embedding_json))
        if len(embedding) == len(query_vec):
            sim = cosine_similarity(query_vec, embedding)
            results.append((id, sim, content, source))
    
    results.sort(key=lambda x: x[1], reverse=True)
    top_results = results[:top_k]
    
    print(f"\nTop {top_k} 结果:")
    for rank, (id, sim, content, source) in enumerate(top_results, 1):
        print(f"\n[{rank}] 相似度: {sim:.4f}")
        print(f"    来源: {source}")
        print(f"    内容: {content[:100]}...")
    
    return top_results

print("=" * 60)
print("五星项目搜索测试")
print("=" * 60)

queries = [
    "Vue PR怎么提交",
    "TypeScript feature贡献要求",
    "React main分支策略",
    "Node.js贡献需要签名吗",
    "Rust新手怎么开始贡献",
    "Django Trac ticket",
]

for query in queries:
    search(query, top_k=3)

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)