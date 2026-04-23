# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import json
import time

print("=" * 60)
print("LangChain高评论PR爬取")
print("=" * 60)

# 找评论多的PR（尝试不同的筛选）
url = "https://api.github.com/repos/langchain-ai/langchain/pulls"
params = {"state": "closed", "per_page": 30, "sort": "updated"}

try:
    resp = requests.get(url, params=params, timeout=30)
    prs = resp.json()
    
    print(f"\n扫描 {len(prs)} 个已关闭PR...")
    
    total_comments = 0
    saved_data = []
    
    for pr in prs:
        pr_num = pr["number"]
        pr_title = pr["title"]
        comments_count = pr.get("comments", 0)
        review_comments = pr.get("review_comments", 0)
        
        total = comments_count + review_comments
        
        if total > 0:
            print(f"#{pr_num} ({total}条评论): {pr_title[:40]}")
            
            # 获取详细评论
            comments_url = f"https://api.github.com/repos/langchain-ai/langchain/pulls/{pr_num}/comments"
            try:
                c_resp = requests.get(comments_url, timeout=20)
                comments = c_resp.json()
                
                for c in comments:
                    body = c.get("body", "")
                    if len(body) > 100:
                        saved_data.append({
                            "source": f"langchain#{pr_num}",
                            "title": pr_title,
                            "content": body[:300],
                        })
                        total_comments += 1
                
                time.sleep(0.3)
                
            except:
                pass
    
    print(f"\n收集 {total_comments} 条有效评论")
    
    # 保存到文件
    if saved_data:
        output_path = r"C:\Users\Administrator\.openclaw\brain-system\data\langchain_pr_comments.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(saved_data, f, ensure_ascii=False, indent=2)
        print(f"保存到: {output_path}")
    
    print("=" * 60)

except Exception as e:
    print(f"错误: {e}")