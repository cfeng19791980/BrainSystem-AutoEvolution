# -*- coding: utf-8 -*-
"""
抓取 andreisiteru/awesome-reviewers README.md
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import time

url = "https://raw.githubusercontent.com/andreisiteru/awesome-reviewers/main/README.md"

print("抓取:", url)
print("=" * 60)

try:
    # 增加超时时间和重试
    session = requests.Session()
    session.max_redirects = 5
    
    for retry in range(3):
        print(f"尝试 {retry+1}/3...")
        try:
            resp = session.get(url, timeout=(10, 30), verify=True)
            print(f"状态码: {resp.status_code}")
            print(f"内容长度: {len(resp.text)} chars")
            
            if resp.status_code == 200:
                content = resp.text
                
                # 保存到文件
                with open(r"C:\Users\Administrator\.openclaw\brain-system\data\knowledge\AWESOME_REVIEWERS_ANDREISITERU.md", 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("\n内容预览 (前500 chars):")
                print(content[:500])
                print("\n" + "=" * 60)
                print("抓取成功！")
                break
            else:
                print(f"HTTP错误: {resp.status_code}")
                time.sleep(2)
        except requests.exceptions.Timeout:
            print("超时，重试...")
            time.sleep(3)
        except requests.exceptions.SSLError:
            print("SSL错误，尝试不验证...")
            resp = session.get(url, timeout=(10, 30), verify=False)
            if resp.status_code == 200:
                content = resp.text
                with open(r"C:\Users\Administrator\.openclaw\brain-system\data\knowledge\AWESOME_REVIEWERS_ANDREISITERU.md", 'w', encoding='utf-8') as f:
                    f.write(content)
                print("\n抓取成功（SSL跳过验证）")
                print(f"内容长度: {len(content)} chars")
                break
        except Exception as e:
            print(f"错误: {e}")
            time.sleep(3)
    
except Exception as e:
    print(f"最终错误: {e}")
    print("建议: 检查网络连接或代理设置")