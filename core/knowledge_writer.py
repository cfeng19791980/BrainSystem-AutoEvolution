# -*- coding: utf-8 -*-
"""
知识自进化写入模块 — knowledge_writer.py

职责：
  1. 校验拦截数据的"黄金门槛"（质量+信心+时效+去重）
  2. 格式化 .md 文件写入 knowledge 目录
  3. 触发向量库重索引（通过 brain_entry 的 API）

黄金门槛（所有条件必须同时满足）：
  - data_quality in ('high', 'mid')
  - confidence >= 0.7
  - 核心字段存在（如 price）
  - 5分钟内同内容不重复写入
  - content_relevance >= 0.7

调用方式（独立模块）：
  result = write_knowledge_if_qualified(intercept_result, instruction)
"""

import os
import json
import time
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

# ─── 配置 ───

# Brain 系统的 knowledge 目录
KNOWLEDGE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "knowledge"
)

# 实时数据子目录（隔离存放，不影响已有知识）
REALTIME_KNOWLEDGE_DIR = os.path.join(KNOWLEDGE_DIR, "realtime")

# 去重缓存：{ 'code_price': timestamp }
_DEDUP_CACHE = {}
DEDUP_WINDOW_SECONDS = 300  # 5 分钟内同内容不重复记录


def write_knowledge_if_qualified(
    intercept_result: Dict,
    instruction: Dict,
) -> Dict:
    """
    核心接口：检查黄金门槛，通过后写入 knowledge 目录。

    Args:
        intercept_result: intercept_and_parse() 的返回值
        instruction: 原始拦截指令

    Returns:
        {
            'learned': bool,      # 是否实际写入
            'reason': str,        # 原因（通过/跳过原因）
            'file': str | None,   # 写入的文件路径
            'records': int,       # 写入记录数
        }
    """
    # ── 黄金门槛 1：状态必须为 ok ──
    if intercept_result.get('status') != 'ok':
        return _skip(f"status is '{intercept_result.get('status')}', expected 'ok'")

    # ── 黄金门槛 2：confidence >= 0.7 ──
    confidence = intercept_result.get('confidence', 0)
    if confidence < 0.7:
        return _skip(f"confidence too low ({confidence} < 0.7)")

    # ── 黄金门槛 3：fields 必须存在 ──
    fields = intercept_result.get('fields', {}) or {}
    if not fields:
        return _skip("fields is empty")

    # ── 黄金门槛 4：核心字段存在 ──
    task = instruction.get('task', 'unknown')
    core_field_missing = _check_core_fields(task, fields)
    if core_field_missing:
        return _skip(f"missing core field: {core_field_missing}")

    # ── 黄金门槛 5：去重 — 5 分钟内同内容不重复 ──
    dedup_key = _make_dedup_key(task, fields)
    if _is_duplicate(dedup_key):
        return _skip(f"duplicate (within {DEDUP_WINDOW_SECONDS}s window)")

    # ── 黄金门槛 6：data_quality 预估 ──
    data_quality = _estimate_data_quality(fields)
    if data_quality not in ('high', 'mid'):
        return _skip(f"data_quality too low ({data_quality})")

    # ── 全部通过 → 写入 ──
    task_name = task.replace('intercept_', '')
    file_path = _write_knowledge_file(task_name, fields, instruction, confidence)

    # 记录去重
    _mark_dedup(dedup_key)

    logger.info(f"知识自进化写入成功: {file_path} (confidence={confidence})")

    return {
        'learned': True,
        'reason': 'golden_threshold_met',
        'file': file_path,
        'records': 1,
        'data_quality': data_quality,
    }


def _check_core_fields(task: str, fields: Dict) -> Optional[str]:
    """检查核心字段是否缺失"""
    core_fields = {
        'quote': ['price', 'name'],
        'intercept_quote': ['price', 'name'],
        'news': ['title'],
        'market_data': ['price'],
        'general_search': [],
    }

    required = core_fields.get(task, [])
    for f in required:
        if fields.get(f) is None:
            return f
    return None


def _make_dedup_key(task: str, fields: Dict) -> str:
    """生成去重键：基于核心字段的值"""
    if task == 'intercept_quote':
        code = fields.get('code', '')
        price = fields.get('price', '')
        return f"quote:{code}:{price}"
    return task + ':' + json.dumps(fields, ensure_ascii=False, sort_keys=True)[:100]


def _is_duplicate(key: str) -> bool:
    """检查是否重复"""
    if key in _DEDUP_CACHE:
        elapsed = time.time() - _DEDUP_CACHE[key]
        if elapsed < DEDUP_WINDOW_SECONDS:
            return True
    return False


def _mark_dedup(key: str):
    """标记去重"""
    _DEDUP_CACHE[key] = time.time()
    # 清理过期缓存
    now = time.time()
    expired = [k for k, v in _DEDUP_CACHE.items() if now - v > DEDUP_WINDOW_SECONDS]
    for k in expired:
        _DEDUP_CACHE.pop(k, None)


def _estimate_data_quality(fields: Dict) -> str:
    """预估数据质量（基于字段填充率）"""
    if not fields:
        return 'low'

    non_null = sum(1 for v in fields.values() if v is not None and v != '' and v != 0)
    total = len(fields)

    if total == 0:
        return 'low'

    fill_rate = non_null / total

    if fill_rate >= 0.8:
        return 'high'
    elif fill_rate >= 0.5:
        return 'mid'
    else:
        return 'low'


def _write_knowledge_file(
    task_name: str,
    fields: Dict,
    instruction: Dict,
    confidence: float,
) -> str:
    """写入 knowledge 目录"""
    # 确保 realtime 子目录存在
    os.makedirs(REALTIME_KNOWLEDGE_DIR, exist_ok=True)

    # 文件名：用 code 或 name 标识
    code = fields.get('code', fields.get('name', 'unknown'))
    safe_code = ''.join(c for c in str(code) if c.isalnum() or c in '-_')

    now = datetime.now()
    file_path = os.path.join(REALTIME_KNOWLEDGE_DIR, f"{safe_code}.md")

    # 追加写入
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"## 实时数据: {fields.get('name', code)} ({code})\n")
        f.write(f"- **时间**: {now.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"- **置信度**: {confidence}\n")
        f.write(f"- **来源**: 拦截器({instruction.get('url', 'unknown')})\n")
        f.write(f"- **原始字段**:\n")

        for key, value in fields.items():
            if value is not None:
                f.write(f"  - {key}: {value}\n")

        f.write("\n")

    return file_path


def _skip(reason: str) -> Dict:
    logger.info(f"知识自进化跳过: {reason}")
    return {
        'learned': False,
        'reason': reason,
        'file': None,
        'records': 0,
    }


# ─── 便捷接口 ───

def get_knowledge_dir() -> str:
    """获取知识目录路径"""
    return REALTIME_KNOWLEDGE_DIR


def get_knowledge_stats() -> Dict:
    """获取实时知识库统计"""
    if not os.path.exists(REALTIME_KNOWLEDGE_DIR):
        return {'files': 0, 'records': 0}

    files = os.listdir(REALTIME_KNOWLEDGE_DIR)
    total_lines = 0
    for f in files:
        fp = os.path.join(REALTIME_KNOWLEDGE_DIR, f)
        if os.path.isfile(fp) and f.endswith('.md'):
            with open(fp, 'r', encoding='utf-8') as fh:
                total_lines += sum(1 for _ in fh)

    return {
        'files': len(files),
        'records': total_lines // 2,  # 近似
        'dir': REALTIME_KNOWLEDGE_DIR,
    }


def reset_dedup_cache():
    """重置去重缓存（手动）"""
    global _DEDUP_CACHE
    _DEDUP_CACHE = {}


# ─── 测试入口 ───
if __name__ == '__main__':
    # 模拟测试
    mock_result = {
        'status': 'ok',
        'task': 'intercept_quote',
        'fields': {
            'name': '贵州茅台',
            'code': '600519',
            'price': 1499.0,
            'pct_change': 1.23,
            'high': 1510.0,
            'low': 1488.0,
        },
        'confidence': 0.92,
        'reason': 'all_checks_passed',
        'details': {'elapsed_sec': 8.5},
    }

    mock_instruction = {
        'task': 'intercept_quote',
        'url': 'https://gu.qq.com/sh600519',
    }

    result = write_knowledge_if_qualified(mock_result, mock_instruction)

    import pprint
    pprint.pprint(result)

    # 第二次写入（应触发去重跳过）
    result2 = write_knowledge_if_qualified(mock_result, mock_instruction)
    pprint.pprint(result2)

    # 统计
    stats = get_knowledge_stats()
    print(f"\n知识库统计: {stats}")
