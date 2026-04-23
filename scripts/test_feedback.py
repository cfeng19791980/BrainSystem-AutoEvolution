import requests
import json

print("=== FeedbackManager API Tests ===\n")

# 1. 基础统计
r = requests.get('http://127.0.0.1:5002/feedback/stats')
print("1. /feedback/stats:")
print(json.dumps(r.json(), indent=2))

# 2. 详细统计
r = requests.get('http://127.0.0.1:5002/feedback/detailed')
print("\n2. /feedback/detailed:")
print(json.dumps(r.json(), indent=2))

# 3. 隐式反馈推断测试
test_cases = [
    "好的，就这样做",
    "不对，换一个方案",
    "改成 XXX 的方式",
    "下一个话题"
]
print("\n3. /feedback/infer tests:")
for tc in test_cases:
    r = requests.post('http://127.0.0.1:5002/feedback/infer', 
                      json={'user_input': tc})
    result = r.json()
    print(f"  '{tc}' -> {result['inferred_action']}")

# 4. 优化建议
r = requests.get('http://127.0.0.1:5002/feedback/recommendations')
print("\n4. /feedback/recommendations:")
print(json.dumps(r.json(), indent=2))

# 5. 模拟反馈记录
r = requests.post('http://127.0.0.1:5002/entry', 
                  json={'content': '测试feedback功能',
                        'sessionKey': 'test-session',
                        'senderId': 'test-user'})
print("\n5. Entry with feedback:")
result = r.json()
print(f"  Intent: {result['brain_context']['intent']['type']}")
print(f"  Success: {result['success']}")

print("\n=== All tests completed! ===")