import requests

# 测试detailed端点
r = requests.get('http://127.0.0.1:5002/feedback/detailed')
print("Status code:", r.status_code)
print("Response text:", r.text[:500] if r.text else "(empty)")