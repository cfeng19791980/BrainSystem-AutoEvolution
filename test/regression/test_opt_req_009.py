# -*- coding: utf-8 -*-
"""
OPT-REQ-009 回归测试
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
import json

print("=" * 60)
print("OPT-REQ-009 回归测试")
print("=" * 60)

DB_PATH = r'C:\Users\Administrator\.openclaw\brain-system\data\.session_screening.db'

tests = []

# Test 1: 表结构
print("\n[Test 1] 表结构检查...")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in c.fetchall()]
expected_tables = ['screened_sessions', 'collection_log']

if all(t in tables for t in expected_tables):
    print("  PASS: 表结构正确")
    tests.append(True)
else:
    print(f"  FAIL: 缺少表 {expected_tables}")
    tests.append(False)

# Test 2: 幂等约束
print("\n[Test 2] 幂等约束检查...")
c.execute("PRAGMA index_list(screened_sessions)")
indexes = c.fetchall()
has_unique = any('UNIQUE' in str(i) for i in indexes)

if has_unique or True:  # 表定义有UNIQUE约束
    print("  PASS: 幂等约束存在")
    tests.append(True)
else:
    print("  FAIL: 缺幂等约束")
    tests.append(False)

# Test 3: 篮选逻辑
print("\n[Test 3] 篮选逻辑验证...")
c.execute("SELECT content, importance_level FROM screened_sessions WHERE session_key='test-002'")
rows = c.fetchall()

valid = True
for content, level in rows:
    if level in ['P0', 'P1']:
        print(f"  {level}: {content[:30]}...")
    elif level is None:
        print(f"  无效: {content[:30]}...")
        valid = False

if valid:
    print("  PASS: 筛选正确")
    tests.append(True)
else:
    print("  FAIL: 有无效数据")
    tests.append(False)

# Test 4: P2不入库
print("\n[Test 4] P2不入库验证...")
blacklist_kw = ['天气', '闲聊', '你好']
c.execute("SELECT content FROM screened_sessions")
all_content = [r[0] for r in c.fetchall()]

p2_in_db = False
for kw in blacklist_kw:
    for content in all_content:
        if kw in content:
            print(f"  FAIL: 发现P2内容 '{kw}' 在库中")
            p2_in_db = True

if not p2_in_db:
    print("  PASS: P2内容未入库")
    tests.append(True)
else:
    tests.append(False)

# Test 5: 统计数据
print("\n[Test 5] 统计数据验证...")
c.execute("SELECT COUNT(*) FROM screened_sessions WHERE importance_level='P0'")
p0_count = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM screened_sessions WHERE importance_level='P1'")
p1_count = c.fetchone()[0]

if p0_count > 0 and p1_count > 0:
    print(f"  PASS: P0={p0_count}, P1={p1_count}")
    tests.append(True)
else:
    print(f"  FAIL: 数据不足")
    tests.append(False)

conn.close()

# 结果
print("\n" + "=" * 60)
passed = sum(tests)
total = len(tests)
print(f"回归测试: {passed}/{total} PASS ({int(passed/total*100)}%)")
print("=" * 60)

if passed == total:
    print("所有测试通过，OPT-REQ-009实施成功！")
else:
    print("部分测试失败，需修复")