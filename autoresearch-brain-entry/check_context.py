# -*- coding: utf-8 -*-
"""检查brain_context结构"""

import urllib.request
import json

data = json.dumps({'content': '检查系统状态'}).encode('utf-8')
req = urllib.request.Request(
    'http://127.0.0.1:5002/entry',
    data=data,
    headers={'Content-Type': 'application/json'}
)
response = urllib.request.urlopen(req, timeout=30)
result = json.loads(response.read().decode('utf-8'))

brain_context = result.get('brain_context', {})
print("brain_context keys:", list(brain_context.keys()))

# 检查intent位置
if 'intent' in brain_context:
    intent = brain_context['intent']
    print("intent type:", intent.get('type', 'N/A'))
elif 'intent_type' in brain_context:
    print("intent_type:", brain_context['intent_type'])
else:
    # 打印所有值
    for key, value in brain_context.items():
        if isinstance(value, dict):
            print(f"{key}: {value}")
        else:
            print(f"{key}: {value[:50] if isinstance(value, str) else value}")