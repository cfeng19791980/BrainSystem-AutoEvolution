# -*- coding: utf-8 -*-
"""
Feedback Daily Aggregation Script
每天00:00执行，分析反馈数据并生成优化建议
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
import logging

# 配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = "C:/Users/Administrator/.openclaw/brain-system/data/.brain_feedback.db"
STATS_DB_PATH = "C:/Users/Administrator/.openclaw/brain-system/data/.brain_feedback_stats.db"
REPORT_PATH = "C:/Users/Administrator/.openclaw/brain-system/data/daily_feedback_report.json"

def aggregate_daily_stats():
    """聚合每日统计"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 获取昨日的反馈数据
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 按意图类型统计
        c.execute('''SELECT intent_type, user_action, COUNT(*) 
                    FROM feedback 
                    WHERE timestamp LIKE ? 
                    GROUP BY intent_type, user_action''', (yesterday + '%',))
        intent_rows = c.fetchall()
        
        by_intent = {}
        for intent_type, action, count in intent_rows:
            if intent_type not in by_intent:
                by_intent[intent_type] = {'accepted': 0, 'rejected': 0, 'modified': 0, 'ignored': 0, 'total': 0}
            if action in by_intent[intent_type]:
                by_intent[intent_type][action] = count
            by_intent[intent_type]['total'] += count
        
        # 计算采纳率
        for intent_type, stats in by_intent.items():
            total = stats['total']
            accepted = stats.get('accepted', 0)
            stats['accept_rate'] = round(accepted / total if total > 0 else 0, 2)
        
        # 按置信度区间统计
        c.execute('''SELECT 
                    CASE 
                        WHEN confidence < 0.3 THEN 'low'
                        WHEN confidence < 0.7 THEN 'medium'
                        ELSE 'high'
                    END as confidence_level,
                    user_action, COUNT(*)
                    FROM feedback 
                    WHERE timestamp LIKE ?
                    GROUP BY confidence_level, user_action''', (yesterday + '%',))
        
        by_confidence = {}
        for level, action, count in c.fetchall():
            if level not in by_confidence:
                by_confidence[level] = {'accepted': 0, 'rejected': 0, 'total': 0}
            by_confidence[level][action] = count
            by_confidence[level]['total'] += count
        
        # 总体统计
        c.execute('SELECT COUNT(*) FROM feedback WHERE timestamp LIKE ?', (yesterday + '%',))
        total_yesterday = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM feedback WHERE timestamp LIKE ? AND user_action = 'accepted'", (yesterday + '%',))
        accepted_yesterday = c.fetchone()[0]
        
        conn.close()
        
        return {
            'date': yesterday,
            'total_events': total_yesterday,
            'accepted_count': accepted_yesterday,
            'overall_accept_rate': round(accepted_yesterday / total_yesterday if total_yesterday > 0 else 0, 2),
            'by_intent_type': by_intent,
            'by_confidence_level': by_confidence,
            'generated_at': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Aggregation error: {e}")
        return None

def generate_optimization_report(stats):
    """生成优化报告"""
    if not stats:
        return []
    
    recommendations = []
    
    # 按意图类型分析
    for intent_type, data in stats.get('by_intent_type', {}).items():
        accept_rate = data.get('accept_rate', 0)
        total = data.get('total', 0)
        
        if total < 3:  # 样本太少
            continue
        
        if accept_rate < 0.5:
            recommendations.append({
                'priority': 'HIGH' if accept_rate < 0.3 else 'MEDIUM',
                'type': 'threshold_adjustment',
                'target': intent_type,
                'current_rate': accept_rate,
                'suggestion': f"提高{intent_type}触发阈值，当前采纳率仅{accept_rate:.0%}",
                'action': 'increase_confidence_threshold'
            })
        elif accept_rate > 0.85:
            recommendations.append({
                'priority': 'LOW',
                'type': 'priority_boost',
                'target': intent_type,
                'current_rate': accept_rate,
                'suggestion': f"{intent_type}表现优异，可提高触发优先级",
                'action': 'increase_priority'
            })
    
    # 按置信度分析
    for level, data in stats.get('by_confidence_level', {}).items():
        total = data.get('total', 0)
        accepted = data.get('accepted', 0)
        rate = accepted / total if total > 0 else 0
        
        if level == 'low' and total > 5 and rate < 0.3:
            recommendations.append({
                'priority': 'HIGH',
                'type': 'confidence_warning',
                'target': 'low_confidence',
                'current_rate': rate,
                'suggestion': f"低置信度决策采纳率仅{rate:.0%}，建议拒绝或降级处理",
                'action': 'reject_low_confidence'
            })
    
    return recommendations

def save_daily_report(stats, recommendations):
    """保存每日报告"""
    report = {
        'stats': stats,
        'recommendations': recommendations,
        'generated_at': datetime.now().isoformat()
    }
    
    try:
        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"Report saved to {REPORT_PATH}")
    except Exception as e:
        logger.error(f"Save error: {e}")

def update_stats_db(stats):
    """更新统计数据库（历史聚合）"""
    try:
        conn = sqlite3.connect(STATS_DB_PATH)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS daily_stats (
            date TEXT PRIMARY KEY,
            total_events INTEGER,
            accepted_count INTEGER,
            overall_accept_rate REAL,
            by_intent_json TEXT,
            by_confidence_json TEXT,
            created_at TEXT
        )''')
        
        c.execute('''INSERT OR REPLACE INTO daily_stats 
            (date, total_events, accepted_count, overall_accept_rate, by_intent_json, by_confidence_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (stats['date'], stats['total_events'], stats['accepted_count'], stats['overall_accept_rate'],
             json.dumps(stats['by_intent_type']), json.dumps(stats['by_confidence_level']),
             datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        logger.info(f"Stats DB updated for {stats['date']}")
    except Exception as e:
        logger.error(f"Stats DB error: {e}")

def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("Feedback Daily Aggregation Started")
    logger.info("=" * 50)
    
    # 1. 聚合统计
    stats = aggregate_daily_stats()
    if stats:
        logger.info(f"Processed {stats['total_events']} events for {stats['date']}")
        logger.info(f"Overall accept rate: {stats['overall_accept_rate']:.0%}")
        
        # 2. 生成优化建议
        recommendations = generate_optimization_report(stats)
        logger.info(f"Generated {len(recommendations)} recommendations")
        
        for rec in recommendations:
            logger.info(f"  [{rec['priority']}] {rec['suggestion']}")
        
        # 3. 保存报告
        save_daily_report(stats, recommendations)
        
        # 4. 更新统计数据库
        update_stats_db(stats)
    else:
        logger.warning("No stats generated")
    
    logger.info("=" * 50)
    logger.info("Feedback Daily Aggregation Completed")
    logger.info("=" * 50)

if __name__ == '__main__':
    main()