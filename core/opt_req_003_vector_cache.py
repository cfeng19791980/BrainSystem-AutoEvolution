# -*- coding: utf-8 -*-
"""
OPT-REQ-003: Vector Result Cache Pattern
=========================================
Source: milvus #20687 - Very slow searching and query embeddings from collection
Pattern ID: vector_result_cache
Approved: 2026-04-23

Problem:
- Vector retrieval is super slow (each request went to S3)
- Search task takes 56s
- Getting embeddings by IDs takes 5.5 minutes

Solution:
- Add vector result cache to avoid repeated S3/database access
- Add chunk manager for local caching
- Add cache preloading for hot vectors
"""

import json
import logging
import time
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger('BrainEntry.OptReq003')

# ============================================================
# Pattern: vector_result_cache
# ============================================================
VECTOR_CACHE_CONFIG = {
    "enabled": True,
    "cache_method": "local_memory",  # Local memory cache
    "max_cache_size_mb": 100,  # Max 100MB cache
    "preload_topk": 100,  # Preload top 100 vectors
    "ttl_seconds": 3600,  # 1 hour TTL
    "compression": False,  # Compression option
    "track_frequency": True,  # Track query frequency for hot vectors
}

class VectorResultCache:
    """Cache vector results to avoid repeated S3/DB access - Pattern from milvus #20687"""
    
    def __init__(self):
        self.cache = {}  # id -> embedding vector
        self.timestamps = {}  # id -> cache timestamp
        self.frequency = defaultdict(int)  # id -> query frequency
        self.cache_size_bytes = 0
        self.stats = {
            "hits": 0,
            "misses": 0,
            "total_queries": 0,
            "preload_count": 0,
            "evictions": 0,
        }
    
    def get_vector_size_bytes(self, vector):
        """Calculate vector size in bytes"""
        if isinstance(vector, dict):
            vector = vector.get("embedding", [])
        if isinstance(vector, list):
            return len(vector) * 4  # float32 = 4 bytes
        return 0
    
    def is_cache_full(self):
        """Check if cache size limit reached"""
        max_bytes = VECTOR_CACHE_CONFIG["max_cache_size_mb"] * 1024 * 1024
        return self.cache_size_bytes >= max_bytes
    
    def evict_oldest(self):
        """Evict oldest cached entry"""
        if not self.timestamps:
            return
        
        oldest_id = min(self.timestamps.keys(), key=self.timestamps.get)
        vector_size = self.get_vector_size_bytes(self.cache.get(oldest_id))
        
        del self.cache[oldest_id]
        del self.timestamps[oldest_id]
        self.cache_size_bytes -= vector_size
        self.stats["evictions"] += 1
        
        logger.debug(f'Evicted oldest entry: {oldest_id} ({vector_size} bytes)')
    
    def get_cached_vectors(self, ids):
        """Get vectors from cache for given IDs"""
        if not VECTOR_CACHE_CONFIG["enabled"]:
            return [], ids
        
        cached_vectors = []
        uncached_ids = []
        
        for id in ids:
            # Track frequency
            self.frequency[id] += 1
            
            # Check cache
            if id in self.cache:
                # Check TTL
                timestamp = self.timestamps.get(id)
                if timestamp:
                    age = datetime.now() - timestamp
                    ttl = timedelta(seconds=VECTOR_CACHE_CONFIG["ttl_seconds"])
                    if age < ttl:
                        cached_vectors.append({"id": id, "embedding": self.cache[id]})
                        self.stats["hits"] += 1
                        continue
                    else:
                        # Expired
                        del self.cache[id]
                        del self.timestamps[id]
                        self.cache_size_bytes -= self.get_vector_size_bytes(self.cache.get(id, []))
            
            uncached_ids.append(id)
            self.stats["misses"] += 1
        
        self.stats["total_queries"] += len(ids)
        
        logger.debug(f'Cache hits: {len(cached_vectors)}, misses: {len(uncached_ids)}')
        
        return cached_vectors, uncached_ids
    
    def set_cached_vectors(self, vectors):
        """Store vectors in cache"""
        if not VECTOR_CACHE_CONFIG["enabled"]:
            return
        
        for vec in vectors:
            id = vec.get("id")
            embedding = vec.get("embedding")
            
            if not id or not embedding:
                continue
            
            # Evict if cache full
            while self.is_cache_full():
                self.evict_oldest()
            
            # Store in cache
            self.cache[id] = embedding
            self.timestamps[id] = datetime.now()
            
            vector_size = self.get_vector_size_bytes(embedding)
            self.cache_size_bytes += vector_size
            
            logger.debug(f'Cached vector: {id} ({vector_size} bytes)')
    
    def preload_hot_vectors(self, get_vectors_func, topk=100):
        """Preload frequently queried vectors"""
        if not VECTOR_CACHE_CONFIG["track_frequency"]:
            return
        
        # Get topk by frequency
        hot_ids = sorted(self.frequency.keys(), key=self.frequency.get, reverse=True)[:topk]
        
        if not hot_ids:
            logger.debug('No hot vectors to preload')
            return
        
        # Get vectors (assuming get_vectors_func is provided)
        vectors = get_vectors_func(hot_ids)
        
        # Cache them
        self.set_cached_vectors(vectors)
        self.stats["preload_count"] += len(vectors)
        
        logger.info(f'Preloaded {len(vectors)} hot vectors')
    
    def search_with_cache(self, query_func, query_vector, topk=100):
        """Search with vector result cache"""
        # Execute search (returns IDs)
        start_time = time.time()
        search_result = query_func(query_vector, topk)
        search_time = time.time() - start_time
        
        # Extract IDs from result
        ids = []
        if isinstance(search_result, list):
            ids = [item.get("id") if isinstance(item, dict) else item for item in search_result]
        
        # Get vectors from cache
        cached_vectors, uncached_ids = self.get_cached_vectors(ids)
        
        # If uncached, fetch from source
        fetch_time = 0
        if uncached_ids:
            start_time = time.time()
            new_vectors = query_func(uncached_ids)  # Fetch vectors
            fetch_time = time.time() - start_time
            
            # Cache new vectors
            self.set_cached_vectors(new_vectors)
            cached_vectors.extend(new_vectors)
        
        return {
            "result": cached_vectors,
            "search_time_ms": search_time * 1000,
            "fetch_time_ms": fetch_time * 1000,
            "cache_hit_count": len(cached_vectors) - len(uncached_ids),
            "cache_miss_count": len(uncached_ids),
        }
    
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
            "cache_size_mb": self.cache_size_bytes / (1024 * 1024),
            "preload_count": self.stats["preload_count"],
            "evictions": self.stats["evictions"],
        }
    
    def clear_cache(self):
        """Clear all cached vectors"""
        self.cache.clear()
        self.timestamps.clear()
        self.cache_size_bytes = 0
        logger.info('Vector cache cleared')
    
    def cleanup_expired(self):
        """Remove expired entries"""
        ttl = timedelta(seconds=VECTOR_CACHE_CONFIG["ttl_seconds"])
        expired_ids = []
        
        for id, timestamp in self.timestamps.items():
            if datetime.now() - timestamp >= ttl:
                expired_ids.append(id)
        
        for id in expired_ids:
            vector_size = self.get_vector_size_bytes(self.cache.get(id))
            del self.cache[id]
            del self.timestamps[id]
            self.cache_size_bytes -= vector_size
        
        if expired_ids:
            logger.info(f'Cleaned up {len(expired_ids)} expired cache entries')
        
        return len(expired_ids)


# ============================================================
# Integration Helper Functions
# ============================================================
_global_vector_cache = None

def get_vector_result_cache():
    """Get global vector result cache instance"""
    global _global_vector_cache
    if _global_vector_cache is None:
        _global_vector_cache = VectorResultCache()
    return _global_vector_cache


def optimize_vector_search(query_func, query_vector, topk=100):
    """
    Optimize vector search using result cache.
    
    Usage:
        result = optimize_vector_search(my_search_func, query_vec, topk=1000)
    """
    cache = get_vector_result_cache()
    return cache.search_with_cache(query_func, query_vector, topk)


# ============================================================
# Test Function
# ============================================================
def test_vector_result_cache():
    """Test vector result cache optimization"""
    print("=" * 60)
    print("OPT-REQ-003 Test: Vector Result Cache")
    print("=" * 60)
    
    cache = VectorResultCache()
    
    # Simulate vector database
    mock_vectors = {
        "id_1": [0.1, 0.2, 0.3],
        "id_2": [0.4, 0.5, 0.6],
        "id_3": [0.7, 0.8, 0.9],
        "id_4": [0.11, 0.12, 0.13],
        "id_5": [0.14, 0.15, 0.16],
    }
    
    def mock_search_func(query_vector, topk):
        """Mock search function"""
        time.sleep(0.02)  # Simulate 20ms search time
        return list(mock_vectors.keys())[:topk]
    
    def mock_fetch_func(ids):
        """Mock fetch function"""
        time.sleep(0.05)  # Simulate 50ms fetch time (S3 access)
        return [{"id": id, "embedding": mock_vectors.get(id, [])} for id in ids]
    
    # Test queries
    test_queries = [
        ["id_1", "id_2", "id_3"],  # First query (miss)
        ["id_1", "id_2", "id_3"],  # Same query (hit)
        ["id_4", "id_5"],          # New IDs (miss)
        ["id_1", "id_2", "id_4"],  # Mixed (partial hit)
        ["id_1", "id_2"],          # Cached (hit)
    ]
    
    print("\n--- Test Queries ---")
    total_without_cache = 0
    total_with_cache = 0
    
    for i, ids in enumerate(test_queries):
        # Measure without cache (simulated)
        without_cache_time = len(ids) * 50  # 50ms per ID fetch
        
        # Measure with cache
        start = time.time()
        cached_vectors, uncached_ids = cache.get_cached_vectors(ids)
        if uncached_ids:
            new_vectors = mock_fetch_func(uncached_ids)
            cache.set_cached_vectors(new_vectors)
        elapsed_ms = (time.time() - start) * 1000
        
        total_without_cache += without_cache_time
        total_with_cache += elapsed_ms
        
        status = f"hit={len(cached_vectors)}, miss={len(uncached_ids)}"
        print(f"Query {i+1}: {status} - {elapsed_ms:.2f}ms (without cache: {without_cache_time}ms)")
    
    # Get statistics
    stats = cache.get_stats()
    
    print("\n--- Cache Statistics ---")
    print(f"Total queries: {stats['total_queries']}")
    print(f"Cache hits: {stats['hits']}")
    print(f"Cache misses: {stats['misses']}")
    print(f"Hit rate: {stats['hit_rate']:.2%}")
    print(f"Cache size: {stats['cache_size_mb']:.3f}MB")
    
    print("\n--- Performance Comparison ---")
    improvement = (total_without_cache - total_with_cache) / total_without_cache * 100
    
    print(f"Without cache: {total_without_cache}ms")
    print(f"With cache: {total_with_cache:.2f}ms")
    print(f"Time saved: {total_without_cache - total_with_cache:.2f}ms")
    print(f"Improvement: {improvement:.1f}%")
    
    print("\n--- Test Result ---")
    if stats['hit_rate'] >= 0.3:  # Expected good hit rate
        print("[PASS] Vector cache hit rate meets expectation")
        return True
    else:
        print("[FAIL] Vector cache hit rate below expectation")
        return False


if __name__ == '__main__':
    test_result = test_vector_result_cache()
    
    # Record pattern
    pattern = {
        "pattern_id": "vector_result_cache",
        "source": "github_milvus_20687",
        "approved_at": "2026-04-23T16:27",
        "status": "implemented",
        "test_result": "pass" if test_result else "fail"
    }
    
    print("\n" + "=" * 60)
    print("Pattern Implementation Record")
    print("=" * 60)
    print(json.dumps(pattern, indent=2))