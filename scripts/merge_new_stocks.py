import json
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
today_str = date.today().isoformat()

# 1. 读取新数据（支持 stocks 为 dict 或 list 格式）
new_data_path = BASE_DIR / 'data' / f'stocks_master_{today_str}.json'
if not new_data_path.exists():
    print(f'❌ 未找到新数据文件: {new_data_path}')
    exit(1)

with open(new_data_path, 'r', encoding='utf-8') as f:
    new_data = json.load(f)

raw_stocks = new_data.get('stocks', {})

if isinstance(raw_stocks, dict):
    new_stocks_dict = raw_stocks
elif isinstance(raw_stocks, list):
    new_stocks_dict = {s['code']: s for s in raw_stocks if 'code' in s}
else:
    new_stocks_dict = {}

print(f'{today_str} 新数据: {len(new_stocks_dict)} 只股票')
for code, s in new_stocks_dict.items():
    articles = s.get('articles', [])
    n_arts = len(articles)
    tv = articles[0].get('target_valuation', 'N/A') if articles else '无'
    print(f'  {code} {s["name"]}: {n_arts} 篇文章, tv={tv}')

# 2. 读取主文件
master_path = BASE_DIR / 'data' / 'stocks' / 'stocks_master.json'
with open(master_path, 'r', encoding='utf-8') as f:
    master = json.load(f)
master_stocks = master.get('stocks', {})
print(f'\n主文件: {len(master_stocks)} 只股票')

# 3. 合并新数据到主文件
new_count = 0
updated_count = 0
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
            master_stocks[code]['last_updated'] = today_str
            
            # 合并其他列表字段
            for field in ['core_business', 'industry_position', 'chain', 'partners', 'concepts', 'products']:
                if field in new_s and new_s[field]:
                    existing_set = set(master_stocks[code].get(field, []))
                    for item in new_s[field]:
                        if item not in existing_set:
                            master_stocks[code].setdefault(field, []).append(item)
                            existing_set.add(item)
            
            updated_count += 1
            print(f'  ✅ {code} {new_s["name"]}: 合并了文章 + 字段更新')
        else:
            print(f'  = {code} {new_s["name"]}: 无新内容需要合并')
    else:
        # 新股票
        new_s['last_updated'] = today_str
        if 'mention_count' not in new_s:
            new_s['mention_count'] = len(new_s.get('articles', []))
        master_stocks[code] = new_s
        new_count += 1
        print(f'  🆕 {code} {new_s["name"]}: 新增股票')

# 4. 保存主文件
master['stocks'] = master_stocks
master['updated_at'] = today_str
with open(master_path, 'w', encoding='utf-8') as f:
    json.dump(master, f, ensure_ascii=False, indent=2)
print(f'\n主文件已更新: {master_path}')
print(f'  新增: {new_count} 只, 更新: {updated_count} 只')

# 5. 更新分片文件
shard_path = BASE_DIR / 'data' / 'stocks' / f'{today_str}.json'
if shard_path.exists():
    with open(shard_path, 'r', encoding='utf-8') as f:
        shard = json.load(f)
else:
    shard = {'date': today_str, 'update_count': 0, 'last_updated': '', 'stocks': {}}

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
        shard_stocks[code]['last_updated'] = today_str
    else:
        merged_s = dict(new_s)
        merged_s['last_updated'] = today_str
        if 'mention_count' not in merged_s:
            merged_s['mention_count'] = len(merged_s.get('articles', []))
        shard_stocks[code] = merged_s

shard['stocks'] = shard_stocks
shard['update_count'] = len(shard_stocks)
shard['last_updated'] = today_str
with open(shard_path, 'w', encoding='utf-8') as f:
    json.dump(shard, f, ensure_ascii=False, indent=2)
print(f'分片文件已更新: {shard_path} ({len(shard_stocks)} 只)')

# 6. 验证摘要
print(f'\n{"="*50}')
print(f'合并完成！')
print(f'  新增股票: {new_count}')
print(f'  更新股票: {updated_count}')
print(f'  总计: {len(master_stocks)} 只')
print(f'{"="*50}')