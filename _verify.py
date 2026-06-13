#!/usr/bin/env python3
"""验证关键个股数据完整性"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/stocks/stocks_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"版本: {data['version']}")
print(f"股票: {len(data['stocks'])} 只")

# 关键个股检查
codes = ['688047', '688041', '002463', '002962', '300450', '000725']
for code in codes:
    s = data['stocks'].get(code, {})
    if not s:
        print(f"\n[{code}] ❌ 不在库中")
        continue
    name = s.get('name', '?')
    ip = s.get('industry_position', [])
    arts = s.get('articles', [])
    ib_count = sum(1 for a in arts if a.get('industry_background'))
    print(f"\n[{code}] {name}")
    print(f"  industry_position: {ip}")
    print(f"  articles: {len(arts)} (其中 {ib_count} 篇有 industry_background)")

# 全局统计
all_arts = []
for s in data['stocks'].values():
    all_arts.extend(s.get('articles', []))

with_ib = [a for a in all_arts if a.get('industry_background')]
with_ip = [s for s in data['stocks'].values() if s.get('industry_position')]
print(f"\n总计: {len(data['stocks'])} 只股票, {len(all_arts)} 篇文章")
print(f"有 industry_position: {len(with_ip)} 只")
print(f"有 industry_background: {len(with_ib)} 篇 ({len(with_ib)/len(all_arts)*100:.1f}%)")
