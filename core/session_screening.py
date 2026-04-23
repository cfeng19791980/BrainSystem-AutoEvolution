# -*- coding: utf-8 -*-
"""
OPT-REQ-009: 会话筛选入库系统
Phase 1-4: 完整实施
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3
import os
import json
import re
import hashlib
from datetime import datetime, timedelta

print("=" * 60)
print("OPT-REQ-009 Phase 1-4 实施")
print("=" * 60)

DB_PATH = r'C:\Users\Administrator\.openclaw\brain-system\data\.session_screening.db'

# ============================================================
# Phase 1: 表结构创建
# ============================================================
print("\n[Phase 1] 创建表结构...")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# session_pending表（单轮完成标记）
c.execute('''CREATE TABLE IF NOT EXISTS session_pending (
    session_key TEXT PRIMARY KEY,
    last_msg_time TEXT,
    pending_status TEXT DEFAULT 'active',
    messages_count INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
)''')

# screened_sessions表（筛选入库）
c.execute('''CREATE TABLE IF NOT EXISTS screened_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_key TEXT,
    message_id TEXT,
    role TEXT,
    content TEXT,
    importance_level TEXT,
    keywords TEXT,
    intent_type TEXT,
    embedding TEXT,
    created_at TEXT,
    vectorized INTEGER DEFAULT 0,
    expires_at TEXT,
    is_archived INTEGER DEFAULT 0,
    UNIQUE(session_key, message_id)
)''')

# collection_log表（防重复）
c.execute('''CREATE TABLE IF NOT EXISTS collection_log (
    session_key TEXT PRIMARY KEY,
    collected_at TEXT,
    trigger_type TEXT,
    messages_count INTEGER,
    p0_count INTEGER,
    p1_count INTEGER
)''')

# 索引
c.execute('CREATE INDEX IF NOT EXISTS idx_importance ON screened_sessions(importance_level)')
c.execute('CREATE INDEX IF NOT EXISTS idx_keywords ON screened_sessions(keywords)')
c.execute('CREATE INDEX IF NOT EXISTS idx_session ON screened_sessions(session_key)')

conn.commit()
print("  表创建完成: session_pending, screened_sessions, collection_log")

# ============================================================
# Phase 2: 篮选规则+触发检测器
# ============================================================
print("\n[Phase 2] 篮选规则+触发检测器...")

# 黑白名单
WHITELIST = ['决策', '诊断', '修复', '升级', '问题', '解决', '验证', '完成', '发现']
BLACKLIST = ['天气', '闲聊', '你好', '谢谢', '帮忙', '请问', '好的', '收到']
SEMANTIC_PATTERNS = [r'问题.*方案', r'诊断.*结论', r'需求.*实现', r'升级.*完成']
P1_KEYWORDS = ['添加', '修改', '创建', '执行', '部署', '测试', '分析', '导入', '配置', '优化']

# 脱敏规则
SENSITIVE_PATTERNS = [
    (r'API_KEY["\s:=]+["\']?[\w-]+', 'API_KEY=****'),
    (r'password["\s:=]+["\']?[\w-]+', 'password=****'),
    (r'\b[\w.-]+@[\w.-]+\.\w+\b', '***@***'),
]

def screen_message(content):
    """筛选消息重要性"""
    if not content or len(content) < 10:
        return None, []
    
    # 黑名单检测
    for kw in BLACKLIST:
        if kw in content:
            return 'P2', []  # 直接丢弃
    
    # 白名单检测（强制P0）
    for kw in WHITELIST:
        if kw in content:
            keywords = extract_keywords(content)
            return 'P0', keywords
    
    # 语义模式检测
    for pattern in SEMANTIC_PATTERNS:
        if re.search(pattern, content):
            keywords = extract_keywords(content)
            return 'P0', keywords
    
    # P1关键词检测
    for kw in P1_KEYWORDS:
        if kw in content:
            keywords = extract_keywords(content)
            return 'P1', keywords
    
    # 默认P1
    keywords = extract_keywords(content)
    return 'P1', keywords

def extract_keywords(content):
    """提取关键词"""
    english = re.findall(r'[a-zA-Z_]{3,}', content)
    chinese = re.findall(r'[\u4e00-\u9fa5]{2,}', content)
    return list(set(english + chinese))[:10]

def desensitize(content):
    """脱敏处理"""
    for pattern, replacement in SENSITIVE_PATTERNS:
        content = re.sub(pattern, replacement, content)
    return content

class SessionTerminationDetector:
    """会话终止检测器"""
    
    TIMEOUT_THRESHOLD = 300  # 5分钟
    
    def check_session_end(self, session_key, last_msg_time):
        """三大触发条件检测"""
        now = datetime.now()
        elapsed = (now - last_msg_time).total_seconds()
        
        # 条件1: 5分钟无交互
        if elapsed >= self.TIMEOUT_THRESHOLD:
            return "timeout_terminate"
        
        # 条件2: 检查pending状态
        c = conn.cursor()
        c.execute('SELECT pending_status FROM session_pending WHERE session_key=?', (session_key,))
        row = c.fetchone()
        if row and row[0] == 'complete':
            return "round_complete"
        
        return "active"
    
    def mark_round_complete(self, session_key, last_msg_time, msg_count):
        """标记单轮完成（pending状态）"""
        now = datetime.now().isoformat()
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO session_pending 
            (session_key, last_msg_time, pending_status, messages_count, created_at, updated_at)
            VALUES (?, ?, 'complete', ?, ?, ?)''',
            (session_key, last_msg_time.isoformat(), msg_count, now, now))
        conn.commit()

print("  篮选规则: 白名单{}个, 黑名单{}个".format(len(WHITELIST), len(BLACKLIST)))
print("  脱敏规则: {}项".format(len(SENSITIVE_PATTERNS)))

# ============================================================
# Phase 3: 异步采集入库
# ============================================================
print("\n[Phase 3] 异步采集入库...")

def collect_session(session_key, messages, trigger_type="timeout"):
    """采集会话并入库"""
    # 防重复检查
    c = conn.cursor()
    c.execute('SELECT 1 FROM collection_log WHERE session_key=?', (session_key,))
    if c.fetchone():
        print(f"  [跳过] {session_key} 已采集")
        return 0
    
    # 篮选消息
    screened = []
    p0_count, p1_count = 0, 0
    
    for msg in messages:
        role = msg.get('role', '')
        content = msg.get('content', '')
        
        if isinstance(content, list):
            content = ' '.join([c.get('text', '') for c in content if isinstance(c, dict)])
        
        if not content or role not in ['user', 'assistant']:
            continue
        
        # 筛选
        level, keywords = screen_message(content)
        
        if level == 'P2':
            continue  # 跳过
        
        # 脱敏
        content_safe = desensitize(content)
        
        # 生成message_id
        msg_id = hashlib.md5(f"{session_key}:{role}:{content[:50]}".encode()).hexdigest()[:16]
        
        screened.append({
            'session_key': session_key,
            'message_id': msg_id,
            'role': role,
            'content': content_safe,
            'importance_level': level,
            'keywords': json.dumps(keywords),
            'intent_type': 'session_import',
            'created_at': datetime.now().isoformat(),
        })
        
        if level == 'P0':
            p0_count += 1
        elif level == 'P1':
            p1_count += 1
    
    # 入库
    for item in screened:
        try:
            c.execute('''INSERT OR IGNORE INTO screened_sessions 
                (session_key, message_id, role, content, importance_level, keywords, intent_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (item['session_key'], item['message_id'], item['role'], item['content'],
                 item['importance_level'], item['keywords'], item['intent_type'], item['created_at']))
        except Exception as e:
            print(f"  入库错误: {e}")
    
    # 记录采集日志
    c.execute('''INSERT INTO collection_log 
        (session_key, collected_at, trigger_type, messages_count, p0_count, p1_count)
        VALUES (?, ?, ?, ?, ?, ?)''',
        (session_key, datetime.now().isoformat(), trigger_type, len(screened), p0_count, p1_count))
    
    conn.commit()
    
    print(f"  [入库] {session_key}: {len(screened)}条 (P0={p0_count}, P1={p1_count})")
    return len(screened)

# 模拟采集测试
print("\n  测试采集...")
test_session = "test-session-001"
test_messages = [
    {"role": "user", "content": "v5过拟合诊断：发现数据泄露导致虚假100%胜率"},
    {"role": "assistant", "content": "诊断结论：训练包含测试数据，修复方案排除测试数据"},
    {"role": "user", "content": "添加brain-hook拦截逻辑"},
    {"role": "assistant", "content": "代码实现：监听before_prompt_build事件"},
    {"role": "user", "content": "今天天气怎么样？"},  # P2应跳过
    {"role": "assistant", "content": "抱歉无法查询天气"},
]

count = collect_session(test_session, test_messages, trigger_type="test")
print(f"  测试完成: 入库{count}条")

# ============================================================
# Phase 4: 灰度试运行+监控
# ============================================================
print("\n[Phase 4] 灰度试运行配置...")

# 监控统计
def get_monitoring_stats():
    """监控统计"""
    c = conn.cursor()
    
    # 总入库数
    c.execute('SELECT COUNT(*) FROM screened_sessions')
    total = c.fetchone()[0]
    
    # P0/P1分布
    c.execute('SELECT importance_level, COUNT(*) FROM screened_sessions GROUP BY importance_level')
    levels = c.fetchall()
    
    # 已采集会话数
    c.execute('SELECT COUNT(*) FROM collection_log')
    sessions = c.fetchone()[0]
    
    # 平均入库率
    c.execute('SELECT AVG(messages_count) FROM collection_log')
    avg_count = c.fetchone()[0] or 0
    
    return {
        'total_messages': total,
        'level_distribution': dict(levels),
        'sessions_collected': sessions,
        'avg_messages_per_session': round(avg_count, 2),
    }

stats = get_monitoring_stats()
print("  监控统计:")
print(f"    总入库: {stats['total_messages']}条")
print(f"    级别分布: {stats['level_distribution']}")
print(f"    会话数: {stats['sessions_collected']}")
print(f"    平均入库/会话: {stats['avg_messages_per_session']}")

# 灰度配置
GRAYSCALE_CONFIG = {
    'trial': 0.1,     # 试运行10%
    'expand': 0.5,    # 放量50%
    'full': 1.0,      # 全量100%
    'current': 'trial',  # 当前阶段
}

print(f"\n  灰度配置:")
print(f"    当前阶段: {GRAYSCALE_CONFIG['current']} ({int(GRAYSCALE_CONFIG['trial']*100)}%)")

conn.close()

print("\n" + "=" * 60)
print("Phase 1-4 完成")
print("=" * 60)
print("下一步:")
print("  1. 集成到brain_entry.py")
print("  2. 配置定时采集任务")
print("  3. 运行回归测试")
print("=" * 60)