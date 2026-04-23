# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
import os
import json
import re
import hashlib
from datetime import datetime

print("=" * 60)
print("OPT-REQ-009 Phase 1-4 实施（修复版）")
print("=" * 60)

DB_PATH = r'C:\Users\Administrator\.openclaw\brain-system\data\.session_screening.db'

# Phase 1: 表结构
print("\n[Phase 1] 创建表结构...")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS screened_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_key TEXT,
    message_id TEXT,
    role TEXT,
    content TEXT,
    importance_level TEXT,
    keywords TEXT,
    intent_type TEXT,
    created_at TEXT,
    vectorized INTEGER DEFAULT 0,
    UNIQUE(session_key, message_id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS collection_log (
    session_key TEXT PRIMARY KEY,
    collected_at TEXT,
    trigger_type TEXT,
    p0_count INTEGER,
    p1_count INTEGER
)''')

c.execute('CREATE INDEX IF NOT EXISTS idx_importance ON screened_sessions(importance_level)')
conn.commit()
print("  表创建完成")

# Phase 2: 篮选规则
print("\n[Phase 2] 篮选规则...")

WHITELIST = ['决策', '诊断', '修复', '升级', '问题', '解决', '验证', '完成', '发现']
BLACKLIST = ['天气', '闲聊', '你好', '谢谢', '帮忙', '请问', '好的', '收到']
P1_KEYWORDS = ['添加', '修改', '创建', '执行', '部署', '测试', '分析', '导入', '配置']

def screen_message(content):
    """筛选消息"""
    if not content or len(content) < 10:
        return 'P2', []
    
    # 黑名单 -> 直接跳过
    for kw in BLACKLIST:
        if kw in content:
            return 'P2', []
    
    # 白名单 -> P0
    for kw in WHITELIST:
        if kw in content:
            return 'P0', extract_keywords(content)
    
    # P1关键词
    for kw in P1_KEYWORDS:
        if kw in content:
            return 'P1', extract_keywords(content)
    
    return 'P1', extract_keywords(content)

def extract_keywords(content):
    english = re.findall(r'[a-zA-Z_]{3,}', content)
    chinese = re.findall(r'[\u4e00-\u9fa5]{2,}', content)
    return list(set(english + chinese))[:5]

def desensitize(content):
    content = re.sub(r'API_KEY[\w-]+', 'API_KEY=****', content)
    content = re.sub(r'password[\w-]+', 'password=****', content)
    content = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '***@***', content)
    return content

print(f"  白名单: {len(WHITELIST)}项, 黑名单: {len(BLACKLIST)}项")

# Phase 3: 采集入库
print("\n[Phase 3] 测试采集...")

def collect_session(session_key, messages, trigger_type="test"):
    c = conn.cursor()
    c.execute('SELECT 1 FROM collection_log WHERE session_key=?', (session_key,))
    if c.fetchone():
        print(f"  [跳过] {session_key} 已采集")
        return 0
    
    screened = []
    p0_count, p1_count = 0, 0
    
    for msg in messages:
        role = msg.get('role', '')
        content = msg.get('content', '')
        
        if isinstance(content, list):
            content = ' '.join([x.get('text', '') for x in content if isinstance(x, dict)])
        
        if not content or role not in ['user', 'assistant']:
            continue
        
        level, keywords = screen_message(content)
        
        # 关键修复：P2和空内容完全跳过
        if level == 'P2':
            print(f"  [P2跳过] {content[:30]}...")
            continue
        
        content_safe = desensitize(content)
        msg_id = hashlib.md5(f"{session_key}:{role}:{content[:30]}".encode()).hexdigest()[:12]
        
        screened.append({
            'session_key': session_key,
            'message_id': msg_id,
            'role': role,
            'content': content_safe,
            'importance_level': level,
            'keywords': json.dumps(keywords),
            'created_at': datetime.now().isoformat(),
        })
        
        if level == 'P0':
            p0_count += 1
        elif level == 'P1':
            p1_count += 1
    
    for item in screened:
        c.execute('''INSERT OR IGNORE INTO screened_sessions 
            (session_key, message_id, role, content, importance_level, keywords, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (item['session_key'], item['message_id'], item['role'], item['content'],
             item['importance_level'], item['keywords'], item['created_at']))
    
    c.execute('''INSERT INTO collection_log 
        (session_key, collected_at, trigger_type, p0_count, p1_count)
        VALUES (?, ?, ?, ?, ?)''',
        (session_key, datetime.now().isoformat(), trigger_type, p0_count, p1_count))
    
    conn.commit()
    print(f"  [入库] {session_key}: {len(screened)}条 (P0={p0_count}, P1={p1_count})")
    return len(screened)

# 测试
test_messages = [
    {"role": "user", "content": "v5过拟合诊断：发现数据泄露"},
    {"role": "assistant", "content": "诊断结论：训练包含测试数据"},
    {"role": "user", "content": "添加brain-hook拦截"},
    {"role": "assistant", "content": "代码实现完成"},
    {"role": "user", "content": "今天天气怎么样？"},
    {"role": "assistant", "content": "抱歉无法查询天气"},
]

collect_session("test-002", test_messages)

# Phase 4: 监控
print("\n[Phase 4] 监控统计...")
c = conn.cursor()
c.execute('SELECT importance_level, COUNT(*) FROM screened_sessions GROUP BY importance_level')
levels = dict(c.fetchall())
c.execute('SELECT COUNT(*) FROM collection_log')
sessions = c.fetchone()[0]

print(f"  级别分布: {levels}")
print(f"  会话数: {sessions}")

conn.close()

print("\n" + "=" * 60)
print("Phase 1-4 完成，筛选逻辑已修复")
print("=" * 60)