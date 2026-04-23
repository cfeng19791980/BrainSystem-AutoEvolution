# -*- coding: utf-8 -*-
"""
PR评论批量爬取 - 喂养Brain系统
目标: langchain-ai/langchain (与BrainSystem最相关)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json
import time
import sqlite3
import os
import re
from datetime import datetime

print("=" * 60)
print("PR评论爬取 - 喂养Brain系统")
print("=" * 60)

# GitHub API (无需token可爬取，但有限速)
GITHUB_API = "https://api.github.com"
TARGET_REPOS = [
    ("langchain-ai", "langchain", 30),  # 30个PR
    ("pytorch", "pytorch", 20),         # 20个PR
    ("microsoft", "vscode", 20),        # 20个PR
]

# 数据库路径
DB_PATH = r"C:\Users\Administrator\.openclaw\brain-system\data\.brain_vectors.db"

def fetch_pr_comments(owner, repo, pr_limit=30):
    """爬取PR评论"""
    print(f"\n爬取 {owner}/{repo}...")
    
    # 获取PR列表
    pr_url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls?state=all&per_page={pr_limit}"
    
    try:
        resp = requests.get(pr_url, timeout=30)
        if resp.status_code != 200:
            print(f"  错误: {resp.status_code}")
            return []
        
        prs = resp.json()
        print(f"  获取 {len(prs)} 个PR")
        
        comments_data = []
        
        for pr in prs[:pr_limit]:
            pr_number = pr["number"]
            pr_title = pr["title"]
            pr_state = pr["state"]
            
            # 获取PR评论
            comments_url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
            
            try:
                c_resp = requests.get(comments_url, timeout=30)
                if c_resp.status_code == 200:
                    comments = c_resp.json()
                    
                    if len(comments) > 0:
                        print(f"  PR #{pr_number} ({pr_state}): {len(comments)}条评论")
                        
                        for c in comments:
                            body = c.get("body", "")
                            if body and len(body) > 50:  # 过滤短评论
                                # 提取知识点
                                pattern = extract_pattern(body, pr_title)
                                if pattern:
                                    comments_data.append({
                                        "source": f"{owner}/{repo}#{pr_number}",
                                        "title": pr_title,
                                        "content": body[:500],  # 截断
                                        "pattern": pattern,
                                        "created_at": c.get("created_at", ""),
                                    })
                
                time.sleep(0.5)  # 限速
                
            except Exception as e:
                print(f"  PR #{pr_number} 评论获取失败: {e}")
        
        return comments_data
        
    except Exception as e:
        print(f"  爬取失败: {e}")
        return []

def extract_pattern(body, title):
    """从PR评论提取Pattern"""
    patterns = []
    
    # 工程约束Pattern
    if re.search(r"should|must|require|need|avoid|don't", body.lower()):
        patterns.append("constraint")
    
    # 性能优化Pattern
    if re.search(r"performance|slow|fast|optimize|cache|memory", body.lower()):
        patterns.append("performance")
    
    # API设计Pattern
    if re.search(r"API|interface|method|parameter|return|type", body.lower()):
        patterns.append("api_design")
    
    # 错误处理Pattern
    if re.search(r"error|exception|fail|handle|catch|throw", body.lower()):
        patterns.append("error_handling")
    
    # 安全Pattern
    if re.search(r"security|vulnerability|exploit|sanitize|validate", body.lower()):
        patterns.append("security")
    
    # 测试Pattern
    if re.search(r"test|unit|integration|coverage|mock", body.lower()):
        patterns.append("testing")
    
    return patterns[0] if patterns else None

def save_to_kb(data):
    """保存到知识库"""
    print(f"\n保存到知识库...")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 创建表（如果不存在）
    c.execute('''CREATE TABLE IF NOT EXISTS pr_knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        title TEXT,
        content TEXT,
        pattern TEXT,
        created_at TEXT,
        imported_at TEXT,
        vectorized INTEGER DEFAULT 0
    )''')
    
    count = 0
    for item in data:
        try:
            c.execute('''INSERT INTO pr_knowledge 
                (source, title, content, pattern, created_at, imported_at)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (item["source"], item["title"], item["content"], 
                 item["pattern"], item["created_at"], datetime.now().isoformat()))
            count += 1
        except Exception as e:
            print(f"  插入失败: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"  保存 {count} 条知识")
    return count

# 主流程
total_comments = 0

for owner, repo, limit in TARGET_REPOS:
    comments = fetch_pr_comments(owner, repo, limit)
    if comments:
        saved = save_to_kb(comments)
        total_comments += saved
    time.sleep(2)  # 项目间隔

print("\n" + "=" * 60)
print(f"爬取完成: {total_comments}条PR评论入库")
print("=" * 60)

# 统计Pattern分布
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT pattern, COUNT(*) FROM pr_knowledge GROUP BY pattern")
patterns = c.fetchall()
print("\nPattern分布:")
for p, cnt in patterns:
    print(f"  {p}: {cnt}条")

conn.close()

print("\n下一步:")
print("  1. 运行向量导入脚本")
print("  2. brain_entry.py自动匹配新知识")
print("  3. 观察进化效果")
print("=" * 60)