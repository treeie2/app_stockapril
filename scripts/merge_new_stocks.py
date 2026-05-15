import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# 1. 读取新数据
with open(BASE_DIR / 'data' / 'stocks_master_2026-05-15.json', 'r', encoding='utf-8') as f:
    new_data = json.load(f)
new_stocks_list = new_data.get('stocks', [])
new_stocks_dict = {s['code']: s for s in new_stocks_list if 'code' in s}
print(f'新数据: {len(new_stocks_list)} 只股票')
for code, s in new_stocks_dict.items():
    articles = s.get('articles', [])
    tv = articles[0].get('target_valuation', 'N/A') if articles else '无'
    print(f'  {code} {s["name"]}: {len(articles)} 篇文章, tv={tv}')

# 2. 读取主文件
master_path = BASE_DIR / 'data' / 'stocks' / 'stocks_master.json'
with open(master_path, 'r', encoding='utf-8') as f:
    master = json.load(f)
master_stocks = master.get('stocks', {})
print(f'\n主文件: {len(master_stocks)} 只股票')

# 3. 合并新数据到主文件
for code, new_s in new_stocks_dict.items():
    if code in master_stocks:
        old_articles = master_stocks[code].get('articles', [])
        new_articles = new_s.get('articles', [])
        existing_sources = {a.get('source', '') for a in old_articles}
        merged = False
        for a in new_articles:
            if a.get('source', '') not in existing_sources:
                old_articles.append(a)
                existing_sources.add(a.get('source', ''))
                merged = True
        if merged:
            master_stocks[code]['articles'] = old_articles
            master_stocks[code]['mention_count'] = len(old_articles)
            print(f'  + {code} {new_s["name"]}: 合并了 {len(new_articles)} 篇新文章')
        else:
            print(f'  = {code} {new_s["name"]}: 无新文章需要合并')
    else:
        master_stocks[code] = new_s
        print(f'  + {code} {new_s["name"]}: 新增股票')

# 4. 保存主文件
master['stocks'] = master_stocks
with open(master_path, 'w', encoding='utf-8') as f:
    json.dump(master, f, ensure_ascii=False, indent=2)
print(f'\n主文件已更新: {master_path}')

# 5. 更新分片文件 data/stocks/2026-05-15.json
shard_path = BASE_DIR / 'data' / 'stocks' / '2026-05-15.json'
if shard_path.exists():
    with open(shard_path, 'r', encoding='utf-8') as f:
        shard = json.load(f)
else:
    shard = {'date': '2026-05-15', 'update_count': 0, 'stocks': {}}

shard_stocks = shard.get('stocks', {})
for code, new_s in new_stocks_dict.items():
    if code in shard_stocks:
        old_articles = shard_stocks[code].get('articles', [])
        new_articles = new_s.get('articles', [])
        existing_sources = {a.get('source', '') for a in old_articles}
        for a in new_articles:
            if a.get('source', '') not in existing_sources:
                old_articles.append(a)
        shard_stocks[code]['articles'] = old_articles
        shard_stocks[code]['mention_count'] = len(old_articles)
    else:
        shard_stocks[code] = new_s

shard['stocks'] = shard_stocks
shard['update_count'] = len(shard_stocks)
with open(shard_path, 'w', encoding='utf-8') as f:
    json.dump(shard, f, ensure_ascii=False, indent=2)
print(f'分片文件已更新: {shard_path} ({len(shard_stocks)} 只)')

# 6. 验证
with open(master_path, 'r', encoding='utf-8') as f:
    verify = json.load(f)
s = verify.get('stocks', {}).get('002254', {})
articles = s.get('articles', [])
print(f'\n验证 002254 泰和新材: {len(articles)} 篇文章')
for a in articles:
    print(f'  - {a.get("title")}: tv={a.get("target_valuation", [])}')