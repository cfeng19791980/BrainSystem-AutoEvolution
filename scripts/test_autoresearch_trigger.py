# -*- coding: utf-8 -*-
import requests

print("="*60)
print("AutoResearch Template Trigger Test")
print("="*60)

# 测试触发
test_cases = [
    ("启动autoresearch优化代码", "autoresearch"),
    ("进行自主研究实验", "autoresearch"),
    ("overnight优化系统", "autoresearch"),
    ("运行AI实验循环", "autoresearch"),
]

for content, expected in test_cases:
    r = requests.post('http://127.0.0.1:5002/entry', 
                      json={'content': content,
                            'sessionKey': 'autoresearch-test',
                            'senderId': 'tester'})
    
    result = r.json()
    intent = result.get('brain_context', {}).get('intent', {})
    detected = intent.get('type', 'unknown')
    template = intent.get('flow_template', 'none')
    
    status = "OK" if detected == f"flow_{expected}" else "FAIL"
    print(f"\n{status} Input: '{content}'")
    print(f"   Expected: flow_{expected}")
    print(f"   Detected: {detected}")
    print(f"   Template: {template}")

print("\n" + "="*60)
print("AutoResearch Template Ready!")
print("="*60)
print("\nFiles created:")
print("  - brain-system/docs/AUTORESEARCH-ADAPTATION.md")
print("  - brain-system/scripts/autoresearch_simple.py")
print("  - brain-system/data/knowledge/flow_template_autoresearch.md")
print("\nSource:")
print("  - workspace-工程师/skills/autoresearch-karpathy/program.md")