# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
from pathlib import Path

MEMORY_DIR = Path('C:/Users/Administrator/.openclaw/workspace-工程师/memory')
BRAIN_API = 'http://127.0.0.1:5002'

def import_files():
    md_files = list(MEMORY_DIR.glob('*.md'))
    print(f"[INFO] Found {len(md_files)} memory files")
    
    imported = 0
    for md_file in md_files:
        content = md_file.read_text(encoding='utf-8')
        paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 100]
        
        chunks = []
        for i, para in enumerate(paragraphs[:5]):
            chunks.append({
                'content': para,
                'source': md_file.name,
                'metadata': {'chunk': i}
            })
        
        if chunks:
            resp = requests.post(f'{BRAIN_API}/import/batch', 
                json={'chunks': chunks}, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                imported += data.get('imported', 0)
                print(f"  {md_file.name}: +{data.get('imported', 0)}")
    
    # Verify
    resp = requests.get(f'{BRAIN_API}/stats')
    print(f"[OK] Total imported: {imported}")
    print(f"[OK] DB stats: {resp.json()}")

if __name__ == '__main__':
    import_files()