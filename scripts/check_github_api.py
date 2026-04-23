# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import json

print("=" * 60)
print("GitHub API响应检查")
print("=" * 60)

url = "https://api.github.com/repos/langchain-ai/langchain/pulls"
params = {"state": "closed", "per_page": 5}

try:
    resp = requests.get(url, params=params, timeout=30)
    print(f"状态码: {resp.status_code}")
    
    data = resp.json()
    print(f"返回类型: {type(data)}")
    
    if isinstance(data, list):
        print(f"列表长度: {len(data)}")
        if data:
            print(f"第一项keys: {list(data[0].keys())[:10]}")
    else:
        print(f"返回内容: {str(data)[:200]}")
    
    print("=" * 60)

except Exception as e:
    print(f"错误: {e}")