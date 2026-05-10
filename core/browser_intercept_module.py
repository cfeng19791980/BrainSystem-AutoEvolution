# -*- coding: utf-8 -*-
"""
BrowserInterceptor 调用模块 — browser_intercept_module.py

职责：
  1. 接收 Brain 的拦截指令 → 调用 BrowserInterceptor 执行网络劫持
  2. 将原始拦截数据交给本地 LLM（Qwen3.5-9B）解析
  3. 严格校验 LLM 输出，返回结构化结果

调用方式（独立模块，不依赖 brain_entry）：
  result = intercept_and_parse(instruction)
  
指令格式：
  {
    "task": "intercept_quote",
    "url": "https://gu.qq.com/sh600519",
    "filters": ["gtimg"],
    "max_wait_seconds": 10,
    "expected_fields": ["price", "pct_change", "name"],
    "fallback_url": "https://quote.eastmoney.com/sh600519.html"
  }
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# 引入 BrowserInterceptor
sys.path.insert(0, r'C:\dev')
from browser_interceptor import BrowserInterceptor

logger = logging.getLogger(__name__)

# ─── 配置 ───

# 本地 LLM（llama.cpp）API 地址
LLM_API_URL = "http://127.0.0.1:1235/v1/chat/completions"
LLM_MODEL = "qwen3-vl-4b-instruct"
LLM_TIMEOUT = 30  # LLM 推理超时秒数
LLM_MAX_TOKENS = 500  # 输出字数上限，超限丢弃

# 数据大小边界
MAX_RAW_BYTES = 500_000  # 原始拦截数据上限 500KB
MAX_CONTEXT_CHARS = 8000  # 喂给 LLM 的文本截断长度

# 拦截默认参数
DEFAULT_WAIT_SECONDS = 10
DEFAULT_FILTERS = ['gtimg', 'qt.gtimg', 'push2.eastmoney']


def intercept_and_parse(instruction: Dict) -> Dict:
    """
    执行拦截 + LLM 解析，返回结构化结果。
    这是本模块的核心接口。所有边界控制都在这里。

    Args:
        instruction: {
            "task": str,           # 任务类型
            "url": str,            # 目标 URL
            "filters": List[str],  # URL 过滤关键字
            "max_wait_seconds": int,
            "expected_fields": List[str],
            "fallback_url": str,   # 可选，主目标失败时回退
        }

    Returns:
        {
            "status": "ok" | "rejected" | "error" | "empty",
            "task": str,
            "fields": Dict | None,
            "confidence": float,
            "reason": str,
            "details": Dict,       # 调试信息
        }
    """
    # ── 第一步：校验指令参数 ──
    validation = _validate_instruction(instruction)
    if validation is not None:
        return validation

    url = instruction['url']
    filters = instruction.get('filters', DEFAULT_FILTERS)
    max_wait = instruction.get('max_wait_seconds', DEFAULT_WAIT_SECONDS)
    expected_fields = instruction.get('expected_fields', [])
    fallback_url = instruction.get('fallback_url')

    task_start = time.time()

    # ── 第二步：执行拦截 ──
    try:
        raw_data = _execute_intercept(url, filters, max_wait)
    except Exception as e:
        logger.error(f"拦截执行失败: {e}")

        # 有回退 URL 则尝试
        if fallback_url:
            logger.info(f"尝试回退 URL: {fallback_url}")
            try:
                raw_data = _execute_intercept(fallback_url, filters, max_wait)
            except Exception as e2:
                return _error_result(f"拦截执行失败（含回退）: {e2}", task_start)

        else:
            return _error_result(f"拦截执行失败: {e}", task_start)

    if not raw_data:
        return {
            'status': 'empty',
            'task': instruction.get('task', 'unknown'),
            'fields': None,
            'confidence': 0.0,
            'reason': 'intercept returned no data',
            'details': {'elapsed_sec': round(time.time() - task_start, 1)},
        }

    # ── 第三步：构建 LLM 指令（严格边界） ──
    llm_prompt = _build_llm_prompt(instruction, raw_data)

    # ── 第四步：调用本地 LLM 解析 ──
    try:
        llm_response = _call_local_llm(llm_prompt)
    except Exception as e:
        return _error_result(f"LLM 调用失败: {e}", task_start)

    # ── 第五步：严格校验 LLM 输出 ──
    validated = _validate_llm_output(llm_response, instruction, task_start)

    return validated


def _execute_intercept(url: str, filters: List[str], max_wait: int) -> List[Dict]:
    """
    执行浏览器拦截，返回原始拦截数据。
    """
    interceptor = BrowserInterceptor(headless=True)
    interceptor.start(url)

    for f in filters:
        interceptor.intercept_fetch(filter=[f])
        interceptor.intercept_xhr(filter=[f])

    time.sleep(max_wait)

    raw = interceptor.flush()
    interceptor.close()

    # 数据大小边界
    raw_str = json.dumps(raw, ensure_ascii=False, default=str)
    if len(raw_str.encode('utf-8')) > MAX_RAW_BYTES:
        logger.warning(f"拦截数据过大 ({len(raw_str)} 字符)，截断")
        raw = raw[:50]  # 只保留前 50 条

    return raw


def _build_llm_prompt(instruction: Dict, raw_data: List[Dict]) -> str:
    """
    构建 LLM 指令。
    严格约束：固定 JSON 结构、字数上限、字段白名单。
    """
    task = instruction.get('task', 'unknown')
    expected_fields = instruction.get('expected_fields', [])

    # 截断原始数据
    raw_text = json.dumps(raw_data, ensure_ascii=False, default=str)
    if len(raw_text) > MAX_CONTEXT_CHARS:
        raw_text = raw_text[:MAX_CONTEXT_CHARS] + "\n...[截断]"

    prompt = f"""你是一个严格的数据提取器。只做以下事情：

【任务】
从浏览器拦截的 API 响应中提取 {task} 数据。

【规则-必须遵守】
1. 只输出 JSON，不加任何其他文字
2. 只提取指定字段：{', '.join(expected_fields) if expected_fields else '所有可用字段'}
3. 如果找不到指定字段的值，设该字段为 null
4. 如果所有核心字段都为空，设 "empty": true
5. confidence=0.0~1.0 表示你对数据的信心
6. 不得编造任何数据
7. JSON 总长度不超过 500 字符

【输出格式】
{{
    "task": "{task}",
    "fields": {{
        "name": "<字符串或null>",
        "price": <数字或null>,
        "pct_change": <数字或null>
    }},
    "confidence": 0.0~1.0,
    "empty": false
}}

【数据源】
{raw_text}"""

    return prompt


def _call_local_llm(prompt: str) -> str:
    """
    调用本地 LLM（llama.cpp / LM Studio）。
    """
    import requests

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.0,      # 确定输出，不创造
        "max_tokens": LLM_MAX_TOKENS,
        "stream": False,
    }

    resp = requests.post(
        LLM_API_URL,
        json=payload,
        timeout=LLM_TIMEOUT,
    )
    resp.raise_for_status()

    result = resp.json()
    content = result["choices"][0]["message"]["content"]

    return content


def _validate_llm_output(response: str, instruction: Dict, start_time: float) -> Dict:
    """
    严格校验 LLM 输出。8 道关卡。
    """
    task = instruction.get('task', 'unknown')
    expected_fields = instruction.get('expected_fields', [])
    elapsed = round(time.time() - start_time, 1)

    # 关卡 1：字数检查
    if len(response) > LLM_MAX_TOKENS * 2:
        return {
            'status': 'rejected',
            'task': task,
            'fields': None,
            'confidence': 0.0,
            'reason': f'exceeded length limit ({len(response)} > {LLM_MAX_TOKENS * 2})',
            'details': {'elapsed_sec': elapsed},
        }

    # 关卡 2：JSON 解析
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        # 尝试提取 JSON 块
        import re
        m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
            except:
                return _reject_result(task, 'invalid_json_no_markdown', elapsed)
        else:
            m = re.search(r'(\{.*\})', response, re.DOTALL)
            if m:
                try:
                    data = json.loads(m.group(1))
                except:
                    return _reject_result(task, 'invalid_json', elapsed)
            else:
                return _reject_result(task, 'no_json_found', elapsed)

    # 关卡 3：字数（精细检查）
    response_str = json.dumps(data, ensure_ascii=False)
    if len(response_str) > LLM_MAX_TOKENS:
        return _reject_result(task, f'json_oversized ({len(response_str)} > {LLM_MAX_TOKENS})', elapsed)

    # 关卡 4：空数据
    if data.get('empty') is True:
        return _reject_result(task, 'empty_data_flag', elapsed)

    # 关卡 5：信心检查
    confidence = data.get('confidence', 0) or 0
    if confidence < 0.7:
        return _reject_result(task, f'low_confidence ({confidence})', elapsed)

    # 关卡 6：核心字段检查
    fields = data.get('fields', {}) or {}
    if task == 'intercept_quote':
        if fields.get('price') is None:
            return _reject_result(task, 'missing_core_field:price', elapsed)

    # 关卡 7：字段匹配（expected_fields 中的存在性检查）
    if expected_fields:
        missing = [f for f in expected_fields if f not in fields]
        if missing:
            # 不致命，仅降 confidence
            confidence = max(0.0, confidence - 0.1)

    # 通过所有关卡
    return {
        'status': 'ok',
        'task': task,
        'fields': fields,
        'confidence': round(confidence, 2),
        'reason': 'all_checks_passed',
        'details': {
            'elapsed_sec': elapsed,
            'field_count': len(fields),
            'expected_fields_match': len(missing) == 0 if 'missing' in dir() else True,
        },
    }


def _validate_instruction(instruction: Dict) -> Optional[Dict]:
    """校验指令参数合法性"""
    if not isinstance(instruction, dict):
        return _error_result('instruction must be a dict')

    if 'url' not in instruction or 'task' not in instruction:
        return _error_result('instruction missing url or task')

    url = instruction['url']
    # 防止注入（先于协议检查）
    forbidden = ['file:', 'localhost', '127.0.0.1', '0.0.0.0']
    for f in forbidden:
        if f in url:
            return _error_result(f'url contains forbidden pattern: {f}')

    if not url.startswith(('http://', 'https://')):
        return _error_result(f'invalid url: {url}')

    return None


def _error_result(msg: str, start_time: float = None) -> Dict:
    elapsed = round(time.time() - start_time, 1) if start_time else 0
    return {'status': 'error', 'fields': None, 'confidence': 0.0, 'reason': msg, 'details': {'elapsed_sec': elapsed}}


def _reject_result(task: str, reason: str, elapsed: float) -> Dict:
    return {
        'status': 'rejected',
        'task': task,
        'fields': None,
        'confidence': 0.0,
        'reason': reason,
        'details': {'elapsed_sec': elapsed},
    }


# ─── 便捷接口 ───

def quick_quote(stock_code: str) -> Dict:
    """
    快速查询股票行情。一行调用。
    
    Args:
        stock_code: "600519" 或 "600519.SH"
    
    Returns:
        同 intercept_and_parse 返回值
    """
    code = stock_code.split('.')[0]
    exchange = 'sh' if code.startswith(('6', '9')) else 'sz'

    instruction = {
        "task": "intercept_quote",
        "url": f"https://gu.qq.com/{exchange}{code}",
        "filters": ["gtimg", "qt.gtimg"],
        "max_wait_seconds": 10,
        "expected_fields": ["name", "code", "price", "pct_change", "high", "low", "volume_hand"],
    }

    return intercept_and_parse(instruction)


# ─── 测试入口 ───
if __name__ == '__main__':
    # 测试快速行情查询
    import pprint
    result = quick_quote("600519")
    pprint.pprint(result)
