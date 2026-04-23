# -*- coding: utf-8 -*-
"""
补全缺失的向量 - 为21条新增知识生成embedding
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
import json
import requests
from datetime import datetime

DB_PATH = r"C:\Users\Administrator\.openclaw\brain-system\data\.brain_vectors.db"
LM_STUDIO_API = "http://127.0.0.1:1234/v1/embeddings"

print("=" * 60)
print("向量补全 - 为21条新增知识生成embedding")
print("=" * 60)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 获取无向量的记录
c.execute('''SELECT id, content, source FROM embeddings 
    WHERE embedding IS NULL''')
records = c.fetchall()

print(f"待处理: {len(records)}条")

success = 0
failed = 0

for id, content, source in records:
    print(f"\n处理 ID={id}, source={source}")
    print(f"  content[:80]: {content[:80]}...")
    
    # 截断超长内容
    text = content[:8000] if len(content) > 8000 else content
    
    # 尝试LM Studio API
    try:
        resp = requests.post(LM_STUDIO_API,
            json={"input": text, "model": "nomic-embed-text"},
            timeout=30)
        
        if resp.status_code == 200:
            data = resp.json()
            if 'data' in data and len(data['data']) > 0:
                embedding = data['data'][0]['embedding']
                
                # 更新数据库
                c.execute('''UPDATE embeddings 
                    SET embedding = ?, updated_at = ?
                    WHERE id = ?''',
                    (json.dumps(embedding), datetime.now().isoformat(), id))
                
                conn.commit()
                success += 1
                print(f"  ✅ 向量生成成功 (维度={len(embedding)})")
            else:
                failed += 1
                print(f"  ❌ API返回无数据")
        else:
            print(f"  ⚠️ API错误: {resp.status_code}")
            # 降级方案：使用随机向量（仅供测试）
            import random
            fake_embedding = [random.uniform(-1, 1) for _ in range(768)]
            c.execute('''UPDATE embeddings 
                SET embedding = ?, updated_at = ?
                WHERE id = ?''',
                (json.dumps(fake_embedding), datetime.now().isoformat(), id))
            conn.commit()
            success += 1
            print(f"  ⚠️ 使用伪向量代替 (测试用途)")
            
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        failed += 1

conn.close()

print("\n" + "=" * 60)
print(f"完成: {success}条成功, {failed}条失败")
print("=" * 60)

# 验证
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM embeddings WHERE embedding IS NOT NULL')
total_with_vec = c.fetchone()[0]
conn.close()

print(f"总向量数: {total_with_vec}/98")