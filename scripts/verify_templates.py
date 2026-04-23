# -*- coding: utf-8 -*-
import requests

print("=" * 60)
print("Flow Templates Verification")
print("=" * 60)

test_cases = [
    ("测试系统功能", "test"),
    ("修复这个bug", "fix"),
    ("检查系统状态", "check"),
    ("部署到生产环境", "deploy"),
    ("重启服务", "restart"),
    ("清理临时文件", "clean"),
    ("优化性能", "optimize"),
    ("调试代码", "debug"),
    ("添加新功能", "add"),
    ("更新配置", "update"),
]

for content, expected_type in test_cases:
    r = requests.post('http://127.0.0.1:5002/entry', 
                      json={'content': content,
                            'sessionKey': 'template-test',
                            'senderId': 'tester'})
    
    result = r.json()
    intent = result.get('brain_context', {}).get('intent', {})
    detected_type = intent.get('type', 'unknown')
    flow_template = intent.get('flow_template', 'none')
    
    status = "OK" if detected_type == f"flow_{expected_type}" else "FAIL"
    print(f"\n{status} Input: '{content}'")
    print(f"   Expected: flow_{expected_type}")
    print(f"   Detected: {detected_type}")
    print(f"   Template: {flow_template}")

print("\n" + "=" * 60)
print("Verification Complete")
print("=" * 60)