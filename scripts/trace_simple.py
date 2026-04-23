# -*- coding: utf-8 -*-
import requests
import json
import sqlite3

# 模拟用户输入
test_input = "你是专业测试工程师，对系统进行模拟生成任务测试"

# 调用Brain Entry
r = requests.post('http://127.0.0.1:5002/entry', 
                  json={'content': test_input,
                        'sessionKey': 'trace-test',
                        'senderId': 'test-engineer'})

result = r.json()

print("=" * 50)
print("BRAIN SYSTEM TRACE")
print("=" * 50)

# 1. Input Validation
print(f"\n[1] INPUT VALIDATION")
print(f"    Success: {result.get('success')}")
print(f"    Processed: {result.get('processed_content', '')[:80]}")

if result.get('success'):
    brain_ctx = result.get('brain_context', {})
    intent = brain_ctx.get('intent', {})
    
    # 2. Intent Detection
    print(f"\n[2] INTENT DETECTION")
    print(f"    Type: {intent.get('type')}")
    print(f"    Confidence: {intent.get('confidence', 0):.2f}")
    print(f"    Priority: {intent.get('priority')}")
    print(f"    Need Brain: {intent.get('need_brain')}")
    
    # 3. Vector Results
    print(f"\n[3] VECTOR SEARCH")
    results = brain_ctx.get('results', [])
    print(f"    Total Results: {len(results)}")
    for i, res in enumerate(results[:3], 1):
        score = res.get('score', 0)
        source = res.get('source', 'N/A')
        print(f"    #{i}: {source} (score={score:.3f})")
    
    # 4. Provider
    print(f"\n[4] PROVIDER")
    print(f"    Embedding: {brain_ctx.get('provider')}")
    print(f"    Latency: {brain_ctx.get('latency_ms', 'N/A')}ms")

# 5. Feedback DB
print(f"\n[5] FEEDBACK DATABASE")
conn = sqlite3.connect('C:/Users/Administrator/.openclaw/brain-system/data/.brain_feedback.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM feedback')
total = c.fetchone()[0]
print(f"    Total Records: {total}")

c.execute('SELECT intent_type, user_action, timestamp FROM feedback ORDER BY id DESC LIMIT 3')
for row in c.fetchall():
    print(f"    Intent={row[0]}, Action={row[1]}, Time={row[2][:19]}")
conn.close()

# 6. Stats
print(f"\n[6] STATS")
r = requests.get('http://127.0.0.1:5002/feedback/stats')
stats = r.json()
print(f"    Total: {stats['total_feedback']}")
print(f"    Positive Rate: {stats['positive_rate']:.2%}")

# 7. Recommendations
print(f"\n[7] RECOMMENDATIONS")
r = requests.get('http://127.0.0.1:5002/feedback/recommendations')
recs = r.json()
print(f"    Count: {len(recs.get('recommendations', []))}")

print("\n" + "=" * 50)
print("TRACE COMPLETE")
print("=" * 50)