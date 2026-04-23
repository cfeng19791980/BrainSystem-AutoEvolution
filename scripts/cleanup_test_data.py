# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

conn = sqlite3.connect(r'C:\Users\Administrator\.openclaw\brain-system\data\.session_screening.db')
c = conn.cursor()

# 清理旧测试数据
c.execute('DELETE FROM screened_sessions WHERE session_key=?', ('test-session-001',))
c.execute('DELETE FROM screened_sessions WHERE importance_level IS NULL')
c.execute('DELETE FROM collection_log WHERE session_key=?', ('test-session-001',))

conn.commit()

c.execute('SELECT COUNT(*) FROM screened_sessions')
print(f'清理后记录数: {c.fetchone()[0]}')

c.execute('SELECT importance_level, COUNT(*) FROM screened_sessions GROUP BY importance_level')
print(f'级别分布: {dict(c.fetchall())}')

conn.close()
print('清理完成')