# -*- coding: utf-8 -*-
import requests

print("=" * 60)
print("Flow Template Injection Test")
print("=" * 60)

# 测试触发flow_template_check
test_input = "检查系统状态"

r = requests.post('http://127.0.0.1:5002/entry', 
                  json={'content': test_input,
                        'sessionKey': 'flow-test',
                        'senderId': 'tester'})

result = r.json()

print(f"\n输入: '{test_input}'")
print(f"\n[1] Intent Detection:")
intent = result.get('brain_context', {}).get('intent', {})
print(f"    Type: {intent.get('type')}")
print(f"    Confidence: {intent.get('confidence')}")
print(f"    Priority: {intent.get('priority')}")
print(f"    Reason: {intent.get('reason')}")
print(f"    Flow Template: {intent.get('flow_template')}")

print(f"\n[2] Template Injection Check:")
brain_ctx = result.get('brain_context', {})
if 'flow_template_content' in brain_ctx:
    print(f"    Template Injected: YES")
    print(f"    Content Preview: {brain_ctx['flow_template_content'][:100]}...")
else:
    print(f"    Template Injected: NO (file not found)")

print(f"\n[3] Vector Search:")
results = brain_ctx.get('results', [])
print(f"    Results Count: {len(results)}")
for i, res in enumerate(results[:3], 1):
    print(f"    #{i}: {res.get('source')} (score={res.get('score', 0):.3f})")

print(f"\n[4] Processed Content:")
print(f"    {result.get('processed_content', '')[:100]}")

print("\n" + "=" * 60)