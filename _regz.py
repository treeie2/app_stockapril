import json, gzip

with open('data/stocks/stocks_master.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

stocks = d.get('stocks', {})
print(f"原始: {len(stocks)} stocks, updated_at={d.get('updated_at','?')}")

with gzip.open('data/stocks/stocks_master.json.gz', 'wt', encoding='utf-8', compresslevel=9) as f:
    json.dump(d, f, ensure_ascii=False)

import os
sz = os.path.getsize('data/stocks/stocks_master.json.gz')
print(f"gz: {sz/1024:.0f}KB")

# verify
with gzip.open('data/stocks/stocks_master.json.gz', 'rt', encoding='utf-8') as f:
    v = json.load(f)
print(f"验证: {len(v.get('stocks',{}))} stocks")
