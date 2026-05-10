# -*- coding: utf-8 -*-
"""
搜索意图识别模块 — realtime_intent.py

职责：独立分析用户输入是否属于"需要实时数据支撑"的搜索意图。
      不依赖 Brain 系统其他模块，可被 brain_entry 或其他模块调用。

搜索意图定义：
  用户问题需要访问实时网页/API 数据才能回答，
  无法仅凭已有的知识库/记忆库内容作答。

输出：
  - is_realtime: bool — 是否搜索意图
  - realtime_type: str — 子类型（stock_quote / news / general_search / timely_query）
  - confidence: float — 匹配置信度 (0~1)
  - keywords: list — 提取的关键词
  - fallback_viable: bool — 无法获取实时数据时能否回退到知识库
"""

import re
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ─── 搜索意图模式定义（按类别分组） ───

# 行情类（最高优先级）
STOCK_QUOTE_PATTERNS = [
    r'(股价|行情|股票)\s*(多少|查询|代码|名字|名称|涨|跌)',
    r'(最新|当前|今天)\s*(价格|股价|行情|交易)',
    r'(涨了|跌了|涨跌|涨幅|跌幅)\s*(多少|几个点)',
    r'多少\s*(钱|元|块)',
    r'查[一1]下\s*.{0,10}(股|价格|行情)',
    r'(茅台|腾讯|阿里|比亚迪|宁德|平安|招商|兴业|工商|农业|建设)',
    r'\d{6}.*(股|行情|价格)',  # 6位数字+股/行情（更宽松）
    r'\d{6}$',  # 纯6位数字（股票代码）
]

# 新闻/公告类
NEWS_PATTERNS = [
    r'今天.*新闻|最新.*(公告|消息|动态)',
    r'(发生|发布|公布|更新).*(什么|哪些|了)',
    r'(头条|热搜|热点)',
    r'(公告|新闻|消息)\s*(搜索|查询|查看)',
]

# 汇率/市场数据类
MARKET_PATTERNS = [
    r'(汇率|美元|欧元|英镑|日元|港币)\s*(兑|汇率|价格|多少)',
    r'(黄金|白银|原油|期货|比特币)\s*(价格|行情|多少)',
    r'(大盘|上证|深证|创业板|科创板)\s*(指数|多少|涨跌)',
]

# 通用搜索类（用户明确要求搜索）
GENERAL_SEARCH_PATTERNS = [
    r'(帮我查|帮我搜|搜索一下|查一下|搜一下|百度一下|Google)',
    r'(搜索|查询|查找)\s*.{2,}',
]

# 时效性查询
# 时效性查询
TIMELY_QUERY_PATTERNS = [
    r'(现在|当前|最近|目前)\s*.{1,}(怎么样|情况|状态|如何|是什么)',
    r'(是不是还|还活着|还在|还有没有|还能用|还能买)',
    r'(今天|昨天|明天|这周|本月)\s*.{2,}(事件|新闻|公告|行情)',
    r'(最近|最新|今天)\s*(新闻|公告|事件|情况)',
    r'(有什么|什么.*(新闻|公告|事件))',
]

def analyze_realtime_intent(content: str) -> Dict:
    """
    分析用户输入是否为搜索意图（需要实时数据）。

    Args:
        content: 用户输入文本

    Returns:
        dict: {
            'is_realtime': bool,
            'realtime_type': str | None,
            'confidence': float,
            'keywords': List[str],
            'fallback_viable': bool,
            'reason': str
        }
    """
    if not content or not isinstance(content, str):
        return _default_result(reason='empty_input')

    content_clean = content.strip().lower()

    # 按优先级顺序检测
    checks = [
        ('stock_quote', STOCK_QUOTE_PATTERNS, 0.9, True),
        ('market_data', MARKET_PATTERNS, 0.85, True),
        ('news', NEWS_PATTERNS, 0.85, True),
        ('general_search', GENERAL_SEARCH_PATTERNS, 0.8, False),
        ('timely_query', TIMELY_QUERY_PATTERNS, 0.7, True),
    ]

    for realtime_type, patterns, base_confidence, fallback in checks:
        matched_pattern = _match_patterns(content_clean, patterns)
        if matched_pattern:
            keywords = _extract_keywords(content, realtime_type)
            return {
                'is_realtime': True,
                'realtime_type': realtime_type,
                'confidence': _adjust_confidence(base_confidence, content),
                'keywords': keywords,
                'fallback_viable': fallback,
                'reason': f'matched: {realtime_type} / {matched_pattern}',
            }

    # 未匹配任何搜索意图
    return _default_result(reason='no_realtime_match')


def _match_patterns(content: str, patterns: List[str]) -> Optional[str]:
    """匹配模式列表，返回第一个匹配的模式"""
    for pattern in patterns:
        if re.search(pattern, content):
            return pattern
    return None


def _extract_keywords(content: str, realtime_type: str) -> List[str]:
    """提取关键词，用于后续构造拦截指令"""
    keywords = []

    # 提取股票代码（6位数字）
    codes = re.findall(r'\b\d{6}\b', content)
    keywords.extend(codes)

    # 提取常见股票名
    stock_names = re.findall(
        r'(茅台|腾讯|阿里|比亚迪|宁德|平安|招商|兴业|'
        r'工商|农业|建设|中信|华泰|海通|国泰|君安|'
        r'中芯|华为|小米|百度|京东|拼多多|美团)',
        content
    )
    keywords.extend(stock_names)

    # 提取数字+单位组合（如：多少钱、多少元）
    amounts = re.findall(r'(\d+)\s*(元|块|点|个|百分比|%)', content)
    keywords.extend([f"{a}{u}" for a, u in amounts])

    return keywords


def _adjust_confidence(base: float, content: str) -> float:
    """根据内容质量微调置信度"""
    # 有具体数字 → 提升
    if re.search(r'\d+', content):
        base = min(1.0, base + 0.05)
    # 有股票代码 → 明显是行情查询
    if re.search(r'\b\d{6}\b', content):
        base = min(1.0, base + 0.1)
    # 含疑问词 → 提升
    if '?' in content or '？' in content:
        base = min(1.0, base + 0.05)
    # 长度太短 → 降低
    if len(content) < 3:
        base = max(0.0, base - 0.2)
    return round(base, 2)


def _default_result(reason: str = 'unknown') -> Dict:
    return {
        'is_realtime': False,
        'realtime_type': None,
        'confidence': 0.0,
        'keywords': [],
        'fallback_viable': True,
        'reason': reason,
    }


# ─── 便捷调用接口 ───

def is_realtime_query(content: str) -> bool:
    """快速判断：用户输入是否是需要实时数据的查询"""
    result = analyze_realtime_intent(content)
    return result['is_realtime'] and result['confidence'] >= 0.7


def get_intercept_type(content: str) -> Optional[str]:
    """获取最匹配的拦截类型"""
    result = analyze_realtime_intent(content)
    return result['realtime_type'] if result['is_realtime'] else None


# ─── 测试入口 ───
if __name__ == '__main__':
    test_cases = [
        "茅台现在多少钱？",
        "今天上证指数多少？",
        "帮我查一下最近的新闻",
        "Python怎么优化性能？",
        "600519的股价",
        "美元兑人民币汇率",
        "帮我搜一下AI的最新进展",
        "你好",
        "苹果公司股价多少？",
        "最近有什么公告？",
    ]

    for case in test_cases:
        result = analyze_realtime_intent(case)
        tag = "🔴 搜索意图" if result['is_realtime'] else "⚪ 普通查询"
        print(f"{tag} [{result['realtime_type'] or 'none'}] "
              f"conf={result['confidence']} "
              f"kw={result['keywords'][:3]} "
              f"→ '{case[:20]}...'")
