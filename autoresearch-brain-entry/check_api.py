# -*- coding: utf-8 -*-
"""检查API响应格式"""

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

# 打印关键信息
print("intent type:", result.get('intent', {}).get('type', 'N/A'))
print("intent reason:", result.get('intent', {}).get('reason', 'N/A'))
print("response preview:", result.get('response', '')[:100])