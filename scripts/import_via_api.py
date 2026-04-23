# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import requests

MEMORY_DIR = Path('C:/Users/Administrator/.openclaw/workspace-工程师/memory')
DB_PATH = Path('C:/Users/Administrator/.openclaw/.brain_vectors.db')
BRAIN_API = 'http://127.0.0.1:5002'

def init_db():
    """Initialize vector database - skip if exists"""
    if DB_PATH.exists():
        print(f"[OK] Vector DB already exists: {DB_PATH}")
        return
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
    print("[OK] Vector DB initialized")

def get_embedding_via_api(content):
    """Get embedding from Brain Entry API (OpenAI style)"""
    try:
        resp = requests.post(f'{BRAIN_API}/v1/embeddings',
            json={'input': content[:8000], 'model': 'all-MiniLM-L6-v2'},
            timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if 'data' in data and len(data['data']) > 0:
                return data['data'][0]['embedding']
    except Exception as e:
        print(f"[WARN] API embed error: {e}")
    return None

def import_files():
    """Import memory files"""
    init_db()
    
    md_files = list(MEMORY_DIR.glob('*.md'))
    print(f"[INFO] Found {len(md_files)} memory files")
    
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    imported = 0
    
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            
            # Split into chunks
            paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 100]
            
            for i, chunk in enumerate(paragraphs[:10]):  # Limit to 10 chunks per file
                print(f"  Processing: {md_file.name} chunk {i+1}")
                
                embedding = get_embedding_via_api(chunk)
                
                if embedding:
                    metadata = {
                        'file': md_file.name,
                        'chunk': i,
                        'chars': len(chunk)
                    }
                    c.execute('''INSERT INTO embeddings 
                        (content, embedding, source, metadata, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                        (chunk, json.dumps(embedding), md_file.name,
                         json.dumps(metadata), datetime.now().isoformat(),
                         datetime.now().isoformat()))
                    imported += 1
                    
        except Exception as e:
            print(f"[ERR] {md_file.name}: {e}")
    
    conn.commit()
    conn.close()
    
    # Verify
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM embeddings')
    total = c.fetchone()[0]
    conn.close()
    
    print(f"[OK] Imported {imported} chunks, Total: {total}")

if __name__ == '__main__':
    print("=" * 60)
    print("Memory Import via Brain API")
    print("=" * 60)
    import_files()