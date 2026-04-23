# -*- coding: utf-8 -*-
import requests

BASE = "http://127.0.0.1:5002"

print("="*50)
print("Brain Entry Endpoints Check")
print("="*50)

endpoints = [
    "/health",
    "/entry",
    "/embedding/status",
    "/embedding/test",
    "/vector/search",
    "/patterns/ready",
]

for ep in endpoints:
    r = requests.get(f"{BASE}{ep}")
    print(f"  {ep}: {r.status_code} - {r.text[:50] if r.text else 'empty'}")