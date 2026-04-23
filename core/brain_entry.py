# -*- coding: utf-8 -*-
"""
Brain Entry V3.0 - 本地向量优先版
=====================================
改进内容：
1. FAISS + Sentence-Transformers 本地向量搜索
2. 完全离线运行，无网络依赖
3. 向量维度384，真实语义理解
4. 多级Fallback: local_sentence > openai > fallback
5. 流程模板系统（10个标准流程）
6. Self-Improving自我进化机制
7. 请求队列+超时控制
8. LRU缓存机制
9. 增强健康检查
10. 反馈学习记录
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json
import os
import sqlite3
import hashlib
import re
import logging
import threading
import time
import sys
import queue
import traceback
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from pathlib import Path
import numpy as np

# ============================================================
# Custom JSON Encoder for numpy types
# ============================================================
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    """Handle numpy.float32 and other numpy types"""
    def default(self, obj):
        if isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

# ============================================================
# 日志配置
# ============================================================
LOG_DIR = "C:/Users/Administrator/.openclaw/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f'{LOG_DIR}/brain_entry.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('BrainEntry')

# ============================================================
# 配置区
# ============================================================
BRAIN_CONFIG = {
    # Brain System 集中目录 (2026-04-22)
    "brain_root": "C:/Users/Administrator/.openclaw/brain-system",
    "memory_db": "C:/Users/Administrator/.openclaw/brain-system/data/.brain_vectors.db",
    "memory_dir": "C:/Users/Administrator/.openclaw/workspace-工程师/memory",  # 保留原位置（共享memory）
    "knowledge_dir": "C:/Users/Administrator/.openclaw/brain-system/data/knowledge",
    "feedback_db": "C:/Users/Administrator/.openclaw/brain-system/data/.brain_feedback.db",
    "cache_db": "C:/Users/Administrator/.openclaw/brain-system/data/.brain_cache.db",
    
    # Self-Improving配置
    "learnings_dir": "C:/Users/Administrator/.openclaw/brain-system/data/.learnings",
    "pattern_db": "C:/Users/Administrator/.openclaw/brain-system/data/.brain_patterns.db",
    "promotion_threshold": 3,  # Recurrence-Count阈值
    
    # Embedding配置
    "embedding_provider": "auto",  # auto, openai, local, fallback
    "openai_api_base": "https://api.openai.com/v1",
    "openai_model": "text-embedding-ada-002",
    "local_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "local_model_timeout": 3,  # 本地模型测试超时
    
    # 稳定性配置
    "default_confidence": 0.3,
    "min_confidence": 0.5,
    "max_results": 5,
    "brain_host": "127.0.0.1",
    "brain_port": 5002,
    "heartbeat_interval": 30,
    "max_request_timeout": 10,
    "thread_pool": 4,
    "max_queue_size": 100,
    "retry_attempts": 3,
    "retry_delay": 1.0,
    
    # 缓存配置
    "cache_enabled": True,
    "cache_ttl": 3600,  # 1小时
    "cache_max_size": 1000,
    
    # 安全性配置
    "input_max_length": 100000,  # 最大输入长度（增加到50K支持session summary）
    "input_dangerous_patterns": [
        '<script', 'javascript:', 'onerror=', 'onload=',
        'eval(', 'exec(', '__import__', 'os.system', 'subprocess',
        'DROP TABLE', 'DELETE FROM', 'INSERT INTO', '--',
        '../', '..\\\\', 'file://', 'data:text/html'
    ],
    
    # 健壮性配置
    "backup_enabled": True,
    "backup_dir": "C:/Users/Administrator/.openclaw/backups",
    "backup_interval": 3600,  # 1小时自动备份
    "timeout_levels": {
        "urgent": 5,      # 紧急请求超时5秒
        "normal": 10,    # 普通请求超时10秒
        "heavy": 30      # 重型请求超时30秒
    },
    "rollback_enabled": True,
    "rollback_max_steps": 5  # 最大回滚步数
}

app = Flask(__name__)

# Custom jsonify with numpy support
def np_jsonify(data):
    """jsonify with numpy.float32 support"""
    return app.response_class(
        json.dumps(data, cls=NumpyEncoder, ensure_ascii=False),
        mimetype='application/json'
    )

# ============================================================
# 请求队列与线程池
# ============================================================
request_queue = queue.Queue(maxsize=BRAIN_CONFIG['max_queue_size'])
executor = ThreadPoolExecutor(max_workers=BRAIN_CONFIG['thread_pool'])

# AutoResearch优化: 结果缓存（API响应级）
RESULT_CACHE = {}  # query hash -> (response_json, timestamp)
RESULT_CACHE_TTL = 60  # 缓存有效期（秒）
RESULT_CACHE_MAX = 500  # 最大缓存条目
RESULT_CACHE_HITS = 0  # 结果缓存命中统计

# ============================================================
# P3: 冷热数据分层缓存（豆包建议）
# ============================================================
CACHE_TIERS = {
    'hot': {'ttl': 300, 'max_size': 100, 'desc': '高频热数据'},  # 5分钟
    'warm': {'ttl': 120, 'max_size': 200, 'desc': '中频温数据'},   # 2分钟
    'cold': {'ttl': 60, 'max_size': 200, 'desc': '低频冷数据'},   # 1分钟
}

# 分层缓存存储
HOT_CACHE = {}    # 内存常驻
WARM_CACHE = {}   # 内存缓冲
COLD_CACHE = {}   # 快过期

# 访问频率追踪
ACCESS_FREQUENCY = {}

def get_tier_cache_key(content):
    """根据访问频率分配缓存层级"""
    freq = ACCESS_FREQUENCY.get(content[:50], 0)
    if freq >= 10:  # 高频（10次以上）
        return 'hot'
    elif freq >= 3:  # 中频（3-10次）
        return 'warm'
    else:  # 低频
        return 'cold'

def tiered_cache_get(cache_key, content):
    """分层缓存获取"""
    tier = get_tier_cache_key(content)
    tier_cache = {'hot': HOT_CACHE, 'warm': WARM_CACHE, 'cold': COLD_CACHE}[tier]
    
    if cache_key in tier_cache:
        cached_response, cached_time = tier_cache[cache_key]
        ttl = CACHE_TIERS[tier]['ttl']
        if (datetime.now() - cached_time).total_seconds() < ttl:
            # 更新访问频率
            ACCESS_FREQUENCY[content[:50]] = ACCESS_FREQUENCY.get(content[:50], 0) + 1
            return cached_response, tier
    return None, None

def tiered_cache_set(cache_key, response, content):
    """分层缓存存储"""
    tier = get_tier_cache_key(content)
    tier_cache = {'hot': HOT_CACHE, 'warm': WARM_CACHE, 'cold': COLD_CACHE}[tier]
    max_size = CACHE_TIERS[tier]['max_size']
    
    # 缓存满时清理
    if len(tier_cache) >= max_size:
        _cleanup_tier_cache(tier)
    
    tier_cache[cache_key] = (response, datetime.now())
    logger.info(f'Cache stored in {tier} tier (size={len(tier_cache)})')

def _cleanup_tier_cache(tier):
    """清理过期缓存"""
    tier_cache = {'hot': HOT_CACHE, 'warm': WARM_CACHE, 'cold': COLD_CACHE}[tier]
    ttl = CACHE_TIERS[tier]['ttl']
    
    expired_keys = []
    for key, (_, cached_time) in tier_cache.items():
        if (datetime.now() - cached_time).total_seconds() > ttl:
            expired_keys.append(key)
    
    for key in expired_keys:
        del tier_cache[key]
    
    logger.info(f'{tier} cache cleanup: removed {len(expired_keys)} expired items')

# ============================================================
# P4: 缓存脏数据清洗（豆包建议）
# ============================================================
DIRTY_CACHE_THRESHOLD = 0.3  # 错误率阈值
CACHE_QUALITY_SCORES = {}  # 缓存质量评分

def mark_cache_dirty(cache_key, reason='error'):
    """标记缓存为脏数据"""
    if cache_key not in CACHE_QUALITY_SCORES:
        CACHE_QUALITY_SCORES[cache_key] = {'quality': 1.0, 'error_count': 0, 'last_error': None}
    
    CACHE_QUALITY_SCORES[cache_key]['error_count'] += 1
    CACHE_QUALITY_SCORES[cache_key]['last_error'] = datetime.now().isoformat()
    CACHE_QUALITY_SCORES[cache_key]['reason'] = reason
    
    # 降低质量评分
    current_quality = CACHE_QUALITY_SCORES[cache_key]['quality']
    CACHE_QUALITY_SCORES[cache_key]['quality'] = max(0, current_quality - 0.1)
    
    # 质量过低时标记为脏数据
    if CACHE_QUALITY_SCORES[cache_key]['quality'] < DIRTY_CACHE_THRESHOLD:
        _remove_dirty_cache(cache_key)
        logger.info(f'Cache marked as dirty and removed: {cache_key[:16]}... (reason={reason})')

def _remove_dirty_cache(cache_key):
    """移除脏缓存"""
    global RESULT_CACHE, HOT_CACHE, WARM_CACHE, COLD_CACHE
    
    # 从所有缓存层移除
    for cache_dict in [RESULT_CACHE, HOT_CACHE, WARM_CACHE, COLD_CACHE]:
        if cache_key in cache_dict:
            del cache_dict[cache_key]
    
    # 从质量评分中移除
    if cache_key in CACHE_QUALITY_SCORES:
        del CACHE_QUALITY_SCORES[cache_key]

def auto_cleanup_dirty_cache():
    """自动清理脏缓存（定时执行）"""
    dirty_count = 0
    for cache_key, scores in CACHE_QUALITY_SCORES.items():
        if scores['quality'] < DIRTY_CACHE_THRESHOLD:
            _remove_dirty_cache(cache_key)
            dirty_count += 1
    
    if dirty_count > 0:
        logger.info(f'Auto cleanup: removed {dirty_count} dirty cache items')
    return dirty_count

def get_cache_health_report():
    """缓存健康报告"""
    total_items = len(RESULT_CACHE) + len(HOT_CACHE) + len(WARM_CACHE) + len(COLD_CACHE)
    dirty_items = sum(1 for s in CACHE_QUALITY_SCORES.values() if s['quality'] < DIRTY_CACHE_THRESHOLD)
    avg_quality = sum(s['quality'] for s in CACHE_QUALITY_SCORES.values()) / len(CACHE_QUALITY_SCORES) if CACHE_QUALITY_SCORES else 1.0
    
    return {
        'total_cache_items': total_items,
        'dirty_items': dirty_items,
        'dirty_rate': dirty_items / total_items if total_items > 0 else 0,
        'avg_quality': avg_quality,
        'healthy': avg_quality >= 0.8 and dirty_items < total_items * 0.1
    }

# ============================================================
# P5: 日志分级管控（豆包建议）
# ============================================================
LOG_LEVELS = {
    'CRITICAL': {'enabled': True, 'desc': '关键错误'},
    'ERROR': {'enabled': True, 'desc': '错误信息'},
    'WARNING': {'enabled': True, 'desc': '警告信息'},
    'INFO': {'enabled': False, 'desc': '常规信息（关闭减少IO）'},
    'DEBUG': {'enabled': False, 'desc': '调试信息（关闭）'},
}

PERFORMANCE_STATS = {
    'total_requests': 0,
    'total_time_ms': 0,
    'cache_hits': 0,
    'cache_misses': 0,
    'errors': 0,
    'avg_response_time': 0,
}

def controlled_log(level, message):
    """受控日志输出"""
    if LOG_LEVELS.get(level, {}).get('enabled', False):
        logger.log(getattr(logging, level, logging.INFO), message)

def update_performance_stats(response_time, cache_hit=False, error=False):
    """更新性能统计"""
    PERFORMANCE_STATS['total_requests'] += 1
    PERFORMANCE_STATS['total_time_ms'] += response_time
    PERFORMANCE_STATS['avg_response_time'] = PERFORMANCE_STATS['total_time_ms'] / PERFORMANCE_STATS['total_requests']
    
    if cache_hit:
        PERFORMANCE_STATS['cache_hits'] += 1
    else:
        PERFORMANCE_STATS['cache_misses'] += 1
    
    if error:
        PERFORMANCE_STATS['errors'] += 1

def get_performance_report():
    """性能报告"""
    total = PERFORMANCE_STATS['total_requests']
    if total == 0:
        return {'message': 'No requests yet'}
    
    hit_rate = PERFORMANCE_STATS['cache_hits'] / total * 100
    error_rate = PERFORMANCE_STATS['errors'] / total * 100
    
    return {
        'total_requests': total,
        'avg_response_time_ms': round(PERFORMANCE_STATS['avg_response_time'], 2),
        'cache_hit_rate': round(hit_rate, 2),
        'error_rate': round(error_rate, 2),
        'hot_cache_size': len(HOT_CACHE),
        'warm_cache_size': len(WARM_CACHE),
        'cold_cache_size': len(COLD_CACHE),
    }

def reset_performance_stats():
    """重置性能统计"""
    global PERFORMANCE_STATS
    PERFORMANCE_STATS = {
        'total_requests': 0,
        'total_time_ms': 0,
        'cache_hits': 0,
        'cache_misses': 0,
        'errors': 0,
        'avg_response_time': 0,
    }
    controlled_log('INFO', 'Performance stats reset')

# ============================================================
# P6: 知识图谱构建 - 自动建立优化方法关联
# ============================================================
KNOWLEDGE_GRAPH_FILE = os.path.join(BRAIN_CONFIG.get('brain_root', 'C:/Users/Administrator/.openclaw/brain-system'), 'data', 'knowledge_graph.json')

def init_knowledge_graph():
    """初始化知识图谱"""
    default_graph = {
        'nodes': {
            # 性能优化类
            'embedding_cache': {
                'type': 'performance',
                'name': 'Embedding缓存',
                'effect': '-97% latency (146ms→0ms)',
                'prerequisites': ['embedding_model'],
                'applicable_to': ['vector_search', 'semantic_matching'],
                'source': 'experiment_5',
                'status': 'active'
            },
            'result_cache': {
                'type': 'performance',
                'name': '结果缓存',
                'effect': '-99.2% response (207ms→1.4ms)',
                'prerequisites': ['embedding_cache'],
                'applicable_to': ['api_response', 'intent_recognition'],
                'source': 'experiment_9',
                'status': 'active'
            },
            'hot_cache': {
                'type': 'performance',
                'name': '热数据缓存',
                'effect': '5min TTL高频数据常驻内存',
                'prerequisites': ['result_cache'],
                'applicable_to': ['frequent_queries'],
                'source': '豆包建议P3',
                'status': 'active'
            },
            # 准确率优化类
            'normalize_keywords': {
                'type': 'accuracy',
                'name': '语义归一化',
                'effect': '+95% cache_hit率',
                'prerequisites': ['result_cache'],
                'applicable_to': ['intent_matching'],
                'source': '豆包建议P0',
                'status': 'active'
            },
            'flow_templates': {
                'type': 'accuracy',
                'name': 'FLOW_TEMPLATES扩展',
                'effect': '+17pp准确率',
                'prerequisites': [],
                'applicable_to': ['intent_detection'],
                'source': 'experiment_6',
                'status': 'active'
            },
            'brain_patterns': {
                'type': 'accuracy',
                'name': 'brain_patterns扩展',
                'effect': '+10pp准确率',
                'prerequisites': ['flow_templates'],
                'applicable_to': ['keyword_matching'],
                'source': 'experiment_7',
                'status': 'active'
            },
            'composite_patterns': {
                'type': 'accuracy',
                'name': '复合关键词匹配',
                'effect': '解决关键词重叠冲突',
                'prerequisites': ['brain_patterns'],
                'applicable_to': ['conflict_resolution'],
                'source': 'experiment_11',
                'status': 'active'
            },
            'exact_priority': {
                'type': 'accuracy',
                'name': '精确匹配优先',
                'effect': '修复debug→fix误判',
                'prerequisites': ['flow_templates'],
                'applicable_to': ['intent_priority'],
                'source': 'experiment_10',
                'status': 'active'
            },
            # 自进化类
            'pattern_auto_collect': {
                'type': 'evolution',
                'name': 'Pattern自动沉淀',
                'effect': '高频指令自动收集',
                'prerequisites': ['brain_patterns'],
                'applicable_to': ['self_improvement'],
                'source': '豆包建议P1',
                'status': 'active'
            },
            'quality_scoring': {
                'type': 'evolution',
                'name': '执行质量打分',
                'effect': '自动评估任务质量',
                'prerequisites': [],
                'applicable_to': ['feedback_loop'],
                'source': '豆包建议P2',
                'status': 'active'
            },
            'dirty_cache_cleanup': {
                'type': 'evolution',
                'name': '脏缓存清洗',
                'effect': '自动清理低质量缓存',
                'prerequisites': ['result_cache'],
                'applicable_to': ['cache_health'],
                'source': '豆包建议P4',
                'status': 'active'
            },
            # CSI10优化类
            'model_cache': {
                'type': 'csi10',
                'name': '模型缓存',
                'effect': '-66.5% training (7.6s→2.6s)',
                'prerequisites': ['sklearn'],
                'applicable_to': ['stock_analysis'],
                'source': 'csi10优化',
                'status': 'active'
            },
            'feature_extension': {
                'type': 'csi10',
                'name': '特征扩展',
                'effect': '+140%维度 (5→12)',
                'prerequisites': ['model_cache'],
                'applicable_to': ['ml_features'],
                'source': 'csi10优化',
                'status': 'active'
            },
            'adaptive_threshold': {
                'type': 'csi10',
                'name': '自适应持仓管理',
                'effect': '动态阈值策略',
                'prerequisites': ['feature_extension'],
                'applicable_to': ['portfolio_management'],
                'source': 'csi10优化',
                'status': 'active'
            }
        },
        'edges': [
            {'from': 'embedding_cache', 'to': 'result_cache', 'relation': 'DEPENDS_ON', 'desc': '结果缓存依赖embedding缓存命中率'},
            {'from': 'result_cache', 'to': 'normalize_keywords', 'relation': 'ENHANCES', 'desc': '归一化提升缓存命中率'},
            {'from': 'result_cache', 'to': 'hot_cache', 'relation': 'ENHANCES', 'desc': '热数据分层提升稳定性'},
            {'from': 'result_cache', 'to': 'dirty_cache_cleanup', 'relation': 'MAINTAINS', 'desc': '脏数据清洗保障质量'},
            {'from': 'flow_templates', 'to': 'brain_patterns', 'relation': 'DEPENDS_ON', 'desc': 'patterns扩展基于templates'},
            {'from': 'brain_patterns', 'to': 'composite_patterns', 'relation': 'EXTENDS', 'desc': '复合关键词解决冲突'},
            {'from': 'flow_templates', 'to': 'exact_priority', 'relation': 'FIXES', 'desc': '精确匹配修复误判'},
            {'from': 'brain_patterns', 'to': 'pattern_auto_collect', 'relation': 'EVOLVES', 'desc': '自动沉淀进化'},
            {'from': 'model_cache', 'to': 'feature_extension', 'relation': 'DEPENDS_ON', 'desc': '特征扩展需要模型'},
            {'from': 'feature_extension', 'to': 'adaptive_threshold', 'relation': 'DEPENDS_ON', 'desc': '自适应策略基于特征'},
        ],
        'node_types': ['optimization', 'experiment', 'module', 'knowledge'],  # 豆包4类节点
        'categories': ['performance', 'accuracy', 'evolution', 'csi10'],
        'relations': ['DEPENDS_ON', 'ENHANCES', 'EXTENDS', 'FIXES', 'EVOLVES', 'MAINTAINS', 'ALTERNATIVE_TO', 'SUPERSEDED_BY', 'COOPERATE_WITH', 'DERIVED_FROM'],  # 豆包8种关系
        'lifecycle_states': ['VALID', 'OBSOLETE', 'DISCARDED', 'PENDING']  # 生命周期状态
    }
    
    # 尝试加载已有图谱
    if os.path.exists(KNOWLEDGE_GRAPH_FILE):
        try:
            with open(KNOWLEDGE_GRAPH_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                # 合并新方法
                for node_id, node_data in default_graph['nodes'].items():
                    if node_id not in loaded['nodes']:
                        loaded['nodes'][node_id] = node_data
                return loaded
        except Exception as e:
            logger.warning(f'Load knowledge graph error: {e}')
    
    return default_graph

KNOWLEDGE_GRAPH = init_knowledge_graph()

def query_knowledge_graph(method_id=None, category=None, applicable_to=None):
    """查询知识图谱"""
    results = {'nodes': [], 'edges': []}
    
    if method_id:
        # 查询特定方法
        if method_id in KNOWLEDGE_GRAPH['nodes']:
            results['nodes'].append({method_id: KNOWLEDGE_GRAPH['nodes'][method_id]})
            # 关联边
            for edge in KNOWLEDGE_GRAPH['edges']:
                if edge['from'] == method_id or edge['to'] == method_id:
                    results['edges'].append(edge)
    elif category:
        # 查询类别
        for node_id, node_data in KNOWLEDGE_GRAPH['nodes'].items():
            if node_data['type'] == category:
                results['nodes'].append({node_id: node_data})
    elif applicable_to:
        # 查询适用场景
        for node_id, node_data in KNOWLEDGE_GRAPH['nodes'].items():
            if applicable_to in node_data['applicable_to']:
                results['nodes'].append({node_id: node_data})
    else:
        # 返回全部
        results = KNOWLEDGE_GRAPH
    
    return results

def find_related_methods(method_id):
    """查找相关方法（依赖链+增强链）"""
    related = {'depends_on': [], 'enhances': [], 'alternatives': []}
    
    for edge in KNOWLEDGE_GRAPH['edges']:
        if edge['from'] == method_id:
            if edge['relation'] == 'DEPENDS_ON':
                related['depends_on'].append(edge['to'])
            elif edge['relation'] == 'ENHANCES':
                related['enhances'].append(edge['to'])
        if edge['to'] == method_id:
            if edge['relation'] == 'ALTERNATIVE_TO':
                related['alternatives'].append(edge['from'])
    
    return related

def add_knowledge_method(method_id, method_data, edges=None):
    """添加新方法到知识图谱"""
    KNOWLEDGE_GRAPH['nodes'][method_id] = method_data
    if edges:
        for edge in edges:
            KNOWLEDGE_GRAPH['edges'].append(edge)
    
    # 持久化
    try:
        with open(KNOWLEDGE_GRAPH_FILE, 'w', encoding='utf-8') as f:
            json.dump(KNOWLEDGE_GRAPH, f, ensure_ascii=False, indent=2)
        logger.info(f'Knowledge graph updated: {method_id}')
    except Exception as e:
        logger.warning(f'Save knowledge graph error: {e}')

def build_optimization_chain(target_problem):
    """构建优化链（从问题到方案）"""
    chain = []
    for node_id, node_data in KNOWLEDGE_GRAPH['nodes'].items():
        # 只处理有applicable_to的节点
        applicable = node_data.get('applicable_to', [])
        if applicable and target_problem in applicable:
            chain.append({
                'method': node_id,
                'name': node_data.get('name', node_id),
                'effect': node_data.get('effect', ''),
                'prerequisites': node_data.get('prerequisites', [])
            })
    
    # 按依赖排序（简化版，避免死循环）
    sorted_chain = []
    added = set()
    max_iterations = len(chain) * 2 + 10  # 防止死循环
    iterations = 0
    
    while len(sorted_chain) < len(chain) and iterations < max_iterations:
        iterations += 1
        for item in chain:
            if item['method'] in added:
                continue
            # 检查前置是否已添加（空前置直接添加）
            prereqs = item['prerequisites']
            prereqs_met = all(p in added or p not in KNOWLEDGE_GRAPH['nodes'] for p in prereqs)
            if prereqs_met or not prereqs:
                sorted_chain.append(item)
                added.add(item['method'])
    
    # 添加未排序的（循环依赖或缺失前置）
    for item in chain:
        if item['method'] not in added:
            sorted_chain.append(item)
    
    return sorted_chain

def save_knowledge_graph():
    """持久化知识图谱"""
    try:
        with open(KNOWLEDGE_GRAPH_FILE, 'w', encoding='utf-8') as f:
            json.dump(KNOWLEDGE_GRAPH, f, ensure_ascii=False, indent=2)
        logger.info('Knowledge graph saved')
        return True
    except Exception as e:
        logger.warning(f'Save knowledge graph error: {e}')
        return False

# ============================================================
# 豆包增强功能: 语义检索 + 方案推荐 + 冲突检测
# ============================================================
def semantic_search_methods(query_text, top_k=5):
    """豆包建议: 语义化检索优化方案"""
    results = []
    query_lower = query_text.lower()
    
    for node_id, node_data in KNOWLEDGE_GRAPH['nodes'].items():
        searchable = f"{node_data['name']} {node_data.get('effect', '')} {' '.join(node_data.get('applicable_to', []))} {node_data.get('source', '')}"
        if query_lower in searchable.lower() or query_lower in node_id.lower():
            results.append({
                'method': node_id,
                'name': node_data['name'],
                'type': node_data.get('type', 'optimization'),
                'lifecycle': node_data.get('lifecycle', 'VALID')
            })
    
    return {'query': query_text, 'results': results[:top_k], 'total': len(results)}

def scheme_recommendation(problem):
    """豆包建议: 方案推荐 + 权重决策"""
    chain = build_optimization_chain(problem)
    valid_chain = [item for item in chain if KNOWLEDGE_GRAPH['nodes'].get(item['method'], {}).get('lifecycle', 'VALID') == 'VALID']
    
    for item in valid_chain:
        node = KNOWLEDGE_GRAPH['nodes'].get(item['method'], {})
        weights = node.get('decision_weight', {})
        priority_score = {'P0': 100, 'P1': 80, 'P2': 60}.get(weights.get('priority', 'P2'), 60)
        cost_score = {'low': 30, 'medium': 15, 'high': 5}.get(weights.get('cost', 'low'), 30)
        benefit_score = {'high': 40, 'medium': 25, 'low': 10}.get(weights.get('benefit', 'low'), 10)
        risk_penalty = {'low': 0, 'medium': 10, 'high': 20}.get(weights.get('risk', 'low'), 0)
        item['recommendation_score'] = priority_score + cost_score + benefit_score - risk_penalty
    
    sorted_chain = sorted(valid_chain, key=lambda x: x.get('recommendation_score', 0), reverse=True)
    return {'problem': problem, 'recommended': sorted_chain, 'top_pick': sorted_chain[0] if sorted_chain else None}

def conflict_detect(method_ids):
    """豆包建议: 冲突方案检测"""
    conflicts = []
    for method_id in method_ids:
        node = KNOWLEDGE_GRAPH['nodes'].get(method_id, {})
        lifecycle = node.get('lifecycle', 'VALID')
        if lifecycle in ['OBSOLETE', 'DISCARDED']:
            conflicts.append({'method': method_id, 'issue': lifecycle})
    return {'conflicts': conflicts, 'safe': len(conflicts) == 0}

# ============================================================
# P7: 自动抽取引擎
# ============================================================

def experiment_parser(experiment_dir=None):
    """P7-1: 自动解析实验源码，提取方案与结论"""
    if experiment_dir is None:
        experiment_dir = os.path.join(BRAIN_CONFIG.get('brain_root', os.path.dirname(__file__)), 'autoresearch-brain-entry')
    
    if not os.path.exists(experiment_dir):
        return {'parsed': 0, 'experiments': [], 'error': 'directory not found'}
    
    experiments = []
    parsed_count = 0
    
    # 扫描所有experiment_*.py文件
    for filename in os.listdir(experiment_dir):
        if filename.startswith('experiment_') and filename.endswith('.py'):
            filepath = os.path.join(experiment_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取实验编号
                exp_id = filename.replace('experiment_', '').replace('.py', '')
                
                # 提取标题和目标
                title_match = re.search(r'""".*?AutoResearch.*?实验.*?[:：](.+?)"""', content, re.DOTALL)
                title = title_match.group(1).strip() if title_match else filename
                
                # 提取KEEP/DISCARD结论（如果有）
                conclusion = 'PENDING'
                if 'KEEP' in content or '结论: KEEP' in content:
                    conclusion = 'KEEP'
                elif 'DISCARD' in content or '结论: DISCARD' in content:
                    conclusion = 'DISCARD'
                elif '结论' in content:
                    conclusion_match = re.search(r'结论[:：]\s*(\w+)', content)
                    if conclusion_match:
                        conclusion = conclusion_match.group(1)
                
                # 提取关键改进指标
                metrics = {}
                # 匹配如 "-97%" "-99.2%" 等百分比改进
                percent_matches = re.findall(r'(-?\d+\.?\d*)%', content)
                if percent_matches:
                    metrics['improvements'] = percent_matches[:3]
                
                # 匹配时间改进 如 "146ms->0ms"
                time_match = re.search(r'(\d+)ms[→\->](\d+)ms', content)
                if time_match:
                    metrics['before_ms'] = int(time_match.group(1))
                    metrics['after_ms'] = int(time_match.group(2))
                
                # 添加到知识图谱
                exp_node_id = f'exp_{exp_id}'
                if exp_node_id not in KNOWLEDGE_GRAPH['nodes']:
                    KNOWLEDGE_GRAPH['nodes'][exp_node_id] = {
                        'type': 'experiment',
                        'name': title,
                        'exp_id': exp_id,
                        'conclusion': conclusion,
                        'metrics': metrics,
                        'derived_methods': [],
                        'lifecycle': 'VALID' if conclusion == 'KEEP' else ('DISCARDED' if conclusion == 'DISCARD' else 'PENDING'),
                        'file': filename
                    }
                
                experiments.append({
                    'id': exp_id,
                    'title': title,
                    'conclusion': conclusion,
                    'metrics': metrics,
                    'file': filename
                })
                parsed_count += 1
                
            except Exception as e:
                logger.warning(f'Parse experiment {filename} error: {e}')
    
    # 保存更新后的知识图谱
    save_knowledge_graph()
    
    return {
        'parsed': parsed_count,
        'experiments': experiments,
        'new_nodes': parsed_count
    }

def brain_rule_miner(patterns_file=None):
    """P7-2: 深度扫描brain_patterns库"""
    if patterns_file is None:
        patterns_file = BRAIN_CONFIG.get('patterns_file', os.path.join(BRAIN_CONFIG.get('data_dir', 'data'), '.brain_patterns.db'))
    
    mined_rules = []
    
    try:
        conn = sqlite3.connect(patterns_file)
        cursor = conn.cursor()
        
        # 查询所有pattern
        cursor.execute('SELECT keyword, intent, flow, priority, created_at FROM patterns ORDER BY priority DESC, created_at DESC')
        rows = cursor.fetchall()
        
        for row in rows:
            keyword, intent, flow, priority, created_at = row
            
            # 添加到知识图谱
            rule_id = f'rule_{keyword.replace(" ", "_")}'
            if rule_id not in KNOWLEDGE_GRAPH['nodes']:
                KNOWLEDGE_GRAPH['nodes'][rule_id] = {
                    'type': 'rule',
                    'name': f'规则: {keyword}',
                    'keyword': keyword,
                    'intent': intent,
                    'flow': flow,
                    'priority': priority,
                    'source': 'brain_patterns',
                    'lifecycle': 'VALID'
                }
            
            mined_rules.append({
                'keyword': keyword,
                'intent': intent,
                'flow': flow,
                'priority': priority
            })
        
        conn.close()
        
        # 保存知识图谱
        save_knowledge_graph()
        
        return {
            'mined': len(mined_rules),
            'rules': mined_rules[:20],  # 返回前20条
            'total': len(rows)
        }
        
    except Exception as e:
        logger.warning(f'Mine patterns error: {e}')
        return {'mined': 0, 'rules': [], 'error': str(e)}

# ============================================================
# P8: brain_hook - 与Gateway决策联动
# ============================================================

def brain_pre_decision_hook(user_query):
    """P8: 模型决策前自动调取知识图谱参考"""
    # 查询相关优化方案
    related = semantic_search_methods(user_query, top_k=3)
    
    # 查询相关规则
    matched_rules = []
    for node_id, node_data in KNOWLEDGE_GRAPH['nodes'].items():
        if node_data.get('type') == 'rule' and node_data.get('keyword'):
            if node_data['keyword'] in user_query.lower():
                matched_rules.append({
                    'keyword': node_data['keyword'],
                    'intent': node_data.get('intent'),
                    'flow': node_data.get('flow')
                })
    
    reference = {
        'query': user_query,
        'related_methods': related.get('results', []),
        'matched_rules': matched_rules[:5],
        'recommendation': None,
        'confidence': 0
    }
    
    top = related.get('results', [])
    if top:
        first = top[0]
        reference['recommendation'] = first
        reference['confidence'] = 1
    
    return reference

# ============================================================
# P9: autoresearch_hook - 新实验立项前检索
# ============================================================

def autoresearch_pre_check(proposed_experiment):
    """P9: New experiment pre-check"""
    similar = []
    for nid, ndata in KNOWLEDGE_GRAPH['nodes'].items():
        if ndata.get('type') == 'experiment':
            if proposed_experiment.lower() in ndata.get('name', '').lower():
                similar.append({'id': nid, 'name': ndata.get('name'), 'conclusion': ndata.get('conclusion', 'PENDING')})
    
    rec = 'PROCEED'
    reasons = []
    for exp in similar:
        if exp['conclusion'] == 'KEEP':
            rec = 'SKIP'
            reasons.append(f"Success: {exp['name']}")
        elif exp['conclusion'] == 'DISCARD':
            rec = 'AVOID'
            reasons.append(f"Failed: {exp['name']}")
    
    return {'proposed': proposed_experiment, 'similar': similar, 'recommendation': rec, 'reasons': reasons, 'safe': rec in ['PROCEED', 'REUSE']}

NORMALIZE_KEYWORDS = {
    # 测试类
    '测试': ['test', '检测', '验证', '试试', '测试一下', '帮我测试', '系统测试', '测试系统', '下系统', '测试下'],
    # 修复类
    '修复': ['fix', 'bug', '错误', '改正', '解决', '修复一下', '帮我修复', '修复'],
    # 检查类
    '检查': ['check', '查看', '诊断', 'inspect', '检查一下', '帮我检查', '看看'],
    # 部署类
    '部署': ['deploy', '发布', '上线', '部署一下', '帮我部署'],
    # 优化类
    '优化': ['optimize', '改进', '提升', '优化一下', '帮我优化'],
    # 调试类
    '调试': ['debug', '排查', '调试一下', '帮我调试'],
    # 分析类
    '分析': ['analyze', '分析一下', '帮我分析'],
    # 添加类
    '添加': ['add', '新增', '创建', '添加一个', '帮我添加'],
    # 更新类
    '更新': ['update', '刷新', '同步', '更新一下', '帮我更新'],
    # 重启类
    '重启': ['restart', '重新启动', '重启一下', '帮我重启'],
    # 清理类
    '清理': ['clean', '删除', 'remove', '清理一下', '帮我清理'],
}

# 目标词归一化映射
TARGET_NORMALIZE = {
    '系统': ['系统', 'system', 'sys'],
    'brain_entry': ['brain_entry', 'brainentry', 'brain-entry'],
    'gateway': ['gateway', 'gw'],
    'analyzer': ['analyzer', 'analyze'],
    'embedding': ['embedding', 'embed'],
    'memory': ['memory', 'mem'],
    'vector': ['vector', 'vec'],
}

def normalize_intent_key(text):
    """语义归一化V2 - 将不同话术收敛到同一缓存key"""
    text_lower = text.lower().strip()
    import re
    
    # 1. 意图关键词归一化
    intent_keywords = []
    for core_keyword, variants in NORMALIZE_KEYWORDS.items():
        for variant in variants:
            if variant.lower() in text_lower:
                intent_keywords.append(core_keyword)
                break
    
    # 2. 目标词归一化
    target_keywords = []
    for core_target, variants in TARGET_NORMALIZE.items():
        for variant in variants:
            if variant.lower() in text_lower:
                target_keywords.append(core_target)
                break
    
    # 3. 英文单词提取（补充）
    english_words = re.findall(r'[a-zA-Z_]+', text)
    for word in english_words:
        if word.lower() not in [v.lower() for vs in TARGET_NORMALIZE.values() for v in vs]:
            target_keywords.append(word)
    
    # 4. 合并排序生成key
    all_keywords = sorted(set(intent_keywords + target_keywords))
    
    if all_keywords:
        normalized_key = '|'.join(all_keywords)
    else:
        normalized_key = text_lower[:50]
    
    return hashlib.md5(normalized_key.encode('utf-8')).hexdigest()

# ============================================================
# Embedding Provider Manager V3 - 本地优先
# ============================================================
class EmbeddingProvider:
    """Embedding服务提供者管理 - FAISS本地优先"""
    
    PROVIDERS = ['local_sentence', 'openai', 'fallback']
    current_provider = None
    provider_status = {}
    local_model = None
    local_model_name = 'all-MiniLM-L6-v2'  # 使用本地已缓存模型
    local_model_path = Path.home() / '.cache' / 'huggingface' / 'hub' / 'models--sentence-transformers--all-MiniLM-L6-v2' / 'snapshots' / 'c9745ed1d9f207416be6d2e6f8de32d1f16199bf'
    
    @classmethod
    def initialize(cls):
        """初始化embedding providers - 本地优先"""
        logger.info("Initializing embedding providers (local-first)...")
        
        # 优先尝试本地Sentence-Transformers
        if cls._init_local_model():
            cls.current_provider = 'local_sentence'
            cls.provider_status['local_sentence'] = 'healthy'
            logger.info("Embedding: Local Sentence-Transformers available")
            save_provider_state('local_sentence', 'healthy')
            return 'local_sentence'
        
        # 备用：尝试OpenAI
        if cls._test_openai():
            cls.current_provider = 'openai'
            cls.provider_status['openai'] = 'healthy'
            logger.info("Embedding: OpenAI available (backup)")
            save_provider_state('openai', 'healthy')
            return 'openai'
        else:
            cls.provider_status['openai'] = 'unavailable'
            logger.warning("Embedding: OpenAI unavailable")
        
        # 最终降级到fallback
        cls.current_provider = 'fallback'
        cls.provider_status['fallback'] = 'healthy'
        logger.info("Embedding: Using fallback (MD5 hash)")
        save_provider_state('fallback', 'healthy')
        return 'fallback'
    
    @classmethod
    def _init_local_model(cls):
        """初始化本地Sentence-Transformers模型（支持BGE-M3）"""
        try:
            from sentence_transformers import SentenceTransformer
            from pathlib import Path
            import os
            
            logger.info(f"Loading embedding model...")
            
            # 优先使用BGE-M3（8192 tokens）- ModelScope路径
            bge_m3_path = Path('C:/Users/Administrator/.cache/modelscope/Xorbits/bge-m3')
            old_model_path = Path.home() / '.cache' / 'huggingface' / 'hub' / 'models--sentence-transformers--all-MiniLM-L6-v2' / 'snapshots' / 'c9745ed1d9f207416be6d2e6f8de32d1f16199bf'
            
            # 尝试加载BGE-M3（优先）
            if bge_m3_path.exists():
                try:
                    logger.info(f"Loading BGE-M3 from: {bge_m3_path}...")
                    cls.local_model = SentenceTransformer(str(bge_m3_path))
                    logger.info(f"BGE-M3 loaded! Max seq: {cls.local_model.max_seq_length}, Vector dim: {cls.local_model.get_sentence_embedding_dimension()}")
                    return True
                except Exception as e1:
                    logger.warning(f"BGE-M3 load failed: {e1}, trying fallback...")
            
            # 降级到旧模型all-MiniLM-L6-v2（512 tokens）
            if old_model_path.exists():
                logger.info(f"Loading fallback model from: {old_model_path}...")
                cls.local_model = SentenceTransformer(str(old_model_path))
                test_vec = cls.local_model.encode("test")
                logger.info(f"Fallback model loaded, vector dim: {len(test_vec)}")
                return True
            else:
                logger.warning(f"No local model found")
                return False
        except Exception as e:
            logger.warning(f"Local model init failed: {e}")
            return False
    
    @classmethod
    def _test_openai(cls):
        """测试OpenAI连接"""
        try:
            import requests
            api_key = os.environ.get('OPENAI_API_KEY', '')
            if not api_key:
                return False
            r = requests.post(
                f"{BRAIN_CONFIG['openai_api_base']}/embeddings",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"input": "test", "model": BRAIN_CONFIG['openai_model']},
                timeout=5
            )
            return r.status_code == 200
        except:
            return False
    
    @classmethod
    def get_embedding(cls, text):
        """获取embedding向量 - 本地优先"""
        if cls.current_provider is None:
            cls.initialize()
        
        for attempt in range(BRAIN_CONFIG['retry_attempts']):
            try:
                if cls.current_provider == 'local_sentence':
                    return cls._get_local_embedding(text)
                elif cls.current_provider == 'openai':
                    return cls._get_openai_embedding(text)
                else:
                    return cls._get_fallback_embedding(text)
            except Exception as e:
                logger.warning(f"Embedding attempt {attempt+1} failed: {e}")
                # 尝试切换provider
                if cls.current_provider == 'local_sentence' and cls._test_openai():
                    cls.current_provider = 'openai'
                    logger.info("Switched to OpenAI backup")
                elif cls.current_provider != 'fallback':
                    cls.current_provider = 'fallback'
                    logger.info("Switched to fallback")
                time.sleep(BRAIN_CONFIG['retry_delay'])
        
        return cls._get_fallback_embedding(text)
    
    @classmethod
    def _get_local_embedding(cls, text):
        """本地Sentence-Transformers embedding"""
        if cls.local_model is None:
            cls._init_local_model()
        if cls.local_model is None:
            raise Exception("Local model not available")
        vector = cls.local_model.encode(text)
        return [float(x) for x in vector]  # 转换numpy.float32为Python float
    
    @classmethod
    def _get_openai_embedding(cls, text):
        """OpenAI embedding"""
        import requests
        api_key = os.environ.get('OPENAI_API_KEY', '')
        r = requests.post(
            f"{BRAIN_CONFIG['openai_api_base']}/embeddings",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"input": text, "model": BRAIN_CONFIG['openai_model']},
            timeout=BRAIN_CONFIG['max_request_timeout']
        )
        if r.status_code == 200:
            return r.json()['data'][0]['embedding']
        raise Exception(f"OpenAI error: {r.status_code}")
    
    @classmethod
    def _get_fallback_embedding(cls, text):
        """Fallback: MD5哈希作为伪向量"""
        hash_hex = hashlib.md5(text.encode('utf-8')).hexdigest()
        vector = []
        for i in range(0, len(hash_hex), 2):
            val = int(hash_hex[i:i+2], 16) / 255.0
            vector.extend([val] * 12)
        return vector[:384]

# ============================================================
# 向量引擎 V2
# ============================================================
class VectorEngineV2:
    """增强版向量引擎"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()
        self.embedding_available = EmbeddingProvider.initialize()
        logger.info(f"Vector engine V2 initialized: {db_path}")
        logger.info(f"Embedding provider: {EmbeddingProvider.current_provider}")
    
    def _init_db(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT, embedding TEXT, source TEXT, metadata TEXT,
                created_at TEXT, updated_at TEXT)''')
            c.execute('CREATE INDEX IF NOT EXISTS idx_source ON embeddings(source)')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Vector DB init error: {e}")
    
    def _cosine_similarity(self, vec1, vec2):
        try:
            import math
            dot_product = sum(float(a) * float(b) for a, b in zip(vec1, vec2))
            norm1 = math.sqrt(sum(float(a) * float(a) for a in vec1))
            norm2 = math.sqrt(sum(float(b) * float(b) for b in vec2))
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return float(dot_product / (norm1 * norm2))
        except:
            return 0.0
    
    def search(self, query, limit=5):
        try:
            query_embedding = EmbeddingProvider.get_embedding(query)
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('SELECT content, embedding, source, metadata FROM embeddings')
            rows = c.fetchall()
            conn.close()
            
            results = []
            for content, embedding_str, source, metadata in rows:
                try:
                    stored_embedding = json.loads(embedding_str)
                    score = self._cosine_similarity(query_embedding, stored_embedding)
                    results.append({
                        'content': content, 'source': source,
                        'metadata': json.loads(metadata) if metadata else {},
                        'score': score
                    })
                except:
                    continue
            
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:limit]
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

# ============================================================
# 缓存管理
# ============================================================
class CacheManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()
        self._memory_cache = {}
    
    def _init_db(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY, value TEXT, created_at TEXT, expires_at TEXT)''')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Cache DB init error: {e}")
    
    def get(self, key):
        if key in self._memory_cache:
            cached = self._memory_cache[key]
            if datetime.now() < cached['expires_at']:
                return cached['value']
        return None
    
    def set(self, key, value, ttl=None):
        from datetime import timedelta
        ttl = ttl or BRAIN_CONFIG['cache_ttl']
        expires_at = datetime.now() + timedelta(seconds=ttl)
        self._memory_cache[key] = {'value': value, 'expires_at': expires_at}

# ============================================================
# 反馈学习管理
# ============================================================
class FeedbackManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT, intent TEXT, results_count INTEGER,
                user_action TEXT, confidence TEXT, timestamp TEXT)''')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Feedback DB init error: {e}")
    
    def record(self, query, intent, results_count, user_action, confidence):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''INSERT INTO feedback (query, intent, results_count, user_action, confidence, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (query, json.dumps(intent, ensure_ascii=False), results_count,
                 user_action, confidence, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Feedback record error: {e}")
    
    def get_stats(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM feedback')
            total = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM feedback WHERE user_action IN ('accept', 'confirm')")
            positive = c.fetchone()[0]
            c.execute('SELECT AVG(results_count) FROM feedback')
            avg_results = c.fetchone()[0] or 0
            conn.close()
            return {'total_feedback': total, 'positive_rate': positive / total if total > 0 else 0, 'avg_results': avg_results}
        except:
            return {'total_feedback': 0, 'positive_rate': 0, 'avg_results': 0}



# ============================================================
# 输入验证器 - 安全性加固
# ============================================================
class InputValidator:
    """输入验证：防止注入攻击和恶意输入"""
    
    @classmethod
    def validate(cls, content):
        """验证输入内容安全性"""
        if not content or len(content) > BRAIN_CONFIG['input_max_length']:
            return False, "输入长度超限"
        
        # 检查危险模式
        content_lower = content.lower()
        for pattern in BRAIN_CONFIG['input_dangerous_patterns']:
            if pattern.lower() in content_lower:
                logger.warning(f"Dangerous pattern detected: {pattern}")
                return False, f"危险输入检测: {pattern}"
        
        return True, "OK"
    
    @classmethod
    def sanitize(cls, content):
        """清理输入内容"""
        # 移除潜在的HTML标签
        content = re.sub(r'<[^>]+>', '', content)
        # 移除多余空格
        content = re.sub(r'\s+', ' ', content).strip()
        return content

# ============================================================
# 备份管理器 - 健壮性增强
# ============================================================
class BackupManager:
    """自动备份机制：保护重要数据和配置"""
    
    def __init__(self, backup_dir):
        self.backup_dir = backup_dir
        self._init_backup_dir()
        logger.info(f'BackupManager initialized: {backup_dir}')
    
    def _init_backup_dir(self):
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            # 创建日期子目录
            today = datetime.now().strftime('%Y-%m-%d')
            today_dir = os.path.join(self.backup_dir, today)
            os.makedirs(today_dir, exist_ok=True)
        except Exception as e:
            logger.error(f'Backup dir init error: {e}')
    
    def backup_file(self, file_path, reason='auto'):
        """备份单个文件"""
        try:
            if not os.path.exists(file_path):
                return None
            
            # 生成备份文件名
            basename = os.path.basename(file_path)
            timestamp = datetime.now().strftime('%H%M%S')
            backup_name = f"{basename}.{reason}.{timestamp}.bak"
            
            # 目标路径
            today = datetime.now().strftime('%Y-%m-%d')
            backup_path = os.path.join(self.backup_dir, today, backup_name)
            
            # 执行备份
            import shutil
            shutil.copy2(file_path, backup_path)
            logger.info(f'Backup created: {backup_path}')
            return backup_path
        except Exception as e:
            logger.error(f'Backup failed: {e}')
            return None
    
    def backup_critical_files(self):
        """备份关键文件"""
        critical_files = [
            'C:/Users/Administrator/.openclaw/workspace-工程师/brain_entry.py',
            'C:/Users/Administrator/.openclaw/workspace-工程师/SOUL.md',
            'C:/Users/Administrator/.openclaw/workspace-工程师/.brain_vectors.db',
            'C:/Users/Administrator/.openclaw/workspace-工程师/.brain_patterns.db',
        ]
        results = []
        for f in critical_files:
            if os.path.exists(f):
                result = self.backup_file(f, 'scheduled')
                results.append(result)
        return results
    
    def restore_file(self, backup_path, target_path):
        """从备份恢复文件"""
        try:
            import shutil
            shutil.copy2(backup_path, target_path)
            logger.info(f'Restored: {backup_path} -> {target_path}')
            return True
        except Exception as e:
            logger.error(f'Restore failed: {e}')
            return False

# ============================================================
# 事务管理器 - 健壮性增强
# ============================================================
class TransactionManager:
    """事务回滚机制：确保操作一致性"""
    
    def __init__(self):
        self.transactions = {}  # 事务ID -> 操作列表
        self.current_transaction = None
        logger.info('TransactionManager initialized')
    
    def begin(self, transaction_id):
        """开始事务"""
        self.transactions[transaction_id] = {
            'operations': [],
            'status': 'active',
            'start_time': datetime.now()
        }
        self.current_transaction = transaction_id
        return transaction_id
    
    def log_operation(self, operation_type, target, before_state, after_state):
        """记录操作（用于回滚）"""
        if not self.current_transaction:
            return
        
        self.transactions[self.current_transaction]['operations'].append({
            'type': operation_type,
            'target': target,
            'before': before_state,
            'after': after_state,
            'timestamp': datetime.now()
        })
    
    def commit(self, transaction_id):
        """提交事务"""
        if transaction_id in self.transactions:
            self.transactions[transaction_id]['status'] = 'committed'
            self.current_transaction = None
            return True
        return False
    
    def rollback(self, transaction_id):
        """回滚事务"""
        if transaction_id not in self.transactions:
            return False
        
        transaction = self.transactions[transaction_id]
        operations = transaction['operations']
        
        # 逆序执行回滚
        for op in reversed(operations):
            try:
                if op['type'] == 'file_modify':
                    # 恢复文件状态
                    with open(op['target'], 'w', encoding='utf-8') as f:
                        f.write(op['before'])
                    logger.info(f"Rolled back: {op['target']}")
                elif op['type'] == 'db_update':
                    # 恢复数据库状态
                    # 这里需要根据具体数据库操作实现
                    logger.info(f"Rolled back DB: {op['target']}")
            except Exception as e:
                logger.error(f"Rollback failed for {op['target']}: {e}")
        
        transaction['status'] = 'rolled_back'
        self.current_transaction = None
        return True
    
    def clear_old_transactions(self, max_age_hours=24):
        """清理旧事务记录"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        to_remove = []
        for tid, t in self.transactions.items():
            if t['start_time'] < cutoff and t['status'] != 'active':
                to_remove.append(tid)
        for tid in to_remove:
            del self.transactions[tid]
        return len(to_remove)

# ============================================================
# Self-Improving Manager (借鉴ClawHub Self-Improving-Agent)
# ============================================================
class SelfImprovingManager:
    """自进化管理器：检测触发器 + Pattern-Key + 自动晋升"""
    
    CORRECTION_PATTERNS = [
        r'No,.*wrong', r'Actually', r"That's not",
        r'应该是', r'不是这样', r'错了', r'不对',
        r'你理解错了', r'换个方式', r'重做'
    ]
    
    FEATURE_PATTERNS = [
        r'Can you also', r'I wish', r'Could you add',
        r'希望能', r'增加一个', r'缺少'
    ]
    
    def __init__(self, learnings_dir, pattern_db):
        self.learnings_dir = learnings_dir
        self.pattern_db = pattern_db
        self._init_dirs()
        self._init_pattern_db()
        logger.info('SelfImprovingManager initialized')
    
    def _init_dirs(self):
        try:
            os.makedirs(self.learnings_dir, exist_ok=True)
        except Exception as e:
            logger.error(f'Learnings dir init error: {e}')
    
    def _init_pattern_db(self):
        try:
            conn = sqlite3.connect(self.pattern_db)
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS patterns (pattern_key TEXT UNIQUE, count INTEGER, first_seen TEXT, last_seen TEXT, status TEXT)')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f'Pattern DB init error: {e}')
    
    def detect_trigger(self, content):
        """检测触发器"""
        import re
        for pattern in self.CORRECTION_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return {'type': 'correction', 'trigger': pattern}
        for pattern in self.FEATURE_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return {'type': 'feature_request', 'trigger': pattern}
        return None
    
    def log_learning(self, category, summary, pattern_key=None):
        """记录学习"""
        try:
            timestamp = datetime.now().isoformat()
            id_str = f'LRN-{datetime.now().strftime("%Y%m%d")}-{hashlib.md5(summary.encode()).hexdigest()[:3]}'
            entry = f'\n## [{id_str}] {category}\nLogged: {timestamp}\nSummary: {summary}\nPattern-Key: {pattern_key or "none"}\n---\n'
            with open(os.path.join(self.learnings_dir, 'LEARNINGS.md'), 'a', encoding='utf-8') as f:
                f.write(entry)
            if pattern_key:
                self._update_pattern_count(pattern_key)
            return id_str
        except Exception as e:
            logger.error(f'Log learning error: {e}')
            return None
    
    def _update_pattern_count(self, pattern_key):
        """更新Pattern计数"""
        try:
            conn = sqlite3.connect(self.pattern_db)
            c = conn.cursor()
            now = datetime.now().isoformat()
            c.execute('SELECT count FROM patterns WHERE pattern_key = ?', (pattern_key,))
            row = c.fetchone()
            if row:
                new_count = row[0] + 1
                c.execute('UPDATE patterns SET count = ?, last_seen = ? WHERE pattern_key = ?', (new_count, now, pattern_key))
                if new_count >= BRAIN_CONFIG['promotion_threshold']:
                    logger.info(f'Pattern ready for promotion: {pattern_key} (count={new_count})')
            else:
                c.execute('INSERT INTO patterns VALUES (?, 1, ?, ?, "pending")', (pattern_key, now, now))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f'Pattern count error: {e}')
    
    def get_pattern_stats(self):
        """获取Pattern统计"""
        try:
            conn = sqlite3.connect(self.pattern_db)
            c = conn.cursor()
            c.execute('SELECT pattern_key, count, status FROM patterns ORDER BY count DESC LIMIT 10')
            return [{'pattern': r[0], 'count': r[1], 'status': r[2]} for r in c.fetchall()]
        except:
            return []
    
    # ============================================================
    # P1: Pattern自动沉淀（豆包建议）
    # ============================================================
    def auto_collect_patterns(self):
        """从feedback自动收集高频意图词"""
        try:
            feedback_file = BRAIN_CONFIG['data_dir'] + '/daily_feedback_report.json'
            if not os.path.exists(feedback_file):
                return []
            
            with open(feedback_file, 'r', encoding='utf-8') as f:
                feedback_data = json.load(f)
            
            # 统计意图词频率
            intent_freq = {}
            for record in feedback_data.get('records', []):
                content = record.get('content', '')
                intent_type = record.get('intent_type', '')
                if intent_type and intent_type.startswith('flow_'):
                    # 提取关键词
                    keywords = self._extract_keywords(content)
                    for kw in keywords:
                        key = f'{intent_type}:{kw}'
                        intent_freq[key] = intent_freq.get(key, 0) + 1
            
            # 高频词自动沉淀
            new_patterns = []
            for key, count in intent_freq.items():
                if count >= 3:  # 出现3次以上
                    intent_type, keyword = key.split(':', 1)
                    if not self._is_existing_pattern(keyword):
                        new_patterns.append({'keyword': keyword, 'intent': intent_type, 'count': count})
                        self._add_to_pattern_db(keyword, intent_type, count)
            
            return new_patterns
        except Exception as e:
            logger.warning(f'Auto collect patterns error: {e}')
            return []
    
    def _extract_keywords(self, text):
        """提取关键词"""
        import re
        # 英文单词
        english_words = re.findall(r'[a-zA-Z_]+', text)
        # 中文字符串（2字以上）
        chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,}', text)
        return list(set(english_words + chinese_words))
    
    def _is_existing_pattern(self, keyword):
        """检查是否已存在pattern"""
        try:
            conn = sqlite3.connect(self.pattern_db)
            c = conn.cursor()
            c.execute('SELECT 1 FROM patterns WHERE pattern_key = ?', (keyword,))
            return c.fetchone() is not None
        except:
            return False
    
    def _add_to_pattern_db(self, keyword, intent_type, count):
        """添加到pattern数据库"""
        try:
            conn = sqlite3.connect(self.pattern_db)
            c = conn.cursor()
            now = datetime.now().isoformat()
            c.execute('INSERT OR REPLACE INTO patterns VALUES (?, ?, ?, ?, ?)', 
                     (keyword, count, now, now, f'auto:{intent_type}'))
            conn.commit()
            conn.close()
            logger.info(f'Auto pattern added: {keyword} -> {intent_type} (count={count})')
        except Exception as e:
            logger.warning(f'Add pattern error: {e}')
    
    def promote_patterns_to_brain(self, threshold=5):
        """晋升高频pattern到brain_patterns"""
        try:
            conn = sqlite3.connect(self.pattern_db)
            c = conn.cursor()
            c.execute('SELECT pattern_key, count, status FROM patterns WHERE count >= ? AND status LIKE "auto:%"', (threshold,))
            candidates = c.fetchall()
            
            promoted = []
            for pattern_key, count, status in candidates:
                intent_type = status.split(':', 1)[1] if ':' in status else 'unknown'
                # 更新状态
                c.execute('UPDATE patterns SET status = "promoted" WHERE pattern_key = ?', (pattern_key,))
                promoted.append({'keyword': pattern_key, 'intent': intent_type, 'count': count})
                logger.info(f'Pattern promoted: {pattern_key} (count={count})')
            
            conn.commit()
            conn.close()
            return promoted
        except Exception as e:
            logger.warning(f'Promote patterns error: {e}')
            return []
    
    # ============================================================
    # P2: 执行质量打分（豆包建议）
    # ============================================================
    QUALITY_METRICS = {
        'accuracy': {'weight': 0.4, 'threshold': 0.8},
        'response_time': {'weight': 0.2, 'threshold': 200},  # ms
        'error_count': {'weight': 0.2, 'threshold': 0},
        'user_correction': {'weight': 0.2, 'threshold': 0},
    }
    
    def score_task_quality(self, task_result):
        """任务质量自动打分"""
        try:
            scores = {}
            total_score = 0
            
            # 准确率评分
            intent_match = task_result.get('intent_match', True)
            accuracy_score = 1.0 if intent_match else 0.5
            scores['accuracy'] = accuracy_score * self.QUALITY_METRICS['accuracy']['weight']
            
            # 响应时间评分
            response_time = task_result.get('response_time', 100)
            if response_time < 50:  # 极快
                time_score = 1.0
            elif response_time < 100:  # 快
                time_score = 0.8
            elif response_time < 200:  # 正常
                time_score = 0.6
            else:  # 慢
                time_score = 0.3
            scores['response_time'] = time_score * self.QUALITY_METRICS['response_time']['weight']
            
            # 错误评分
            error_count = task_result.get('error_count', 0)
            error_score = 1.0 if error_count == 0 else max(0, 1 - error_count * 0.2)
            scores['error_count'] = error_score * self.QUALITY_METRICS['error_count']['weight']
            
            # 用户修正评分
            user_correction = task_result.get('user_correction', False)
            correction_score = 1.0 if not user_correction else 0.4
            scores['user_correction'] = correction_score * self.QUALITY_METRICS['user_correction']['weight']
            
            total_score = sum(scores.values())
            
            # 低分任务自动记录
            if total_score < 0.6:
                self._log_low_score_task(task_result, total_score, scores)
            
            return {'total': total_score, 'details': scores, 'grade': self._get_grade(total_score)}
        except Exception as e:
            logger.warning(f'Score task error: {e}')
            return {'total': 0.5, 'details': {}, 'grade': 'C'}
    
    def _get_grade(self, score):
        """评分等级"""
        if score >= 0.9: return 'A+'
        elif score >= 0.8: return 'A'
        elif score >= 0.7: return 'B'
        elif score >= 0.6: return 'C'
        else: return 'D'
    
    def _log_low_score_task(self, task_result, total_score, details):
        """记录低分任务，触发优化"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'score': total_score,
                'details': details,
                'content': task_result.get('content', ''),
                'intent': task_result.get('intent_type', ''),
                'suggestions': self._generate_optimization_suggestions(details)
            }
            
            # 写入优化日志
            with open(os.path.join(self.learnings_dir, 'LOW_SCORE_TASKS.json'), 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
            logger.info(f'Low score task logged: {total_score:.2f} - suggestions generated')
        except Exception as e:
            logger.warning(f'Log low score error: {e}')
    
    def _generate_optimization_suggestions(self, details):
        """生成优化建议"""
        suggestions = []
        for metric, score in details.items():
            if score < 0.5:
                if metric == 'accuracy':
                    suggestions.append('扩展关键词覆盖或优化意图匹配逻辑')
                elif metric == 'response_time':
                    suggestions.append('启用缓存预热或减少不必要的embedding调用')
                elif metric == 'error_count':
                    suggestions.append('检查输入验证或增加异常处理')
                elif metric == 'user_correction':
                    suggestions.append('优化输出格式或增强上下文理解')
        return suggestions

try:
    self_improving_manager = SelfImprovingManager(BRAIN_CONFIG['learnings_dir'], BRAIN_CONFIG['pattern_db'])
    logger.info('SelfImprovingManager component ready')
except Exception as e:
    logger.warning(f'SelfImprovingManager failed: {e}')
    self_improving_manager = None


# ============================================================
# Provider状态存储（解决Waitress多进程问题）
# ============================================================
PROVIDER_STATE_FILE = "C:/Users/Administrator/.openclaw/workspace-工程师/.embedding_provider.json"

def save_provider_state(provider, status):
    try:
        with open(PROVIDER_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'provider': provider, 'status': status}, f)
    except Exception as e:
        logger.error(f"Failed to save provider state: {e}")

def load_provider_state():
    try:
        state_file = os.path.abspath(PROVIDER_STATE_FILE)
        if os.path.exists(state_file):
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                provider = data.get('provider')
                status = data.get('status')
                if provider:
                    return provider, status
    except Exception as e:
        logger.error(f"Failed to load provider state: {e}")
    return 'fallback', {'fallback': 'healthy'}

# ============================================================
# 心跳监控
# ============================================================
heartbeat_running = True
last_heartbeat = datetime.now()

def heartbeat_monitor():
    global heartbeat_running, last_heartbeat
    while heartbeat_running:
        try:
            last_heartbeat = datetime.now()
            time.sleep(BRAIN_CONFIG['heartbeat_interval'])
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            time.sleep(5)

# ============================================================
# 全局组件初始化
# ============================================================
try:
    vector_engine = VectorEngineV2(BRAIN_CONFIG["memory_db"])
    save_provider_state(EmbeddingProvider.current_provider, EmbeddingProvider.provider_status)
    logger.info(f"Provider state saved: {EmbeddingProvider.current_provider}")
except Exception as e:
    logger.critical(f"Vector engine failed: {e}")
    vector_engine = None
    save_provider_state('fallback', {'fallback': 'healthy'})

try:
    cache_manager = CacheManager(BRAIN_CONFIG["cache_db"])
except Exception as e:
    logger.warning(f"Cache manager failed: {e}")
    cache_manager = None

try:
    feedback_manager = FeedbackManager(BRAIN_CONFIG["feedback_db"])
except Exception as e:
    logger.warning(f"Feedback manager failed: {e}")
    feedback_manager = None

# 新增组件：安全性和健壮性
backup_manager = None
transaction_manager = None

if BRAIN_CONFIG['backup_enabled']:
    try:
        backup_manager = BackupManager(BRAIN_CONFIG['backup_dir'])
        backup_manager.backup_critical_files()
    except Exception as e:
        logger.warning(f"Backup manager failed: {e}")
        backup_manager = None

if BRAIN_CONFIG['rollback_enabled']:
    try:
        transaction_manager = TransactionManager()
    except Exception as e:
        logger.warning(f"Transaction manager failed: {e}")
        transaction_manager = None

heartbeat_thread = threading.Thread(target=heartbeat_monitor, daemon=True)
heartbeat_thread.start()
logger.info("Heartbeat monitor started")

# ============================================================
# Memory搜索
# ============================================================
def search_memory(query, limit=5):
    cache_key = f"search:{hashlib.md5(query.encode()).hexdigest()}"
    if cache_manager:
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
    
    results = []
    if vector_engine:
        try:
            vec_results = vector_engine.search(query, limit)
            results.extend(vec_results)
        except Exception as e:
            logger.warning(f"Vector search failed: {e}")
    
    knowledge_dir = BRAIN_CONFIG["knowledge_dir"]
    if os.path.exists(knowledge_dir):
        try:
            for filename in os.listdir(knowledge_dir):
                if filename.endswith('.md'):
                    filepath = os.path.join(knowledge_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if query.lower() in content.lower():
                                results.append({
                                    'content': content[:500],
                                    'source': f'knowledge/{filename}',
                                    'metadata': {'type': 'knowledge'},
                                    'score': 0.65
                                })
                    except:
                        pass
        except Exception as e:
            logger.warning(f"Knowledge search failed: {e}")
    
    seen = set()
    unique_results = []
    for r in results:
        key = r['content'][:100]
        if key not in seen:
            seen.add(key)
            unique_results.append(r)
    
    # 深度转换所有numpy类型
    import numpy as np
    def convert_result(res):
        new_res = {}
        for k, v in res.items():
            if isinstance(v, np.floating):
                new_res[k] = float(v)
            elif isinstance(v, dict):
                new_res[k] = {kk: float(vv) if isinstance(vv, np.floating) else vv for kk, vv in v.items()}
            else:
                new_res[k] = v
        return new_res
    
    unique_results = [convert_result(r) for r in unique_results]
    unique_results.sort(key=lambda x: x['score'], reverse=True)
    return unique_results[:limit]

# ============================================================
# 意图分析
# ============================================================
# 流程模板关键词映射
FLOW_TEMPLATES = {
    'test': ['测试', 'test', '检测'],  # 移除'验证'避免重叠
    'fix': ['修复', 'fix', 'bug', '改正', '解决'],
    'check': ['检查', 'check', '查看', '诊断', 'inspect'],
    'deploy': ['部署', 'deploy', '发布', '上线'],
    'restart': ['重启', 'restart', '重新启动'],
    'clean': ['清理', 'clean', '删除', 'remove', '整理'],
    'optimize': ['优化', 'optimize', '改进', '提升', '效率', '减少', '增加', 'overnight', 'latency', '延迟'],
    'debug': ['调试', 'debug', '排查'],  # debug关键词优先
    'add': ['添加', 'add', '新增', '创建', '增加'],
    'update': ['更新', 'update', '刷新'],  # 移除'同步'避免与sync重叠
    # AutoResearch优化: 新增意图类型
    'analyze': ['分析', 'analyze', '统计', '趋势', '瓶颈'],
    'import': ['导入', 'import', '载入', '加载'],
    'export': ['导出', 'export', '输出', '保存'],
    'sync': ['同步', 'sync', '对齐', '一致性'],
    'verify': ['验证', 'verify', '确认', '完整性'],  # 验证单独处理
}

def analyze_intent(content):
    try:
        content_lower = content.lower().strip()
        
        # 优先检查流程模板匹配
        flow_type = detect_flow_template(content_lower)
        if flow_type:
            return {
                'need_brain': True, 
                'reason': f'flow_template: {flow_type}', 
                'priority': 'high', 
                'type': f'flow_{flow_type}', 
                'confidence': 0.9,
                'flow_template': f'flow_template_{flow_type}.md'
            }
        
        # AutoResearch优化: 扩展brain_patterns技术关键词
        brain_patterns = [r'brain', r'大脑', r'智能决策', r'搜索.*知识', r'你记得',
                          r'AutoResearch', r'autoresearch', r'NVIDIA', r'nvidia', r'fallback',
                          r'BGE', r'bge', r'embedding', r'向量', r'知识库', r'memory',
                          r'flow', r'template', r'pattern', r'feedback', r'索引',
                          r'数据库', r'api', r'配置', r'模型', r'FAISS',
                          r'意图', r'算法', r'系统.*设计', r'Wiki', r'wiki', r'synthesis',
                          r'自进化', r'进化', r'机制']
        for pattern in brain_patterns:
            if re.search(pattern, content_lower):
                return {'need_brain': True, 'reason': f'matched: {pattern}', 'priority': 'high', 'type': 'brain_command', 'confidence': 0.8}
        
        medium_patterns = [r'怎么', r'如何', r'帮我', r'创建', r'修改']
        for pattern in medium_patterns:
            if re.search(pattern, content_lower):
                return {'need_brain': True, 'reason': f'matched: {pattern}', 'priority': 'medium', 'type': 'action', 'confidence': 0.6}
        
        return {'need_brain': True, 'reason': 'default', 'priority': 'default', 'type': 'general', 'confidence': 0.5}
    except Exception as e:
        logger.error(f"Intent analysis error: {e}")
        return {'need_brain': True, 'reason': 'error fallback', 'priority': 'default', 'type': 'unknown', 'confidence': 0.3}

def detect_flow_template(content):
    """检测流程模板关键词 - 精确匹配优先 + 复合关键词"""
    # AutoResearch优化: 复合关键词优先匹配（解决关键词重叠）
    COMPOSITE_PATTERNS = {
        'test': [r'验证.*配置', r'验证.*分类', r'验证.*机制', r'验证.*设置'],
        'add': [r'添加.*检测', r'添加.*pattern', r'新增.*检测'],
        'deploy': [r'部署.*升级', r'部署.*检测', r'发布.*升级'],
        'optimize': [r'提升.*效率', r'提升.*性能', r'改进.*效率'],
        'export': [r'导出.*分析', r'导出.*报告', r'输出.*报告'],
    }
    
    # 复合关键词优先匹配
    for flow_type, patterns in COMPOSITE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content):
                return flow_type
    
    # AutoResearch优化: 精确关键词优先匹配
    # 避免'debug'被'fix'的'解决'覆盖
    EXACT_PRIORITY = {
        'debug': 'debug',
        'verify': 'verify',
        'test': 'test',
        'fix': 'fix',
        'check': 'check',
        'deploy': 'deploy',
        'restart': 'restart',
        'clean': 'clean',
        'optimize': 'optimize',
        'analyze': 'analyze',
        'import': 'import',
        'export': 'export',
        'sync': 'sync',
        # 中文关键词精确匹配
        '验证': 'verify',
        '调试': 'debug',
        '测试': 'test',
        '修复': 'fix',
        '检查': 'check',
    }
    
    # 精确匹配优先
    for exact_kw, flow_type in EXACT_PRIORITY.items():
        if exact_kw in content:
            return flow_type
    
    # 中文关键词匹配
    for flow_type, keywords in FLOW_TEMPLATES.items():
        for kw in keywords:
            if kw in content:
                return flow_type
    return None

# ============================================================
# 上下文构建 - 精简版（方案A）+ 流程模板注入
# ============================================================
def build_context(content, brain_results, intent):
    """精简版上下文：只显示关键信息 + 流程模板注入"""
    # 强制转换confidence为Python float
    import numpy as np
    confidence = float(intent.get('confidence', 0.5)) if isinstance(intent.get('confidence', 0.5), np.floating) else intent.get('confidence', 0.5)
    provider, _ = load_provider_state()
    priority = intent.get('priority', 'default')
    intent_type = intent.get('type', 'general')
    flow_template = intent.get('flow_template')
    
    # 精简格式：一行显示关键信息
    summary = f"[Brain] results={len(brain_results)}, confidence={confidence:.2f}, type={intent_type}, provider={provider}"
    
    # 流程模板注入
    flow_content = ""
    if flow_template:
        template_path = os.path.join(BRAIN_CONFIG['knowledge_dir'], flow_template)
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    flow_content = f.read()
                logger.info(f"Injected flow template: {flow_template}")
            except Exception as e:
                logger.error(f"Failed to read template: {e}")
    
    # 简短提示
    notes = ""
    if confidence < 0.5:
        notes = " (低置信度，建议请示用户)"
    if intent_type == 'system':
        notes = " (P3任务，必须请示)"
    
    # 如果有流程模板，返回模板内容
    if flow_content:
        return summary + notes + "\n\n## 流程模板\n" + flow_content[:500]  # 限制500字符
    
    return summary + notes

# ============================================================
# API端点
# ============================================================
@app.route('/entry', methods=['POST'])
def brain_entry():
    global last_heartbeat, RESULT_CACHE_HITS
    last_heartbeat = datetime.now()
    
    try:
        data = request.get_json() or {}
        
        # AutoResearch优化: 检查结果缓存（语义归一化版）
        original_content = str(data.get('content', ''))
        user_action = str(data.get('userAction', 'query'))
        
        # 语义归一化缓存key
        normalized_key = normalize_intent_key(original_content)
        action_key = hashlib.md5(user_action.encode('utf-8')).hexdigest()
        result_cache_key = normalized_key + '_' + action_key
        
        if result_cache_key in RESULT_CACHE:
            cached_response, cached_time = RESULT_CACHE[result_cache_key]
            if (datetime.now() - cached_time).total_seconds() < RESULT_CACHE_TTL:
                RESULT_CACHE_HITS += 1
                logger.info(f"Result cache hit: {RESULT_CACHE_HITS}")
                return cached_response
        
        content = data.get('content', '')
        session_key = data.get('sessionKey', 'unknown')
        sender_id = data.get('senderId', 'unknown')
        # user_action已在上文定义
        priority_level = data.get('priority', 'normal')  # 分级超时
        
        # 输入验证（安全性加固）
        is_valid, msg = InputValidator.validate(content)
        if not is_valid:
            logger.warning(f"Input validation failed: {msg}")
            return jsonify({
                'error': 'invalid_input',
                'message': msg,
                'brain_context': {'provider': 'none', 'results': []}
            }), 400
        
        # 清理输入
        content = InputValidator.sanitize(content)
        
        logger.info(f"Entry request: {content[:50]}...")
        
        # 分级超时设置
        timeout = BRAIN_CONFIG['timeout_levels'].get(priority_level, 10)
        
        # Self-Improving触发器检测
        trigger_detected = None
        if self_improving_manager:
            trigger_detected = self_improving_manager.detect_trigger(content)
            if trigger_detected:
                logger.info(f"Trigger detected: {trigger_detected}")
        
        intent = analyze_intent(content)
        
        brain_results = []
        if intent['need_brain']:
            try:
                future = executor.submit(search_memory, content, BRAIN_CONFIG['max_results'])
                brain_results = future.result(timeout=BRAIN_CONFIG['max_request_timeout'])
            except FuturesTimeoutError:
                logger.warning("Search timeout")
                brain_results = []
            except Exception as e:
                logger.error(f"Search error: {e}")
                brain_results = []
        
        processed_content = build_context(content, brain_results, intent)
        
        if feedback_manager:
            feedback_manager.record(content, intent, len(brain_results), user_action, str(intent.get('confidence', 0.5)))
        
        provider, _ = load_provider_state()
        logger.info(f"Entry success: {intent['priority']}, {len(brain_results)} results")
        
        # AutoResearch优化: 保存结果缓存
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
        return response_json
    except Exception as e:
        import traceback
        logger.error(f"Entry error: {e}\n{traceback.format_exc()}")
        return np_jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc(), 'processed_content': content, 'fallback': True})

@app.route('/test_json', methods=['GET'])
def test_json():
    import numpy as np
    return np_jsonify({'test': np.float32(0.5)})

@app.route('/health', methods=['GET'])
def health():
    heartbeat_elapsed = (datetime.now() - last_heartbeat).total_seconds()
    provider, status = load_provider_state()
    
    components = {
        'vector_engine': vector_engine is not None,
        'cache_manager': cache_manager is not None,
        'feedback_manager': feedback_manager is not None,
        'backup_manager': backup_manager is not None,
        'transaction_manager': transaction_manager is not None,
        'embedding_provider': provider,
        'embedding_status': status,
        'input_validator': InputValidator is not None
    }
    
    feedback_stats = feedback_manager.get_stats() if feedback_manager else {}
    all_healthy = all([heartbeat_elapsed < 60, vector_engine is not None])
    
    return jsonify({
        'status': 'healthy' if all_healthy else 'warning',
        'service': 'Brain Entry V3.0 - Local Vector + Enhanced Security',
        'timestamp': datetime.now().isoformat(),
        'heartbeat_elapsed': heartbeat_elapsed,
        'components': components,
        'feedback_stats': feedback_stats,
        'config': {'port': BRAIN_CONFIG['brain_port'], 'thread_pool': BRAIN_CONFIG['thread_pool']}
    })

@app.route('/embedding/status', methods=['GET'])
def embedding_status():
    provider, status = load_provider_state()
    return jsonify({'current_provider': provider, 'provider_status': status, 'available_providers': EmbeddingProvider.PROVIDERS})

@app.route('/feedback/stats', methods=['GET'])
def feedback_stats():
    if feedback_manager:
        return jsonify(feedback_manager.get_stats())
    return jsonify({'error': 'feedback manager not available'})

@app.route('/patterns/stats', methods=['GET'])
def pattern_stats():
    """Pattern-Key统计接口"""
    if self_improving_manager:
        return jsonify({
            'patterns': self_improving_manager.get_pattern_stats(),
            'promotion_threshold': BRAIN_CONFIG['promotion_threshold'],
            'learnings_dir': BRAIN_CONFIG['learnings_dir']
        })
    return jsonify({'error': 'self improving manager not available'})

# ============================================================
# P1-P5优化端点（豆包建议集成）
# ============================================================
@app.route('/optimize/patterns/auto', methods=['POST'])
def trigger_auto_patterns():
    """P1: Pattern自动沉淀"""
    if self_improving_manager:
        new_patterns = self_improving_manager.auto_collect_patterns()
        return jsonify({'status': 'success', 'new_patterns': new_patterns, 'count': len(new_patterns)})
    return jsonify({'error': 'manager not available'})

@app.route('/optimize/patterns/promote', methods=['POST'])
def promote_patterns():
    """P1: Pattern晋升"""
    if self_improving_manager:
        threshold = request.json.get('threshold', 5) if request.is_json else 5
        promoted = self_improving_manager.promote_patterns_to_brain(threshold)
        return jsonify({'status': 'success', 'promoted': promoted, 'count': len(promoted)})
    return jsonify({'error': 'manager not available'})

@app.route('/optimize/quality/score', methods=['POST'])
def score_quality():
    """P2: 任务质量打分"""
    if self_improving_manager:
        task_result = request.json if request.is_json else {}
        score_result = self_improving_manager.score_task_quality(task_result)
        return jsonify(score_result)
    return jsonify({'error': 'manager not available'})

@app.route('/optimize/cache/health', methods=['GET'])
def cache_health():
    """P4: 缓存健康报告"""
    return jsonify(get_cache_health_report())

@app.route('/optimize/cache/cleanup', methods=['POST'])
def cache_cleanup():
    """P4: 脏缓存清理"""
    dirty_count = auto_cleanup_dirty_cache()
    return jsonify({'status': 'success', 'removed': dirty_count})

@app.route('/optimize/performance', methods=['GET'])
def performance_report():
    """P5: 性能报告"""
    return jsonify(get_performance_report())

@app.route('/optimize/performance/reset', methods=['POST'])
def reset_stats():
    """P5: 重置性能统计"""
    reset_performance_stats()
    return jsonify({'status': 'success'})

# ============================================================
# P6: 知识图谱端点
# ============================================================
@app.route('/knowledge/graph', methods=['GET'])
def get_knowledge_graph():
    """获取完整知识图谱"""
    return jsonify(KNOWLEDGE_GRAPH)

@app.route('/knowledge/method/<method_id>', methods=['GET'])
def get_method_detail(method_id):
    """获取方法详情"""
    if method_id in KNOWLEDGE_GRAPH['nodes']:
        method = KNOWLEDGE_GRAPH['nodes'][method_id]
        related = find_related_methods(method_id)
        return jsonify({'method': method, 'related': related})
    return jsonify({'error': 'method not found'}), 404

@app.route('/knowledge/related/<method_id>', methods=['GET'])
def get_related_methods(method_id):
    """获取相关方法"""
    return jsonify(find_related_methods(method_id))

@app.route('/knowledge/category/<category>', methods=['GET'])
def get_by_category(category):
    """按类别查询方法"""
    results = query_knowledge_graph(category=category)
    return jsonify(results)

@app.route('/knowledge/applicable/<scenario>', methods=['GET'])
def get_by_scenario(scenario):
    """按适用场景查询"""
    results = query_knowledge_graph(applicable_to=scenario)
    return jsonify(results)

@app.route('/knowledge/chain/<problem>', methods=['GET'])
def get_optimization_chain_endpoint(problem):
    """获取优化链（问题→方案序列）"""
    try:
        chain = build_optimization_chain(problem)
        return jsonify({'problem': problem, 'chain': chain, 'steps': len(chain)})
    except Exception as e:
        logger.error(f'Optimization chain error: {e}')
        return jsonify({'error': str(e), 'problem': problem}), 500

@app.route('/knowledge/add', methods=['POST'])
def add_new_method():
    """添加新方法"""
    data = request.json if request.is_json else {}
    method_id = data.get('method_id')
    method_data = data.get('method_data', {})
    edges = data.get('edges', [])
    
    if not method_id:
        return jsonify({'error': 'method_id required'}), 400
    
    add_knowledge_method(method_id, method_data, edges)
    return jsonify({'status': 'success', 'method_id': method_id})

@app.route('/knowledge/search', methods=['GET'])
def search_knowledge():
    """搜索知识图谱"""
    query = request.args.get('q', '').lower()
    results = []
    
    for node_id, node_data in KNOWLEDGE_GRAPH['nodes'].items():
        # 搜索名称、效果、适用场景
        searchable = f"{node_data['name']} {node_data['effect']} {' '.join(node_data['applicable_to'])}".lower()
        if query in searchable or query in node_id.lower():
            results.append({node_id: node_data})
    
    return jsonify({'query': query, 'results': results, 'count': len(results)})

# ============================================================
# 豆包增强端点
# ============================================================
@app.route('/knowledge/semantic', methods=['GET'])
def semantic_search_endpoint():
    """语义化检索"""
    query = request.args.get('q', '')
    results = semantic_search_methods(query)
    return jsonify(results)

@app.route('/knowledge/recommend/<problem>', methods=['GET'])
def recommend_scheme_endpoint(problem):
    """方案推荐 + 权重决策"""
    result = scheme_recommendation(problem)
    return jsonify(result)

@app.route('/knowledge/conflict', methods=['POST'])
def detect_conflicts_endpoint():
    """冲突方案检测"""
    method_ids = request.json.get('methods', []) if request.is_json else []
    result = conflict_detect(method_ids)
    return jsonify(result)


# ============================================================
# P7-P9 API端点
# ============================================================

@app.route('/knowledge/parse', methods=['POST'])
def parse_experiments_endpoint():
    """P7-1: 自动解析实验"""
    result = experiment_parser()
    return jsonify(result)

@app.route('/knowledge/mine', methods=['POST'])
def mine_patterns_endpoint():
    """P7-2: 扫描brain_patterns"""
    result = brain_rule_miner()
    return jsonify(result)

@app.route('/brain/hook', methods=['POST'])
def brain_hook_endpoint():
    """P8: Gateway决策联动"""
    query = request.json.get('query', '') if request.is_json else ''
    result = brain_pre_decision_hook(query)
    return jsonify(result)

@app.route('/autoresearch/check', methods=['POST'])
def autoresearch_check_endpoint():
    """P9: 实验立项前检索"""
    proposed = request.json.get('experiment', '') if request.is_json else ''
    result = autoresearch_pre_check(proposed)
    return jsonify(result)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'pong': datetime.now().isoformat()})

@app.route('/config', methods=['GET'])
def get_config():
    return jsonify(BRAIN_CONFIG)

# ============================================================
# OpenAI风格 Embedding API (Gateway需要)
# ============================================================
@app.route('/v1/embeddings', methods=['POST'])
def openai_embeddings():
    """OpenAI风格的embedding API端点"""
    try:
        data = request.get_json() or {}
        input_text = data.get('input', '')
        model = data.get('model', 'all-MiniLM-L6-v2')
        
        # 如果是列表，取第一个
        if isinstance(input_text, list):
            input_text = input_text[0] if input_text else ''
        
        # 使用EmbeddingProvider静态方法
        embedding = EmbeddingProvider.get_embedding(input_text)
        # 转换为Python float (float32不可直接JSON序列化)
        embedding_floats = [float(x) for x in embedding]
        
        return jsonify({
            'object': 'list',
            'data': [{
                'object': 'embedding',
                'index': 0,
                'embedding': embedding_floats,
                'model': model
            }],
            'model': model,
            'usage': {
                'prompt_tokens': len(input_text.split()),
                'total_tokens': len(input_text.split())
            }
        })
    except Exception as e:
        logger.error(f'Embedding API error: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/import/memory', methods=['POST'])
def import_memory():
    """Batch import memory files into vector DB"""
    try:
        data = request.get_json() or {}
        content = data.get('content', '')
        source = data.get('source', 'manual_import')
        metadata = data.get('metadata', {})
        
        if not content or len(content) < 50:
            return jsonify({'error': 'content too short'}), 400
        
        # Get embedding
        embedding = EmbeddingProvider.get_embedding(content[:8000])
        if embedding:
            embedding_floats = [float(x) for x in embedding]
            
            # Insert into vector DB
            if vector_engine:
                conn = sqlite3.connect(vector_engine.db_path)
                c = conn.cursor()
                c.execute('''INSERT INTO embeddings 
                    (content, embedding, source, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (content, json.dumps(embedding_floats), source,
                     json.dumps(metadata), datetime.now().isoformat(),
                     datetime.now().isoformat()))
                conn.commit()
                conn.close()
                
                logger.info(f"Imported: {source} ({len(content)} chars)")
                return jsonify({'success': True, 'source': source, 'chars': len(content)})
        
        return jsonify({'error': 'embedding failed'}), 500
    except Exception as e:
        logger.error(f"Import error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/import/batch', methods=['POST'])
def import_batch():
    """Batch import multiple chunks"""
    try:
        data = request.get_json() or {}
        chunks = data.get('chunks', [])  # List of {content, source, metadata}
        
        if not chunks:
            return jsonify({'error': 'no chunks provided'}), 400
        
        imported = 0
        failed = 0
        
        for chunk in chunks[:100]:  # Limit to 100 per request
            content = chunk.get('content', '')
            source = chunk.get('source', 'batch')
            metadata = chunk.get('metadata', {})
            
            if len(content) < 50:
                continue
            
            try:
                embedding = EmbeddingProvider.get_embedding(content[:8000])
                if embedding and vector_engine:
                    embedding_floats = [float(x) for x in embedding]
                    conn = sqlite3.connect(vector_engine.db_path)
                    c = conn.cursor()
                    c.execute('''INSERT INTO embeddings 
                        (content, embedding, source, metadata, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                        (content, json.dumps(embedding_floats), source,
                         json.dumps(metadata), datetime.now().isoformat(),
                         datetime.now().isoformat()))
                    conn.commit()
                    conn.close()
                    imported += 1
            except:
                failed += 1
        
        logger.info(f"Batch import: {imported} success, {failed} failed")
        return jsonify({'success': True, 'imported': imported, 'failed': failed})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def vector_stats():
    """Vector DB statistics"""
    try:
        if vector_engine:
            conn = sqlite3.connect(vector_engine.db_path)
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM embeddings')
            total = c.fetchone()[0]
            c.execute('SELECT source, COUNT(*) FROM embeddings GROUP BY source')
            sources = {row[0]: row[1] for row in c.fetchall()}
            conn.close()
            return jsonify({'total': total, 'sources': sources})
        return jsonify({'error': 'vector engine not available'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/v1/models', methods=['GET'])
def openai_models():
    """OpenAI风格的models API端点"""
    return jsonify({
        'object': 'list',
        'data': [
            {'id': 'all-MiniLM-L6-v2', 'object': 'model', 'owned_by': 'local'},
            {'id': 'fallback-md5', 'object': 'model', 'owned_by': 'brain'}
        ]
    })

# ============================================================
# 启动
# ============================================================
def run_production():
    try:
        from waitress import serve
        provider, _ = load_provider_state()
        
        logger.info("=" * 60)
        logger.info("Brain Entry V3.0 - Local Vector + Enhanced Security")
        logger.info("=" * 60)
        logger.info(f"Host: {BRAIN_CONFIG['brain_host']}")
        logger.info(f"Port: {BRAIN_CONFIG['brain_port']}")
        logger.info(f"Threads: {BRAIN_CONFIG['thread_pool']}")
        logger.info(f"Embedding: {provider}")
        logger.info(f"Vector Engine: {vector_engine is not None}")
        logger.info(f"Cache: {cache_manager is not None}")
        logger.info(f"Feedback: {feedback_manager is not None}")
        logger.info(f"Backup: {backup_manager is not None}")
        logger.info(f"Transaction: {transaction_manager is not None}")
        logger.info(f"InputValidator: True")
        logger.info("=" * 60)
        
        serve(app, host=BRAIN_CONFIG['brain_host'], port=BRAIN_CONFIG['brain_port'],
              threads=BRAIN_CONFIG['thread_pool'], connection_limit=100, cleanup_interval=30)
    except ImportError:
        logger.warning("Waitress not installed, using Flask dev server")
        app.run(host=BRAIN_CONFIG['brain_host'], port=BRAIN_CONFIG['brain_port'], threaded=True)

if __name__ == '__main__':
    run_production()