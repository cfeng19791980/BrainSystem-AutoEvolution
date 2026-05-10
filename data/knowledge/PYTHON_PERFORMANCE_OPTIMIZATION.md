# Python性能优化最佳实践

## 基于2024-2025最佳实践汇总

---

## 优化策略概览

### Optimization Strategies

| Strategy | Impact | Complexity | Use Case |
|----------|--------|------------|----------|
| Data Structure Choice | High | Low | All projects |
| Vectorized Operations | High | Medium | Data processing |
| Caching/Memoization | High | Low | Repetitive computation |
| Parallel Processing | High | High | CPU-intensive |
| Profiling First | Critical | Low | All optimization |
| C Extensions | High | High | Critical bottlenecks |
| Memory Optimization | Medium | Medium | Large datasets |

---

## 1. 选择合适的数据结构

### 核心原则

**性能影响**: 选择合适的数据结构和算法可以显著影响Python代码性能

**最佳实践**:
```
✓ List: 有序序列，支持索引访问
✓ Dict: 键值映射，O(1)查找
✓ Set: 无序唯一元素，O(1)查找
✓ Tuple: 不可变序列，内存效率高
✓ NumPy Array: 数值计算，向量化操作
```

---

### 案例: 查找性能对比

```python
import time

# List查找 (O(n))
def find_in_list(lst, target):
    for i, item in enumerate(lst):
        if item == target:
            return i
    return -1

# Dict查找 (O(1))
def find_in_dict(dct, target):
    return dct.get(target, -1)

# Set查找 (O(1))
def find_in_set(st, target):
    return target in st

# 性能测试
data_list = list(range(100000))
data_dict = {i: i for i in range(100000)}
data_set = set(range(100000))

# List: ~0.01s
# Dict/Set: ~0.000001s
# 性能差距: 10,000倍
```

---

### 数据结构选择决策树

```
问题类型 → 数据结构
─────────────────────
需要查找？ → Dict/Set
需要排序？ → List + sort()
需要唯一性？ → Set
数值计算？ → NumPy Array
内存敏感？ → Tuple/Generator
频繁修改？ → List
```

---

## 2. 向量化操作

### 核心原则

**定义**: 对整个数组或数据结构执行操作，而非单个元素

**优势**:
```
✓ 避免Python循环开销
✓ 底层C实现加速
✓ SIMD指令优化
✓ 内存连续访问
```

---

### 案例: NumPy向量化

```python
import numpy as np
import time

# Python循环 (慢)
def python_loop_sum(data):
    total = 0
    for item in data:
        total += item
    return total

# NumPy向量化 (快)
def numpy_vector_sum(data):
    return np.sum(data)

# 性能测试
data = list(range(1000000))
data_np = np.array(data)

# Python loop: ~0.1s
# NumPy vector: ~0.001s
# 性能差距: 100倍
```

---

### Pandas向量化

```python
import pandas as pd

# 遞代循环 (慢)
def iterate_processing(df):
    result = []
    for idx, row in df.iterrows():
        result.append(row['A'] * row['B'])
    return result

# 向量化操作 (快)
def vectorized_processing(df):
    return df['A'] * df['B']

# apply方法 (中等)
def apply_processing(df):
    return df.apply(lambda row: row['A'] * row['B'], axis=1)

# 性能排序
# Vectorized > Apply > Iterate
```

---

## 3. 缓存与Memoization

### 核心原则

**定义**: 避免重复计算，存储计算结果

**适用场景**:
```
✓ 重复函数调用
✓ 递归计算
✓ 数据库查询缓存
✓ API响应缓存
```

---

### 案例: functools.lru_cache

```python
from functools import lru_cache
import time

# 无缓存 (每次重新计算)
def fibonacci_no_cache(n):
    if n <= 1:
        return n
    return fibonacci_no_cache(n-1) + fibonacci_no_cache(n-2)

# 有缓存 (避免重复计算)
@lru_cache(maxsize=128)
def fibonacci_cached(n):
    if n <= 1:
        return n
    return fibonacci_cached(n-1) + fibonacci_cached(n-2)

# 性能测试
# fibonacci_no_cache(35): ~3s
# fibonacci_cached(35): ~0.001s (首次)
# fibonacci_cached(35): ~0.000001s (后续)
# 性能差距: 3,000倍+
```

---

### Brain System缓存应用

```python
# Brain System中的缓存应用

class BrainCache:
    """
    Brain Entry Result Cache.
    Cache brain decisions to avoid repeated computation.
    """
    def __init__(self, maxsize=1000):
        self.cache = {}
        self.maxsize = maxsize
    
    def get(self, query):
        return self.cache.get(query)
    
    def set(self, query, result):
        if len(self.cache) >= self.maxsize:
            # Remove oldest entry
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        self.cache[query] = result
    
    def clear(self):
        self.cache.clear()

# 使用缓存
brain_cache = BrainCache()

def brain_entry_with_cache(query):
    # Check cache first
    cached = brain_cache.get(query)
    if cached:
        return cached
    
    # Compute if not cached
    result = brain_entry(query)
    
    # Cache result
    brain_cache.set(query, result)
    
    return result
```

---

## 4. 并行处理

### 核心原则

**适用场景**:
```
✓ CPU密集型任务
✓ 多核CPU利用率低
✓ 任务可分割
✓ 无共享状态依赖
```

---

### 案例: multiprocessing

```python
import multiprocessing as mp
import time

def cpu_intensive_task(n):
    """CPU-intensive task"""
    total = 0
    for i in range(n):
        total += i ** 2
    return total

# 串行处理
def serial_process(tasks):
    results = []
    for task in tasks:
        results.append(cpu_intensive_task(task))
    return results

# 并行处理
def parallel_process(tasks):
    with mp.Pool(processes=mp.cpu_count()) as pool:
        results = pool.map(cpu_intensive_task, tasks)
    return results

# 性能测试
tasks = [1000000] * 8

# Serial: ~8s (8核CPU)
# Parallel: ~1s
# 性能差距: 8倍
```

---

### concurrent.futures

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# I/O密集型 → ThreadPoolExecutor
def io_task(url):
    # Network request
    return fetch_url(url)

def parallel_io(urls):
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(io_task, urls)
    return list(results)

# CPU密集型 → ProcessPoolExecutor
def parallel_cpu(tasks):
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        results = executor.map(cpu_intensive_task, tasks)
    return list(results)
```

---

## 5. 优先Profile性能瓶颈

### 核心原则

**黄金法则**: "先Profile，后优化"

**工具选择**:
```
✓ cProfile: Python内置profiler
✓ line_profiler: 行级profiler
✓ memory_profiler: 内存分析
✓ py-spy: 低开销profiler
```

---

### 案例: cProfile使用

```python
import cProfile
import pstats

def profile_function(func, *args):
    """
    Profile function execution.
    """
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = func(*args)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    
    # Sort by cumulative time
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    return result

# 使用示例
profile_function(brain_entry, "test query")
```

---

### Profile结果分析

```
输出示例:
         1000003 function calls in 0.500 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
   1       0.001    0.001    0.500    0.500 brain_entry.py:1(brain_entry)
   1000    0.200    0.000    0.200    0.000 embedding.py:50(get_embedding)
   1000    0.150    0.000    0.150    0.000 database.py:30(query)

关键指标:
- tottime: 函数自身执行时间
- cumtime: 函数及子函数总时间
- ncalls: 调用次数
```

---

## 6. 内存优化

### 核心原则

**问题**: Python对象内存开销大

**优化策略**:
```
✓ Generator替代List
✓ NumPy Array替代List
✓ __slots__减少对象内存
✓ 分块处理大数据
```

---

### 案例: Generator替代List

```python
# List (内存占用大)
def list_process(n):
    data = [x ** 2 for x in range(n)]  # 全部存储在内存
    for item in data:
        process(item)

# Generator (内存占用小)
def generator_process(n):
    data = (x ** 2 for x in range(n))  # 逐个生成
    for item in data:
        process(item)

# 内存对比
# List[10M]: ~800MB
# Generator: ~KB级别
```

---

### __slots__优化

```python
# 普通类 (内存开销大)
class NormalClass:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

# __slots__类 (内存优化)
class OptimizedClass:
    __slots__ = ['x', 'y', 'z']
    
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

# 内存对比 (1M对象)
# NormalClass: ~240MB
# OptimizedClass: ~120MB
# 内存节省: 50%
```

---

## 7. 避免常见性能陷阱

### 陷阱1: 循环内执行SQL

```python
# ❌ 错误: 循环内执行SQL
for user in users:
    result = db.query(f"SELECT * FROM orders WHERE user_id = {user.id}")

# ✅ 正确: 批量查询
user_ids = [user.id for user in users]
result = db.query(f"SELECT * FROM orders WHERE user_id IN ({user_ids})")
```

---

### 陷阱2: 循环内执行命令

```python
# ❌ 错误: 循环内执行命令
for file in files:
    subprocess.run(['process', file])

# ✅ 正确: 批量处理
subprocess.run(['process'] + files)
```

---

### 陷阱3: 字符串拼接

```python
# ❌ 错误: 循环拼接字符串
result = ''
for item in items:
    result += str(item)  # 每次创建新字符串

# ✅ 正确: 使用join
result = ''.join(str(item) for item in items)

# ✅ 正确: 使用列表append
parts = []
for item in items:
    parts.append(str(item))
result = ''.join(parts)
```

---

## 8. C扩展优化

### 核心原则

**适用场景**:
```
✓ 关键瓶颈无法用Python优化
✓ 需要底层性能
✓ 算法固定，高频调用
```

---

### Cython示例

```python
# Python版本
def python_sum(n):
    total = 0
    for i in range(n):
        total += i
    return total

# Cython版本 (cython_sum.pyx)
def cython_sum(int n):
    cdef int total = 0
    cdef int i
    for i in range(n):
        total += i
    return total

# 编译
# cythonize -i cython_sum.pyx

# 性能对比
# Python: ~0.1s
# Cython: ~0.001s
# 性能差距: 100倍
```

---

## 9. Polars替代Pandas

### 核心原则

**优势**:
```
✓ 多线程执行
✓ 内存效率更高
✓ 惰性执行
✓ 兼容Pandas API
```

---

### 案例: Polars性能

```python
import polars as pl
import pandas as pd

# Pandas (单线程)
df_pd = pd.read_csv('large_data.csv')
result_pd = df_pd.groupby('category').agg({'value': 'sum'})

# Polars (多线程)
df_pl = pl.read_csv('large_data.csv')
result_pl = df_pl.groupby('category').agg(pl.col('value').sum())

# 性能对比 (10GB数据)
# Pandas: ~30s
# Polars: ~3s
# 性能差距: 10倍
```

---

## 10. Brain System性能优化实践

### Brain Entry优化

```python
# Brain System性能优化案例

class OptimizedBrainEntry:
    """
    Optimized Brain Entry with caching, vectorization.
    """
    
    # 1. 使用__slots__减少内存
    __slots__ = ['cache', 'embedding_model', 'knowledge_graph']
    
    # 2. 使用缓存避免重复计算
    @lru_cache(maxsize=1000)
    def get_embedding_cached(self, text):
        return self.embedding_model.encode(text)
    
    # 3. 使用NumPy向量化计算
    def compute_similarity_vectorized(self, query_vec, doc_vecs):
        # 向量化计算，避免循环
        return np.dot(doc_vecs, query_vec)
    
    # 4. 批量处理
    def batch_process(self, queries):
        # 批量获取embedding
        embeddings = self.embedding_model.encode_batch(queries)
        return [self.process(q, e) for q, e in zip(queries, embeddings)]
```

---

### csi10性能优化

```python
# csi10股票系统性能优化

class OptimizedAnalyzer:
    """
    Optimized stock analyzer with caching.
    """
    
    # 1. 缓存指数数据
    @lru_cache(maxsize=100)
    def get_index_data_cached(self, index_code):
        return fetch_index_data(index_code)
    
    # 2. 使用NumPy计算指标
    def calculate_indicators_numpy(self, data):
        close = np.array(data['Close'])
        
        # SMA向量化计算
        sma_5 = np.convolve(close, np.ones(5)/5, mode='valid')
        sma_15 = np.convolve(close, np.ones(15)/15, mode='valid')
        
        return sma_5, sma_15
    
    # 3. 分块处理大数据
    def process_large_dataset(self, data, chunk_size=10000):
        results = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            results.append(self.process_chunk(chunk))
        return np.concatenate(results)
```

---

## 性能优化决策树

```
性能瓶颈定位 → Profile → 找到瓶颈
───────────────────────────────
瓶颈类型 → 优化策略
───────────────────────
I/O瓶颈 → ThreadPool + 缓存
CPU瓶颈 → ProcessPool + 向量化 + C扩展
内存瓶颈 → Generator + __slots__ + 分块处理
算法瓶颈 → 更优算法 + 数据结构
```

---

## Pattern-Key

`python.performance.optimization` - Python性能优化最佳实践

---

**来源**: Analytics Vidhya + Dev Genius + Fyld.pt
**更新时间**: 2026-04-23 15:20
**适用项目**: BrainSystem + csi10 + Gateway