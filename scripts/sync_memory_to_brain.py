"""
sync_memory_to_brain.py
Sync OpenClaw memory chunks + memory/*.md files to Brain vector DB via /import/batch.
Runs incrementally: only syncs chunks/files updated since last sync.

Two data sources:
  1. main.sqlite chunks  (OpenClaw compacted sessions)
  2. memory/*.md files   (long-term persistent memory)
"""

import sqlite3
import json
import requests
import os
import glob
import hashlib
from datetime import datetime, timezone

# === Config ===
OC_MEMORY_DB = r'C:\Users\10341\.openclaw\memory\main.sqlite'
MEMORY_DIR = os.path.join(os.path.dirname(OC_MEMORY_DB), '..', 'workspace', 'memory')
BRAIN_IMPORT_URL = 'http://127.0.0.1:5002/import/batch'
BRAIN_STATS_URL = 'http://127.0.0.1:5002/stats'
STATE_FILE = os.path.join(os.path.dirname(__file__), 'sync_state.json')
CHUNK_MIN_CHARS = 50
BATCH_MAX = 100
MEMORY_CHUNK_LINES = 50  # split .md files by this many lines per chunk

# === Helpers ===

def load_state():
    """Load last sync state"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'last_sync_at': 0, 'synced_sources': []}

def save_state(ts, synced_sources):
    with open(STATE_FILE, 'w') as f:
        json.dump({'last_sync_at': ts, 'synced_sources': synced_sources}, f, indent=2)

def get_brain_sources():
    """Get list of already-imported source identifiers from Brain stats"""
    try:
        r = requests.get(BRAIN_STATS_URL, timeout=5)
        if r.status_code == 200:
            sources = r.json().get('sources', {})
            return set(sources.keys())
    except Exception as e:
        print(f"  [WARN] Could not fetch Brain sources: {e}")
    return set()

# === Part 1: Sync from main.sqlite chunks ===

def get_openclaw_chunks():
    """Get all chunks from OpenClaw memory DB, ordered by updated_at ASC"""
    if not os.path.exists(OC_MEMORY_DB):
        print(f"  [WARN] DB not found: {OC_MEMORY_DB}")
        return []
    conn = sqlite3.connect(OC_MEMORY_DB)
    c = conn.cursor()
    try:
        c.execute('SELECT id, path, source, text, updated_at FROM chunks ORDER BY updated_at ASC')
        rows = c.fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return rows

def build_chunk_source_key(chunk_id, source, text):
    content_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]
    return f'openclaw_memory:{source}:{chunk_id}:{content_hash}'

def chunk_to_brain_payload(row):
    chunk_id, path, source, text, updated_at = row
    if not text or len(text.strip()) < CHUNK_MIN_CHARS:
        return None
    source_key = build_chunk_source_key(chunk_id, source, text)
    return {
        'content': text.strip(),
        'source': source_key,
        'metadata': {
            'type': 'openclaw_chunk',
            'openclaw_chunk_id': chunk_id,
            'openclaw_path': path,
            'openclaw_source': source,
            'updated_at': updated_at,
            'synced_at': datetime.now(timezone.utc).isoformat()
        }
    }

def sync_openclaw_chunks(brain_sources):
    """Sync main.sqlite chunks to Brain"""
    all_rows = get_openclaw_chunks()
    if not all_rows:
        print("  No chunks in OpenClaw memory DB.")
        return 0, []

    # Build set of already-synced source keys
    already_synced = set()
    for s in brain_sources:
        if s.startswith('openclaw_memory:'):
            already_synced.add(s)

    chunks = []
    new_sources = []
    for row in all_rows:
        chunk_id, path, source, text, updated_at = row
        sk = build_chunk_source_key(chunk_id, source, text)
        if sk in already_synced:
            continue
        payload = chunk_to_brain_payload(row)
        if payload:
            chunks.append(payload)
            new_sources.append(sk)

    if not chunks:
        print("  All chunks already synced.")
        return 0, []

    total = 0
    for i in range(0, len(chunks), BATCH_MAX):
        batch = chunks[i:i + BATCH_MAX]
        try:
            r = requests.post(BRAIN_IMPORT_URL, json={'chunks': batch}, timeout=30)
            result = r.json()
            total += result.get('imported', 0)
            print(f"  [Chunks] Batch {i//BATCH_MAX + 1}: {result.get('imported', 0)} imported")
        except Exception as e:
            print(f"  [Chunks] Batch {i//BATCH_MAX + 1} error: {e}")

    return total, new_sources


# === Part 2: Sync from memory/*.md files ===

def get_memory_files():
    """Get all .md files in memory directory with metadata"""
    mem_dir = MEMORY_DIR
    if not os.path.isdir(mem_dir):
        print(f"  [WARN] Memory dir not found: {mem_dir}")
        return []
    files = []
    for fp in glob.glob(os.path.join(mem_dir, '*.md')):
        stat = os.stat(fp)
        files.append({
            'path': fp,
            'name': os.path.basename(fp),
            'mtime': int(stat.st_mtime),
            'size': stat.st_size
        })
    files.sort(key=lambda f: f['name'])
    return files

def read_file_chunks(file_info):
    """Split a .md file into chunks by line count, preserving context"""
    path = file_info['path']
    name = file_info['name']

    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"    [SKIP] Cannot read {name}: {e}")
        return []

    total_lines = len(lines)
    if total_lines == 0:
        return []

    chunks = []
    for i in range(0, total_lines, MEMORY_CHUNK_LINES):
        chunk_lines = lines[i:i + MEMORY_CHUNK_LINES]
        content = ''.join(chunk_lines).strip()
        if len(content) < CHUNK_MIN_CHARS:
            continue

        # Build deterministic source key: {file}:{chunk_idx}:{content_hash[:12]}
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
        chunk_idx = i // MEMORY_CHUNK_LINES
        source_key = f'memory_file:{name}:{chunk_idx}:{content_hash}'

        chunks.append({
            'content': content,
            'source': source_key,
            'metadata': {
                'type': 'memory_file',
                'file': name,
                'chunk_index': chunk_idx,
                'line_start': i + 1,
                'line_end': min(i + MEMORY_CHUNK_LINES, total_lines),
                'file_mtime': file_info['mtime'],
                'synced_at': datetime.now(timezone.utc).isoformat()
            }
        })

    return chunks

def sync_memory_files(brain_sources):
    """Sync memory/*.md files to Brain"""
    files = get_memory_files()
    if not files:
        print("  No memory files found.")
        return 0, []

    # Build set of already-synced source keys
    # Brain sources are stored as source keys; filter memory_file: prefix
    already_synced = set()
    for s in brain_sources:
        if s.startswith('memory_file:'):
            already_synced.add(s)

    all_chunks = []
    new_sources = []

    for f in files:
        file_chunks = read_file_chunks(f)
        for c in file_chunks:
            if c['source'] in already_synced:
                continue
            all_chunks.append(c)
            new_sources.append(c['source'])

    if not all_chunks:
        print("  All memory files already synced.")
        return 0, []

    print(f"  Found {len(all_chunks)} unsynced chunks from memory files")

    total = 0
    for i in range(0, len(all_chunks), BATCH_MAX):
        batch = all_chunks[i:i + BATCH_MAX]
        try:
            r = requests.post(BRAIN_IMPORT_URL, json={'chunks': batch}, timeout=30)
            result = r.json()
            imported = result.get('imported', 0)
            total += imported
            print(f"  [Memory] Batch {i//BATCH_MAX + 1}: {imported} imported")
        except Exception as e:
            print(f"  [Memory] Batch {i//BATCH_MAX + 1} error: {e}")

    return total, new_sources


# === Main ===

def main():
    state = load_state()
    ts = datetime.now().isoformat()
    print(f"[{ts}] Syncing OpenClaw memory to Brain...")

    # Get current Brain sources (dedup across both data sources)
    brain_sources = get_brain_sources()
    print(f"Brain has {len(brain_sources)} existing sources")

    # Part 1: sync OpenClaw DB chunks
    print("\n--- Part 1: OpenClaw chunks ---")
    chunk_imported, chunk_sources = sync_openclaw_chunks(brain_sources)

    # Part 2: sync memory/*.md files
    print("\n--- Part 2: Memory files ---")
    mem_imported, mem_sources = sync_memory_files(brain_sources)

    # Update state
    if chunk_sources or mem_sources:
        saved_sources = set(state.get('synced_sources', [])) | set(chunk_sources) | set(mem_sources)
        save_state(int(datetime.now().timestamp()), list(saved_sources))

    total = chunk_imported + mem_imported
    print(f"\n[OK] Sync complete. Total imported: {total} (chunks: {chunk_imported}, memory: {mem_imported})")

if __name__ == '__main__':
    main()
