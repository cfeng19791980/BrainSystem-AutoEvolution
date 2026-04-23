# -*- coding: utf-8 -*-
"""轻量级结果缓存 - 使用装饰器方式"""

import re

# 读取文件
with open(r'C:\Users\Administrator\.openclaw\brain-system\core\brain_entry.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到全局变量区域（在executor定义之前）
insert_line = None
for i, line in enumerate(lines):
    if 'executor = ThreadPoolExecutor' in line:
        insert_line = i
        break

if insert_line:
    # 在executor之前插入缓存定义
    cache_code = """
# AutoResearch优化: 结果缓存
RESULT_CACHE = {}
RESULT_CACHE_TTL = 60
RESULT_CACHE_MAX = 500
RESULT_CACHE_HITS = 0

def get_cached_result(key):
    if key in RESULT_CACHE:
        result, timestamp = RESULT_CACHE[key]
        from datetime import datetime
        if (datetime.now() - timestamp).total_seconds() < RESULT_CACHE_TTL:
            RESULT_CACHE_HITS += 1
            return result
    return None

def set_cached_result(key, result):
    if len(RESULT_CACHE) < RESULT_CACHE_MAX:
        from datetime import datetime
        RESULT_CACHE[key] = (result, datetime.now())

"""
    lines.insert(insert_line, cache_code)
    print(f"缓存函数已插入到行{insert_line+1}")

# 找到entry函数的位置，在开头添加缓存检查
for i, line in enumerate(lines):
    if "def entry()" in line or "def entry():" in line:
        # 找到函数的下一行（content = data.get那一行）
        for j in range(i+1, min(i+20, len(lines))):
            if "content = data.get('content'" in lines[j]:
                # 在这行之前插入缓存检查
                cache_check = """    # AutoResearch优化: 检查结果缓存
    cache_key = hashlib.md5((data.get('content', '') + str(data.get('userAction', 'query'))).encode('utf-8')).hexdigest()
    cached = get_cached_result(cache_key)
    if cached:
        logger.info(f"Result cache hit: {RESULT_CACHE_HITS}")
        return cached
    
"""
                lines.insert(j, cache_check)
                print(f"缓存检查已插入到行{j+1}")
                break
        break

# 找到return语句，在之前添加缓存保存
for i, line in enumerate(lines):
    if "'success': True," in line and "'processed_content':" in lines[i+1] if i+1 < len(lines) else False:
        # 检查上下文是否是return np_jsonify
        for k in range(max(0, i-3), i):
            if "return np_jsonify" in lines[k]:
                # 在return之前添加缓存保存
                # 找到intent定义位置（前面几行）
                for m in range(k-1, max(0, k-10)):
                    if "provider, _ = load_provider_state()" in lines[m]:
                        cache_save = """        # AutoResearch优化: 保存结果缓存
        set_cached_result(cache_key, np_jsonify({
            'success': True,
            'processed_content': processed_content,
            'brain_context': {
                'intent': intent,
                'results': brain_results,
                'timestamp': datetime.now().isoformat(),
                'provider': provider,
                'trigger_detected': trigger_detected
            }
        }))
        
"""
                        lines.insert(m+1, cache_save)
                        print(f"缓存保存已插入到行{m+2}")
                        break
                break

# 写回文件
with open(r'C:\Users\Administrator\.openclaw\brain-system\core\brain_entry.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("结果缓存优化完成!")