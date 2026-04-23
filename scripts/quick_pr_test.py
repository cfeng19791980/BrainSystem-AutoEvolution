# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import json

print("=" * 60)
print("LangChain PR快速爬取测试")
print("=" * 60)

# 获取最近5个PR
url = "https://api.github.com/repos/langchain-ai/langchain/pulls"
params = {"state": "all", "per_page": 5}

try:
    resp = requests.get(url, params=params, timeout=30)
    prs = resp.json()
    
    print(f"\n获取 {len(prs)} 个PR:")
    
    for pr in prs:
        pr_num = pr["number"]
        pr_title = pr["title"]
        
        # 获取PR评论
        comments_url = f"https://api.github.com/repos/langchain-ai/langchain/pulls/{pr_num}/comments"
        c_resp = requests.get(comments_url, timeout=30)
        comments = c_resp.json()
        
        print(f"\n#{pr_num} {pr_title[:40]}")
        print(f"  评论数: {len(comments)}")
        
        if comments:
            # 显示第一条评论摘要
            first = comments[0]
            body = first.get("body", "")[:100]
            print(f"  示例: {body}...")
    
    print("\n" + "=" * 60)

except Exception as e:
    print(f"错误: {e}")