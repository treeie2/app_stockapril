import json

# 读取主数据
with open('data/stocks/stocks_master.json', 'r', encoding='utf-8') as f:
    master = json.load(f)

# 读取今日数据
with open('data/stocks/2026-05-13.json', 'r', encoding='utf-8') as f:
    daily = json.load(f)

# 合并
for code, stock_data in daily['stocks'].items():
    if code in master['stocks']:
        # 追加文章（去重）
        existing = master['stocks'][code]
        titles = [(a['title'], a['source']) for a in existing.get('articles',[])]
        for article in stock_data.get('articles',[]):
            if (article['title'], article['source']) not in titles:
                existing.setdefault('articles',[]).append(article)
        # 更新计数
        existing['mention_count'] = len(existing['articles'])
        existing['last_updated'] = daily['date']
        # 更新产品和概念
        if stock_data.get('products'):
            existing_products = set(existing.get('products', []))
            existing_products.update(stock_data['products'])
            existing['products'] = list(existing_products)
        if stock_data.get('concepts'):
            existing_concepts = set(existing.get('concepts', []))
            existing_concepts.update(stock_data['concepts'])
            existing['concepts'] = list(existing_concepts)
    else:
        # 新股票
        stock_data['last_updated'] = daily['date']
        master['stocks'][code] = stock_data

# 更新时间
master['last_updated'] = daily['last_updated']

# 保存
json.dump(master, open('data/stocks/stocks_master.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'✅ 合并完成：{len(daily["stocks"])} 只股票')
print(f'📊 {list(daily["stocks"].values())[0]["name"]} 当前提及次数：{master["stocks"][list(daily["stocks"].keys())[0]]["mention_count"]}')
