# -*- coding: utf-8 -*-
"""
测试向量搜索 - 验证新知识匹配效果
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
    """获取查询文本的embedding"""
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
    """计算余弦相似度"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)

def search_knowledge(query_text, top_k=5):
    """搜索知识库"""
    print(f"\n{'='*60}")
    print(f"查询: {query_text}")
    print(f"{'='*60}")
    
    # 获取查询向量
    query_vec = get_embedding(query_text)
    if query_vec is None:
        print("无法获取查询向量")
        return
    
    print(f"查询向量维度: {len(query_vec)}")
    
    # 搜索数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT id, content, source, embedding FROM embeddings 
        WHERE embedding IS NOT NULL''')
    records = c.fetchall()
    conn.close()
    
    # 计算相似度
    results = []
    for id, content, source, embedding_json in records:
        embedding = np.array(json.loads(embedding_json))
        if len(embedding) == len(query_vec):
            sim = cosine_similarity(query_vec, embedding)
            results.append((id, sim, content, source))
    
    # 排序取top_k
    results.sort(key=lambda x: x[1], reverse=True)
    top_results = results[:top_k]
    
    print(f"\nTop {top_k} 结果:")
    for rank, (id, sim, content, source) in enumerate(top_results, 1):
        print(f"\n[{rank}] 相似度: {sim:.4f}")
        print(f"    来源: {source}")
        print(f"    内容: {content[:100]}...")
    
    return top_results

print("=" * 60)
print("向量搜索测试 - 验证新知识匹配")
print("=" * 60)

# 测试不同类型查询
queries = [
    "PR review 怎么做最好",
    "Google code review 标准",
    "如何避免PR评论冲突",
    "代码审查沟通技巧",
    "nit comment 是什么",
    "小PR优势",
]

for query in queries:
    search_knowledge(query, top_k=3)

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)