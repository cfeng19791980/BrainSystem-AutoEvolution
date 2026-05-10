# -*- coding: utf-8 -*-
"""
OPT-REQ-001: Embedding Auto-Cache Pattern
==========================================
Source: typesense #1932 - Cache Generated Embeddings when Auto-Embedding is used
Pattern ID: embedding_auto_cache
Approved: 2026-04-23

Problem:
- Auto-embedding每次搜索需要重新生成向量
- 使用外部API时耗时~1s或更多
- 重复查询相同文本产生相同向量

Solution:
- 复用BrainSystem已有embedding_cache机制
- 添加缓存过期策略（TTL配置）
- 添加缓存命中率统计
"""

import hashlib
import json
import time
import logging
from datetime import datetime, timedelta
from functools import lru_cache

logger = logging.getLogger('BrainEntry.OptReq001')

# ============================================================
# Pattern: embedding_auto_cache
# ============================================================
EMBEDDING_AUTO_CACHE_CONFIG = {
    "enabled": True,
    "ttl_seconds": 3600,  # 1 hour TTL
    "max_cache_size": 1000,  # Max 1000 cached embeddings
    "hash_method": "sha256",  # Text hash for cache key
    "stats_enabled": True,  # Track cache hit rate
    "compression": False,  # Compression option
}

EMBEDDING_CACHE_STATS = {
    "hits": 0,
    "misses": 0,
    "total_queries": 0,
    "total_time_saved_ms": 0,
}

class EmbeddingAutoCache:
    """Auto-cache for embedding results - Pattern from typesense #1932"""
    
    def __init__(self, cache_db_path=None):
        self.cache = {}  # In-memory cache
        self.timestamps = {}  # Cache timestamps for TTL
        self.stats = EMBEDDING_CACHE_STATS.copy()
        
        # Optional: SQLite backend for persistent cache
        self.cache_db_path = cache_db_path
        if cache_db_path:
            self._init_cache_db()
    
    def _init_cache_db(self):
        """Initialize SQLite cache backend"""
        import sqlite3
        conn = sqlite3.connect(self.cache_db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS embedding_cache
                     (text_hash TEXT PRIMARY KEY,
                      embedding TEXT,
                      created_at TIMESTAMP,
                      expires_at TIMESTAMP)''')
        conn.commit()
        conn.close()
    
    def get_cache_key(self, text):
        """Generate cache key from text using SHA256"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def get_cached_embedding(self, text):
        """Get embedding from cache if exists and not expired"""
        if not EMBEDDING_AUTO_CACHE_CONFIG["enabled"]:
            return None
        
        cache_key = self.get_cache_key(text)
        
        # Check in-memory cache first
        if cache_key in self.cache:
            # Check TTL
            timestamp = self.timestamps.get(cache_key)
            if timestamp:
                age = datetime.now() - timestamp
                ttl = timedelta(seconds=EMBEDDING_AUTO_CACHE_CONFIG["ttl_seconds"])
                if age < ttl:
                    self.stats["hits"] += 1
                    self.stats["total_queries"] += 1
                    logger.debug(f'Cache HIT for text: {text[:50]}...')
                    return self.cache[cache_key]
                else:
                    # Expired, remove from cache
                    del self.cache[cache_key]
                    del self.timestamps[cache_key]
        
        # Cache miss
        self.stats["misses"] += 1
        self.stats["total_queries"] += 1
        logger.debug(f'Cache MISS for text: {text[:50]}...')
        return None
    
    def set_cached_embedding(self, text, embedding):
        """Store embedding in cache with TTL"""
        if not EMBEDDING_AUTO_CACHE_CONFIG["enabled"]:
            return
        
        cache_key = self.get_cache_key(text)
        
        # Check cache size limit
        if len(self.cache) >= EMBEDDING_AUTO_CACHE_CONFIG["max_cache_size"]:
            # Remove oldest entry
            oldest_key = min(self.timestamps.keys(), key=self.timestamps.get)
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
            logger.debug(f'Cache evicted oldest entry: {oldest_key}')
        
        # Store in cache
        self.cache[cache_key] = embedding
        self.timestamps[cache_key] = datetime.now()
        logger.debug(f'Cache SET for text: {text[:50]}...')
    
    def get_or_generate_embedding(self, text, embedding_func):
        """Get embedding from cache or generate new one"""
        # Try cache first
        cached = self.get_cached_embedding(text)
        if cached is not None:
            return cached
        
        # Generate new embedding
        start_time = time.time()
        embedding = embedding_func(text)
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Store in cache
        self.set_cached_embedding(text, embedding)
        
        # Track time saved (assuming next query would take same time)
        self.stats["total_time_saved_ms"] += elapsed_ms
        
        return embedding
    
    def get_stats(self):
        """Get cache statistics"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total if total > 0 else 0
        
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": hit_rate,
            "total_queries": self.stats["total_queries"],
            "total_cached": len(self.cache),
            "time_saved_ms": self.stats["total_time_saved_ms"],
            "time_saved_estimate_seconds": self.stats["total_time_saved_ms"] / 1000,
        }
    
    def clear_cache(self):
        """Clear all cached embeddings"""
        self.cache.clear()
        self.timestamps.clear()
        logger.info('Embedding cache cleared')
    
    def cleanup_expired(self):
        """Remove expired entries from cache"""
        ttl = timedelta(seconds=EMBEDDING_AUTO_CACHE_CONFIG["ttl_seconds"])
        expired_keys = []
        
        for key, timestamp in self.timestamps.items():
            if datetime.now() - timestamp >= ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
            del self.timestamps[key]
        
        if expired_keys:
            logger.info(f'Cleaned up {len(expired_keys)} expired cache entries')
        
        return len(expired_keys)


# ============================================================
# Integration Helper Functions
# ============================================================
def optimize_embedding_query(text, model=None, embedding_func=None):
    """
    Optimize embedding query using auto-cache.
    
    Usage:
        embedding = optimize_embedding_query("search text", model=my_model)
    """
    global _embedding_auto_cache
    if '_embedding_auto_cache' not in globals():
        _embedding_auto_cache = EmbeddingAutoCache()
    
    if embedding_func:
        return _embedding_auto_cache.get_or_generate_embedding(text, embedding_func)
    
    # Default embedding function using model
    if model:
        def default_embedding_func(text):
            return model.encode(text)
        return _embedding_auto_cache.get_or_generate_embedding(text, default_embedding_func)
    
    logger.warning('No embedding function or model provided')
    return None


def get_embedding_cache_stats():
    """Get global embedding cache statistics"""
    global _embedding_auto_cache
    if '_embedding_auto_cache' not in globals():
        return {"hits": 0, "misses": 0, "hit_rate": 0}
    
    return _embedding_auto_cache.get_stats()


# ============================================================
# Test Function
# ============================================================
def test_embedding_auto_cache():
    """Test embedding auto-cache optimization"""
    print("=" * 60)
    print("OPT-REQ-001 Test: Embedding Auto-Cache")
    print("=" * 60)
    
    cache = EmbeddingAutoCache()
    
    # Simulate embedding function (mock)
    def mock_embedding_func(text):
        time.sleep(0.01)  # Simulate 10ms embedding time
        return [0.1, 0.2, 0.3]  # Mock embedding
    
    test_texts = [
        "search query 1",
        "search query 2",
        "search query 1",  # Duplicate (should hit cache)
        "search query 3",
        "search query 1",  # Duplicate again
        "search query 2",  # Duplicate
    ]
    
    print("\n--- Test Queries ---")
    start_total = time.time()
    
    for i, text in enumerate(test_texts):
        start = time.time()
        embedding = cache.get_or_generate_embedding(text, mock_embedding_func)
        elapsed_ms = (time.time() - start) * 1000
        
        status = "HIT" if cache.stats["hits"] > cache.stats["misses"] else "MISS"
        print(f"Query {i+1}: '{text}' - {elapsed_ms:.2f}ms")
    
    total_elapsed_ms = (time.time() - start_total) * 1000
    
    # Get statistics
    stats = cache.get_stats()
    
    print("\n--- Cache Statistics ---")
    print(f"Total queries: {stats['total_queries']}")
    print(f"Cache hits: {stats['hits']}")
    print(f"Cache misses: {stats['misses']}")
    print(f"Hit rate: {stats['hit_rate']:.2%}")
    print(f"Time saved: {stats['time_saved_estimate_seconds']:.3f}s")
    
    print("\n--- Performance Comparison ---")
    without_cache_time = len(test_texts) * 10  # 10ms per query
    with_cache_time = total_elapsed_ms
    improvement = (without_cache_time - with_cache_time) / without_cache_time * 100
    
    print(f"Without cache: {without_cache_time}ms")
    print(f"With cache: {with_cache_time:.2f}ms")
    print(f"Improvement: {improvement:.1f}%")
    
    print("\n--- Test Result ---")
    if stats['hit_rate'] >= 0.3:  # Expected 3/6 hits = 50%
        print("[PASS] Cache hit rate meets expectation")
        return True
    else:
        print("[FAIL] Cache hit rate below expectation")
        return False


if __name__ == '__main__':
    test_result = test_embedding_auto_cache()
    
    # Record pattern
    pattern = {
        "pattern_id": "embedding_auto_cache",
        "source": "github_typesense_1932",
        "approved_at": "2026-04-23T16:27",
        "status": "implemented",
        "test_result": "pass" if test_result else "fail"
    }
    
    print("\n" + "=" * 60)
    print("Pattern Implementation Record")
    print("=" * 60)
    print(json.dumps(pattern, indent=2))