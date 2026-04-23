# -*- coding: utf-8 -*-
import requests
import time

print("Waiting for service...")
for i in range(30):
    try:
        r = requests.get('http://127.0.0.1:5002/health', timeout=2)
        if r.status_code == 200:
            print(f"Service ready after {i} seconds")
            break
    except:
        pass
    time.sleep(1)

print("\n=== Testing New Pattern APIs ===")

# 1. patterns/stats
r = requests.get('http://127.0.0.1:5002/patterns/stats')
print(f"\n1. /patterns/stats:")
print(f"   Status: {r.status_code}")
print(f"   Response: {r.json()}")

# 2. patterns/ready
r = requests.get('http://127.0.0.1:5002/patterns/ready')
print(f"\n2. /patterns/ready:")
print(f"   Status: {r.status_code}")
print(f"   Response: {r.json()}")

# 3. patterns/auto_execute
r = requests.post('http://127.0.0.1:5002/patterns/auto_execute')
print(f"\n3. /patterns/auto_execute:")
print(f"   Status: {r.status_code}")
print(f"   Response: {r.json()}")

# 4. patterns/activate
r = requests.post('http://127.0.0.1:5002/patterns/activate', 
                  json={'pattern_key': 'upgrade.filename_preserve'})
print(f"\n4. /patterns/activate:")
print(f"   Status: {r.status_code}")
print(f"   Response: {r.json()}")

print("\n=== Test Complete ===")