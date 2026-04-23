# -*- coding: utf-8 -*-
"""
Brain API Lite V3 - 完整功能版 + 超链接格式
功能:
1. 拦截LLM直接回复
2. 知识库集成（memory_search）+ 超链接格式
3. 反馈闭环追踪
4. 决策记录与统计
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from flask import Flask, request, jsonify
import json
import os
import subprocess
import re
from datetime import datetime

# 尝试导入向量引擎
try:
    from vec_engine import VectorEngine
    vec_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.brain_vectors.db')
    vec_engine = VectorEngine(vec_db_path)
    VEC_AVAILABLE = vec_engine.vec_available
except:
    VEC_AVAILABLE = False
    vec_engine = None

app = Flask(__name__)

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_PATH, '.brain_hook_state.json')
MEMORY_PATH = os.path.join(BASE_PATH, 'MEMORY.md')

# Brain状态
BRAIN_STATE = {
    'decisions': [],
    'feedbacks': [],
    'knowledge_hits': 0,
    'patterns': []
}

def load_state():
    global BRAIN_STATE
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                BRAIN_STATE = {
                    'decisions': data.get('decisions', []),
                    'feedbacks': data.get('feedbacks', []),
                    'knowledge_hits': data.get('knowledge_hits', 0),
                    'patterns': data.get('patterns', [])
                }
    except:
        pass

def save_state():
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(BRAIN_STATE, f, ensure_ascii=False, indent=2)
    except:
        pass

# ========== 功能2: 知识库集成 ==========

def search_memory(query, max_results=15):
    """搜索MEMORY.md和memory目录"""
    results = []
    
    # 提取关键词：分离英文和中文
    query_clean = query.lower().replace('brain', '').replace('大脑', '').replace('智能', '').replace('决策', '').strip()
    search_terms = []
    
    # 英文关键词
    english_words = re.findall(r'[a-z]{2,}', query_clean)
    search_terms.extend(english_words)
    
    # 中文关键词
    chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,}', query)
    search_terms.extend(chinese_words)
    
    if not search_terms:
        search_terms = ['github', 'python', 'react']
    
    search_terms = list(set(search_terms))[:5]
    
    # 向量搜索
    if VEC_AVAILABLE and vec_engine:
        try:
            vec_results = vec_engine.search(query, max_results)
            for r in vec_results:
                results.append({
                    'source': f"vector_db/{r.get('id', 'unknown')}",
                    'content': r.get('content', ''),
                    'score': r.get('score', 0)
                })
        except:
            pass
    
    # 搜索MEMORY.md
    if os.path.exists(MEMORY_PATH):
        try:
            with open(MEMORY_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                matched = any(term.lower() in line.lower() for term in search_terms)
                if matched and line.strip():
                    context_start = max(0, i-2)
                    context_end = min(len(lines), i+3)
                    context = '\n'.join(lines[context_start:context_end])
                    results.append({
                        'source': 'MEMORY.md',
                        'line': i+1,
                        'content': context[:200],
                        'match': line.strip()[:100]
                    })
                    if len(results) >= max_results:
                        break
        except:
            pass
    
    # 搜索memory目录
    memory_dir = os.path.join(BASE_PATH, 'memory')
    if os.path.exists(memory_dir):
        for root, dirs, files in os.walk(memory_dir):
            for fname in files:
                if fname.endswith('.md'):
                    fpath = os.path.join(root, fname)
                    rel_path = os.path.relpath(fpath, memory_dir)
                    try:
                        with open(fpath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        content_matched = any(term.lower() in content.lower() for term in search_terms)
                        if content_matched:
                            for para in content.split('\n\n'):
                                para_matched = any(term.lower() in para.lower() for term in search_terms)
                                if para_matched and para.strip():
                                    results.append({
                                        'source': f'memory/{rel_path}',
                                        'content': para[:400]
                                    })
                                    if len(results) >= max_results * 2:
                                        break
                    except:
                        pass
    
    return results

# ========== 功能3: 反馈闭环 ==========

def record_feedback(decision_id, success, notes=''):
    """记录执行反馈"""
    feedback = {
        'decision_id': decision_id,
        'success': success,
        'notes': notes,
        'timestamp': datetime.now().isoformat()
    }
    BRAIN_STATE['feedbacks'].append(feedback)
    
    for dec in BRAIN_STATE['decisions']:
        if dec['id'] == decision_id:
            dec['feedback'] = feedback
            break
    
    save_state()
    return feedback

# ========== 智能触发规则 ==========

TRIGGER_RULES = {
    'keywords': ['brain', '大脑', '智能决策', '智能助手', '智能'],
    'intents': {
        'query': ['查询', '搜索', '查找', '找', '帮我找'],
        'analyze': ['分析', '评估', '判断', '检查', '诊断'],
        'suggest': ['建议', '推荐', '推荐一下', '有什么好'],
        'learn': ['学习', '怎么用', '如何', '教程', '指南'],
        'compare': ['对比', '比较', '哪个好', '区别'],
        'action': ['执行', '运行', '开始', '启动', '做']
    }
}

def detect_intent(content):
    if not content:
        return None
    content_lower = content.lower()
    for intent, keywords in TRIGGER_RULES['intents'].items():
        for kw in keywords:
            if kw in content_lower:
                return intent
    return 'general'

def should_trigger(content):
    if not content:
        return False, 0.5, None
    content_lower = content.lower()
    for kw in TRIGGER_RULES['keywords']:
        if kw in content_lower:
            return True, 0.9, detect_intent(content)
    intent = detect_intent(content)
    if intent and intent != 'general':
        return True, 0.7, intent
    return False, 0.5, None

def generate_smart_suggestions(intent, content, knowledge_results):
    suggestions = []
    intent_suggestions = {
        'query': ['搜索外部知识库', '查询历史记录'],
        'analyze': ['执行深度分析', '生成分析报告'],
        'suggest': ['推荐最佳方案', '列出备选方案'],
        'learn': ['查找教程文档', '获取示例代码'],
        'compare': ['对比关键指标', '生成对比表格'],
        'action': ['准备执行环境', '检查前置条件']
    }
    if intent and intent in intent_suggestions:
        suggestions.extend(intent_suggestions[intent])
    if knowledge_results:
        suggestions.append(f'已找到{len(knowledge_results)}条相关知识')
    else:
        suggestions.append('搜索相关知识库')
    if 'github' in content.lower():
        suggestions.append('查看GitHub项目详情')
    if 'python' in content.lower():
        suggestions.append('获取Python最佳实践')
    return suggestions[:5]

# ========== 决策引擎 ==========

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'brain-api-lite-v3',
        'port': 5000,
        'features': ['block_llm', 'knowledge_search', 'feedback_loop', 'smart_trigger', 'intent_detect', 'vector_search', 'hyperlink_format'],
        'vector_available': VEC_AVAILABLE,
        'trigger_rules': len(TRIGGER_RULES['keywords']) + sum(len(v) for v in TRIGGER_RULES['intents'].values())
    })

@app.route('/api/decide', methods=['POST'])
def decide():
    """Brain决策入口"""
    data = request.get_json() or {}
    content = data.get('content', '')
    session_key = data.get('sessionKey', 'unknown')
    sender_id = data.get('senderId', 'unknown')
    
    is_brain_trigger, confidence, intent = should_trigger(content)
    
    knowledge_results = []
    if is_brain_trigger and content:
        knowledge_results = search_memory(content, max_results=15)
        BRAIN_STATE['knowledge_hits'] += len(knowledge_results)
    
    decision = {
        'id': f"dec_{datetime.now().strftime('%H%M%S')}",
        'timestamp': datetime.now().isoformat(),
        'triggered': is_brain_trigger,
        'action': 'process' if is_brain_trigger else 'pass',
        'confidence': confidence,
        'intent': intent,
        'content_preview': content[:100] if content else '',
        'session_key': session_key,
        'sender_id': sender_id,
        'knowledge_results': knowledge_results,
        'suggestions': []
    }
    
    if is_brain_trigger:
        decision['block_llm'] = True
        suggestions = generate_smart_suggestions(intent, content, knowledge_results)
        decision['suggestions'] = suggestions
        
        reply_parts = [f"🧠 **Brain已接收请求**"]
        reply_parts.append(f"\n**置信度**: {confidence}")
        if intent:
            reply_parts.append(f"\n**意图**: {intent}")
        
        # 知识库结果 - 超链接格式
        if knowledge_results:
            reply_parts.append(f"\n\n📚 **相关知识** (共{len(knowledge_results)}条):")
            reply_parts.append("\n")
            for i, kr in enumerate(knowledge_results, 1):
                source = kr.get('source', 'unknown')
                kr_content = kr.get('content', kr.get('match', ''))
                first_line = kr_content.split('\n')[0][:50].strip().replace('#', '')
                
                # 构建Markdown超链接
                if 'github_' in source.lower():
                    file_name = source.split('/')[-1]
                    project_name = file_name.replace('github_', '').replace('.md', '')
                    link = f"[{project_name}](memory/knowledge/{file_name})"
                    title = f"📦 {link}"
                elif source == 'MEMORY.md':
                    link = f"[MEMORY.md](MEMORY.md)"
                    title = f"📝 {link}"
                else:
                    file_name = source.split('/')[-1].replace('.md', '')
                    link = f"[{file_name}]({source})"
                    title = f"📄 {link}"
                
                brief = kr_content[:35].replace('#', '').replace('\n', ' ').strip()
                reply_parts.append(f"{i}. {title} - {brief}...")
            
            reply_parts.append("\n\n💡 点击链接可查看知识详情")
        else:
            reply_parts.append("\n\n📚 未找到相关知识")
        
        # 智能建议
        reply_parts.append("\n\n💡 **建议操作**:")
        for i, sug in enumerate(suggestions, 1):
            reply_parts.append(f"\n{i}. {sug}")
        
        reply_parts.append(f"\n\n---\n`决策ID: {decision['id']}`")
        
        decision['reply_text'] = '\n'.join(reply_parts)
    
    BRAIN_STATE['decisions'].append(decision)
    if len(BRAIN_STATE['decisions']) > 100:
        BRAIN_STATE['decisions'] = BRAIN_STATE['decisions'][-100:]
    save_state()
    
    return jsonify(decision)

@app.route('/api/feedback', methods=['POST'])
def feedback():
    """反馈闭环"""
    data = request.get_json() or {}
    decision_id = data.get('decision_id', '')
    success = data.get('success', True)
    notes = data.get('notes', '')
    
    feedback = record_feedback(decision_id, success, notes)
    return jsonify({'status': 'recorded', 'feedback': feedback})

@app.route('/api/stats', methods=['GET'])
def stats():
    """统计信息"""
    decisions = BRAIN_STATE['decisions']
    feedbacks = BRAIN_STATE['feedbacks']
    
    success_count = sum(1 for f in feedbacks if f['success'])
    success_rate = success_count / max(len(feedbacks), 1)
    
    return jsonify({
        'total_decisions': len(decisions),
        'total_feedbacks': len(feedbacks),
        'knowledge_hits': BRAIN_STATE['knowledge_hits'],
        'trigger_rate': sum(1 for d in decisions if d['triggered']) / max(len(decisions), 1),
        'feedback_success_rate': success_rate,
        'last_decision': decisions[-1] if decisions else None,
        'recent_feedbacks': feedbacks[-5:] if feedbacks else []
    })

# 加载状态
load_state()

if __name__ == '__main__':
    print('[Brain API Lite V3] Starting on port 5000...')
    print('[Brain API Lite V3] Features: block_llm, knowledge_search, hyperlink_format')
    app.run(host='127.0.0.1', port=5000, threaded=True)