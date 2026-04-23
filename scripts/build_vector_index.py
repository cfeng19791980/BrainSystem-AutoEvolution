# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""
向量数据库索引构建脚本
扫描memory/*.md文件并导入到Brain Entry向量数据库
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import sys

# 添加brain_entry路径
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/brain-system/core')

# 配置
MEMORY_DIR = Path('C:/Users/Administrator/.openclaw/workspace-工程师/memory')
DB_PATH = Path('C:/Users/Administrator/.openclaw/.brain_vectors.db')
BRAIN_API = 'http://127.0.0.1:5002/entry'

def init_vector_db():
    """初始化向量数据库"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT, embedding TEXT, source TEXT, metadata TEXT,
        created_at TEXT, updated_at TEXT)''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_source ON embeddings(source)')
    conn.commit()
    conn.close()
    print(f"[OK] Vector DB initialized: {DB_PATH}")

def get_embedding_from_brain(content):
    """通过Brain Entry API获取embedding"""
    import requests
    try:
        # 截断超长内容
        if len(content) > 8000:
            content = content[:8000]
        
        resp = requests.post(BRAIN_API, 
            json={'content': content, 'mode': 'embedding_only'},
            timeout=30)
        
        if resp.status_code == 200:
            data = resp.json()
            if 'embedding' in data:
                return data['embedding']
    except Exception as e:
        print(f"[WARN] API error: {e}")
    return None

def get_embedding_local(content):
    """使用本地Sentence-Transformers获取embedding"""
    try:
        from sentence_transformers import SentenceTransformer
        from pathlib import Path
        
        # 尝试BGE-M3
        bge_m3_path = Path('C:/Users/Administrator/.cache/modelscope/Xorbits/bge-m3')
        if bge_m3_path.exists():
            model = SentenceTransformer(str(bge_m3_path))
        else:
            # 降级到all-MiniLM-L6-v2
            model = SentenceTransformer('all-MiniLM-L6-v2')
        
        embedding = model.encode(content[:8000])
        return embedding.tolist()
    except Exception as e:
        print(f"[WARN] Local embedding error: {e}")
        return None

def import_memory_files():
    """导入memory目录下的所有md文件"""
    init_vector_db()
    
    md_files = list(MEMORY_DIR.glob('*.md'))
    print(f"[INFO] Found {len(md_files)} memory files")
    
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    imported = 0
    failed = 0
    
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            
            # 分段处理长文件（每段2000字符）
            chunks = []
            if len(content) > 2000:
                # 按段落分割
                paragraphs = content.split('\n\n')
                for para in paragraphs:
                    if len(para.strip()) > 50:  # 过滤太短的段落
                        chunks.append(para.strip())
            else:
                chunks = [content]
            
            for i, chunk in enumerate(chunks):
                if len(chunk) < 50:
                    continue
                
                print(f"  Processing: {md_file.name} chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
                
                # 获取embedding
                embedding = get_embedding_local(chunk)
                
                if embedding:
                    metadata = {
                        'file': md_file.name,
                        'chunk': i,
                        'total_chunks': len(chunks),
                        'char_count': len(chunk)
                    }
                    
                    c.execute('''INSERT INTO embeddings 
                        (content, embedding, source, metadata, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                        (chunk, json.dumps(embedding), md_file.name, 
                         json.dumps(metadata), datetime.now().isoformat(), 
                         datetime.now().isoformat()))
                    
                    imported += 1
                else:
                    failed += 1
                    
        except Exception as e:
            print(f"[ERR] Error processing {md_file.name}: {e}")
            failed += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n[OK] Import complete: {imported} chunks imported, {failed} failed")
    
    # 验证
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM embeddings')
    total = c.fetchone()[0]
    conn.close()
    print(f"[INFO] Total vectors in DB: {total}")

def test_search(query="brain hook"):
    """测试向量搜索"""
    import requests
    
    print(f"\n[TEST] Testing search: '{query}'")
    
    resp = requests.post(BRAIN_API, 
        json={'content': query},
        timeout=10)
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"[OK] Search results: {data.get('results_count', 0)}")
        if 'brain_context' in data:
            ctx = data['brain_context']
            print(f"   Intent: {ctx.get('intent', {}).get('type', 'unknown')}")
    else:
        print(f"[ERR] Search failed: {resp.status_code}")

if __name__ == '__main__':
    print("=" * 60)
    print("Vector Index Builder for Brain Entry")
    print("=" * 60)
    
    import_memory_files()
    test_search("brain hook")
    test_search("向量搜索")