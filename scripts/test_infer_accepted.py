# -*- coding: utf-8 -*-
import requests

# 测试隐式反馈推断
test_input = "好的，就这样。好像有个自动调用流程的功能没有被激活。先备份，在升级。"

print("=" * 50)
print("隐式反馈推断测试")
print("=" * 50)

r = requests.post('http://127.0.0.1:5002/feedback/infer', 
                  json={'user_input': test_input})

result = r.json()

print(f"\n用户输入: '{test_input[:30]}...'")
print(f"\n推断结果: {result['inferred_action']}")
print(f"解释: {result['explanation']}")

print("\n" + "=" * 50)