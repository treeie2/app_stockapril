import json
import os

# 读取新数据
with open('data/stocks_master_2026-04-21.json', 'r', encoding='utf-8') as f:
    new_data = json.load(f)

# 读取主数据
with open('data/stocks/stocks_master.json', 'r', encoding='utf-8') as f:
    master = json.load(f)

# 添加五方光电
for stock in new_data['stocks']:
    code = stock['code']
    if code not in master['stocks']:
        master['stocks'][code] = stock
        print(f'新增股票: {code} {stock["name"]}')
    else:
        # 合并文章
        existing = master['stocks'][code]
        existing_articles = {a['source']: a for a in existing.get('articles', [])}
        for article in stock.get('articles', []):
            if article['source'] not in existing_articles:
                existing['articles'].append(article)
                existing['mention_count'] = len(existing['articles'])
                print(f'新增文章: {code} {article["title"]}')

# 保存
with open('data/stocks/stocks_master.json', 'w', encoding='utf-8') as f:
    json.dump(master, f, ensure_ascii=False, indent=2)

print('主数据已更新')