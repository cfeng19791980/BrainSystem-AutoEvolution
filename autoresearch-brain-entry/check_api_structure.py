# -*- coding: utf-8 -*-
"""检查API完整响应结构"""

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

# 打印所有key
print("Response keys:", list(result.keys()))

# 打印关键字段值
for key in ['type', 'intent', 'need_brain', 'priority']:
    print(f"{key}: {result.get(key, 'N/A')}")