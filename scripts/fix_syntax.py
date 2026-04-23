# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\Administrator\.openclaw\brain-system\core\brain_entry.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到并修复问题行
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'rule_id = f' in line and 'keyword.replace' in line:
        # 修复这一行
        lines[i] = '            rule_id = f\'rule_{keyword.replace(" ", "_")}\''
        print(f'Fixed line {i+1}')

content = '\n'.join(lines)

with open(r'C:\Users\Administrator\.openclaw\brain-system\core\brain_entry.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Syntax fixed')