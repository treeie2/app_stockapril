import json, gzip, os

with open('data/stocks/stocks_master.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

with gzip.open('data/stocks/stocks_master.json.gz', 'wt', encoding='utf-8', compresslevel=9) as f:
    json.dump(d, f, ensure_ascii=False)

sz = os.path.getsize('data/stocks/stocks_master.json.gz')
print(f"gz: {sz/1024:.0f}KB, {len(d.get('stocks',{}))} stocks")
