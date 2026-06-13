"""从 stocks_master (1).json 恢复 target_valuation（按 title 匹配）"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('stocks_master (1).json', 'r', encoding='utf-8') as f:
    old = json.load(f)

with open('data/stocks/stocks_master.json', 'r', encoding='utf-8') as f:
    cur = json.load(f)

# 构建旧版 title -> target_valuation 映射
old_tv = {}
for code, s in old['stocks'].items():
    for a in s.get('articles', []):
        title = a.get('title', '').strip()
        tv = a.get('target_valuation', [])
        if title and tv:
            old_tv[title] = tv

print(f"旧版有 {len(old_tv)} 个 titl埋 有 target_valuation")

# 恢复
stats = {'replaced': 0, 'merged': 0, 'skipped': 0}
for code, s in cur['stocks'].items():
    for a in s.get('articles', []):
        title = a.get('title', '').strip()
        if title in old_tv:
            old_val = old_tv[title]
            cur_val = a.get('target_valuation', [])
            if not cur_val:
                # 当前为空 → 直接用旧版
                a['target_valuation'] = old_val
                stats['replaced'] += 1
            elif sorted(str(x) for x in cur_val) != sorted(str(x) for x in old_val):
                # 不同 → 合并去重
                merged = list(dict.fromkeys(old_val + cur_val))
                a['target_valuation'] = merged
                stats['merged'] += 1
            else:
                stats['skipped'] += 1

print(f"恢复: {stats['replaced']} 篇, 合并: {stats['merged']} 篇, 跳过: {stats['skipped']} 篇")

with open('data/stocks/stocks_master.json', 'w', encoding='utf-8') as f:
    json.dump(cur, f, ensure_ascii=False, indent=2)

import gzip, os
with open('data/stocks/stocks_master.json', 'rb') as src:
    with gzip.open('data/stocks/stocks_master.json.gz', 'wb', 9) as dst:
        dst.write(src.read())
print(f"已保存, .gz: {os.path.getsize('data/stocks/stocks_master.json.gz')//1024} KB")
