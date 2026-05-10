# -*- coding: utf-8 -*-
import requests
import time

BASE_URL = "http://127.0.0.1:5002"

endpoints = [
    ("/health", "GET"),
    ("/embedding/test", "POST", {"text": "test"}),
    ("/patterns/ready", "GET"),
    ("/evolution/stats", "GET"),
    ("/dual-kb/stats", "GET"),
]

print("=" * 60)
print("Brain Entry API Check (10s wait)")
print("=" * 60)

time.sleep(10)  # Wait longer for service startup

for ep in endpoints:
    path = ep[0]
    method = ep[1]
    data = ep[2] if len(ep) > 2 else None
    
    try:
        if method == "GET":
            resp = requests.get(f"{BASE_URL}{path}", timeout=5)
        else:
            resp = requests.post(f"{BASE_URL}{path}", json=data, timeout=5)
        
        status = "PASS" if resp.status_code == 200 else f"FAIL ({resp.status_code})"
        print(f"  {path}: {status}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"    {str(result)[:80]}")
    except Exception as e:
        print(f"  {path}: ERROR ({str(e)[:40]})")

print("=" * 60)