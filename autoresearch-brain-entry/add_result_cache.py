# -*- coding: utf-8 -*-
"""添加结果缓存到brain_entry.py"""

import re

# 读取文件
with open(r'C:\Users\Administrator\.openclaw\brain-system\core\brain_entry.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 在全局变量区域添加结果缓存
# 找到executor定义位置
executor_pattern = r"executor\s*=\s*ThreadPoolExecutor"
executor_match = re.search(executor_pattern, content)

if executor_match:
    insert_pos = executor_match.start()
    result_cache_code = """
# AutoResearch优化: 结果缓存
RESULT_CACHE = {}  # content hash -> (result, timestamp)
RESULT_CACHE_TTL = 60  # 缓存有效期（秒）
RESULT_CACHE_MAX_SIZE = 500  # 最大缓存条目

"""
    content = content[:insert_pos] + result_cache_code + content[insert_pos:]
    print("结果缓存变量已添加")
else:
    print("未找到executor定义")

# 2. 在/entry endpoint添加缓存逻辑
# 找到@app.route('/entry')位置
entry_pattern = r"@app\.route\('/entry',\s*methods=\['POST'\]\)\s*def\s*entry\(\):"
entry_match = re.search(entry_pattern, content)

if entry_match:
    # 找到函数开始的下一行
    func_start = entry_match.end()
    
    # 添加缓存检查逻辑
    cache_check_code = """
    # AutoResearch优化: 检查结果缓存
    cache_key = hashlib.md5((content + str(user_action)).encode('utf-8')).hexdigest()
    if cache_key in RESULT_CACHE:
        cached_result, cached_time = RESULT_CACHE[cache_key]
        if (datetime.now() - cached_time).total_seconds() < RESULT_CACHE_TTL:
            logger.info(f"Result cache hit: {cache_key}")
            return cached_result
    
"""
    content = content[:func_start] + cache_check_code + content[func_start:]
    print("缓存检查逻辑已添加")
else:
    print("未找到/entry endpoint")

# 3. 在return之前添加缓存保存逻辑
# 找到return np_jsonify位置
return_pattern = r"return np_jsonify\(\{\s*'success':\s*True,"
return_match = re.search(return_pattern, content)

if return_match:
    # 找到return语句开始位置
    return_start = return_match.start()
    
    # 在return之前添加缓存保存
    cache_save_code = """
        # AutoResearch优化: 保存结果缓存
        result = {
            'success': True,
            'processed_content': processed_content,
            'brain_context': {
                'intent': intent,
                'results': brain_results,
                'timestamp': datetime.now().isoformat(),
                'provider': provider,
                'trigger_detected': trigger_detected
            }
        }
        if len(RESULT_CACHE) < RESULT_CACHE_MAX_SIZE:
            RESULT_CACHE[cache_key] = (np_jsonify(result), datetime.now())
        
        return np_jsonify(result)
"""
    # 需要替换整个return块
    # 先找到return块的结束位置（下一个函数定义或@app.route）
    next_route_pattern = r"\n@app\.route"
    next_route_match = re.search(next_route_pattern, content[return_start:])
    
    if next_route_match:
        return_end = return_start + next_route_match.start()
        content = content[:return_start] + cache_save_code + content[return_end:]
        print("缓存保存逻辑已添加")
    else:
        print("未找到return块结束位置")
else:
    print("未找到return语句")

# 写回文件
with open(r'C:\Users\Administrator\.openclaw\brain-system\core\brain_entry.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("结果缓存已添加到brain_entry.py!")