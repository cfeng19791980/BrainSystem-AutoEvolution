# -*- coding: utf-8 -*-
import requests
import time

BASE_URL = "http://127.0.0.1:5002"

print("=" * 60)
print("Final API Validation")
print("=" * 60)

time.sleep(12)  # Wait for service

endpoints = [
    ("/dual-kb/stats", "GET"),
    ("/patterns/ready", "GET"),
    ("/health", "GET"),
]

for path, method in endpoints:
    try:
        if method == "GET":
            resp = requests.get(f"{BASE_URL}{path}", timeout=5)
        
        status = "PASS" if resp.status_code == 200 else f"FAIL ({resp.status_code})"
        result = resp.json()
        print(f"\n{path}: {status}")
        print(f"  {result}")
    except Exception as e:
        print(f"\n{path}: ERROR - {str(e)[:50]}")

print("\n" + "=" * 60)