# -*- coding: utf-8 -*-
"""结果缓存优化 - 简化版"""

# 读取文件
with open(r'C:\Users\Administrator\.openclaw\brain-system\core\brain_entry.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在EmbeddingProvider缓存后面添加结果缓存
# 找到_cache_max_size = 1000位置
import re
pattern = r"(_cache_max_size = 1000)"
match = re.search(pattern, content)

if match:
    old_text = match.group(1)
    new_text = """_cache_max_size = 1000  # 最大缓存条目
    _cache_hits = 0  # 缓存命中统计

# AutoResearch优化: 结果缓存（API响应级）
RESULT_CACHE = {}  # query hash -> (response_json, timestamp)
RESULT_CACHE_TTL = 60  # 缓存有效期（秒）
RESULT_CACHE_MAX = 500  # 最大缓存条目
RESULT_CACHE_HITS = 0  # 结果缓存命中统计"""
    
    content = content.replace(old_text, new_text, 1)
    print("结果缓存变量已添加")
else:
    print("未找到缓存定义位置")

# 在entry函数开头添加缓存检查
# 找到 content = data.get('content', '')
pattern = r"(content = data\.get\('content', ''))"
match = re.search(pattern, content)

if match:
    old_text = match.group(1)
    new_text = """# AutoResearch优化: 检查结果缓存
    result_cache_key = hashlib.md5((data.get('content', '') + str(data.get('userAction', 'query'))).encode('utf-8')).hexdigest()
    if result_cache_key in RESULT_CACHE:
        cached_response, cached_time = RESULT_CACHE[result_cache_key]
        if (datetime.now() - cached_time).total_seconds() < RESULT_CACHE_TTL:
            RESULT_CACHE_HITS += 1
            logger.info(f"Result cache hit: {RESULT_CACHE_HITS}")
            return cached_response
    
    content = data.get('content', '')"""
    
    content = content.replace(old_text, new_text, 1)
    print("缓存检查逻辑已添加")
else:
    print("未找到content赋值位置")

# 在return之前添加缓存保存
# 找到最后的return np_jsonify位置
pattern = r"(return np_jsonify\(\{[\s\S]*?'trigger_detected': trigger_detected[\s\S]*?\}\))"
match = re.search(pattern, content)

if match:
    old_text = match.group(1)
    # 在return之前添加缓存保存
    new_text = """# AutoResearch优化: 保存结果缓存
        response_json = np_jsonify({
            'success': True,
            'processed_content': processed_content,
            'brain_context': {
                'intent': intent,
                'results': brain_results,
                'timestamp': datetime.now().isoformat(),
                'provider': provider,
                'trigger_detected': trigger_detected
            }
        })
        if len(RESULT_CACHE) < RESULT_CACHE_MAX:
            RESULT_CACHE[result_cache_key] = (response_json, datetime.now())
        return response_json"""
    
    content = content.replace(old_text, new_text, 1)
    print("缓存保存逻辑已添加")
else:
    print("未找到return位置，使用备用方案")

# 写回文件
with open(r'C:\Users\Administrator\.openclaw\brain-system\core\brain_entry.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("结果缓存优化完成!")