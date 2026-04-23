# -*- coding: utf-8 -*-
import requests
import json
import sqlite3
from datetime import datetime
import sys
import io

# Set UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("BRAIN SYSTEM TRACE ANALYSIS")
print("=" * 60)

# 1. 模拟当前用户输入
test_input = "你是专业测试工程师，对系统进行模拟生成任务测试。比如我这条指令都触发了哪些逻辑，返回了什么结果，获得了哪些提升"

print(f"\n[输入内容]\n{test_input[:80]}...")

# 2. 调用Brain Entry API
r = requests.post('http://127.0.0.1:5002/entry', 
                  json={'content': test_input,
                        'sessionKey': 'trace-test',
                        'senderId': 'test-engineer'})

result = r.json()

print("\n" + "=" * 60)
print("[1] INPUT VALIDATION")
print("=" * 60)
print(f"Success: {result.get('success', False)}")
print(f"Processed: {result.get('processed_content', 'N/A')[:100]}")

if not result.get('success'):
    print(f"Error: {result.get('error', 'Unknown')}")
    print(f"Fallback: {result.get('fallback', False)}")
else:
    brain_ctx = result.get('brain_context', {})
    intent = brain_ctx.get('intent', {})
    
    print("\n" + "=" * 60)
    print("[2] INTENT DETECTION")
    print("=" * 60)
    print(f"Intent Type: {intent.get('type', 'N/A')}")
    print(f"Confidence: {intent.get('confidence', 0):.2f}")
    print(f"Priority: {intent.get('priority', 'N/A')}")
    print(f"Need Brain: {intent.get('need_brain', False)}")
    print(f"Reason: {intent.get('reason', 'N/A')}")
    print(f"Trigger Detected: {brain_ctx.get('trigger_detected', 'None')}")
    
    print("\n" + "=" * 60)
    print("[3] VECTOR SEARCH RESULTS")
    print("=" * 60)
    results = brain_ctx.get('results', [])
    print(f"Total Results: {len(results)}")
    
    for i, res in enumerate(results[:5], 1):
        print(f"\n  Result #{i}:")
        print(f"    Source: {res.get('source', 'N/A')}")
        print(f"    Score: {res.get('score', 0):.3f}")
        content_preview = res.get('content', '')[:60].encode('ascii', 'ignore').decode('ascii')
        print(f"    Content Preview: {content_preview}...")
    
    print("\n" + "=" * 60)
    print("[4] PROVIDER INFO")
    print("=" * 60)
    print(f"Embedding Provider: {brain_ctx.get('provider', 'N/A')}")
    print(f"Search Latency: {brain_ctx.get('latency_ms', 'N/A')}ms")

# 3. 查看Feedback记录
print("\n" + "=" * 60)
print("[5] FEEDBACK DATABASE")
print("=" * 60)

conn = sqlite3.connect('C:/Users/Administrator/.openclaw/brain-system/data/.brain_feedback.db')
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM feedback')
total = c.fetchone()[0]
print(f"Total Feedback Records: {total}")

c.execute('SELECT * FROM feedback ORDER BY id DESC LIMIT 5')
rows = c.fetchall()

print("\nRecent Feedback Records:")
for row in rows:
    print(f"  ID={row[0]}, Intent={row[4]}, Action={row[7]}, Time={row[10]}")

conn.close()

# 4. 统计分析
print("\n" + "=" * 60)
print("[6] STATISTICS ANALYSIS")
print("=" * 60)

r = requests.get('http://127.0.0.1:5002/feedback/stats')
stats = r.json()
print(f"Total Feedback: {stats['total_feedback']}")
print(f"Positive Rate: {stats['positive_rate']:.2%}")
print(f"Avg Results: {stats['avg_results']}")

r = requests.get('http://127.0.0.1:5002/feedback/detailed')
detailed = r.json()
print(f"\nBy Intent Type: {json.dumps(detailed['by_intent_type'], indent=4)}")

# 5. 优化建议
print("\n" + "=" * 60)
print("[7] OPTIMIZATION RECOMMENDATIONS")
print("=" * 60)

r = requests.get('http://127.0.0.1:5002/feedback/recommendations')
recs = r.json()
print(f"Generated At: {recs.get('generated_at', 'N/A')}")
print(f"Recommendations Count: {len(recs.get('recommendations', []))}")

for rec in recs.get('recommendations', []):
    print(f"\n  [{rec.get('priority', 'N/A')}] {rec.get('reason', 'N/A')}")

print("\n" + "=" * 60)
print("TRACE COMPLETE")
print("=" * 60)