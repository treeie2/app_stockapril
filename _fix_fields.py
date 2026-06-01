"""Fix stock-level first-tier fields from article data"""
import json
from pathlib import Path

master_path = Path('data/stocks/stocks_master.json')
with open(master_path, 'r', encoding='utf-8') as f:
    master = json.load(f)

stocks = master.get('stocks', {})

# Fields to propagate: use first article's value if stock-level missing
propagate_fields = ['core_business', 'industry_position', 'chain', 'partners']

updated = 0
for code, s in stocks.items():
    articles = s.get('articles', [])
    if not articles:
        continue
    
    needs_update = False
    first_article = articles[0]
    
    for field in propagate_fields:
        stock_val = s.get(field)
        # Check if stock-level is missing/empty
        if not stock_val or (isinstance(stock_val, list) and len(stock_val) == 0):
            article_val = first_article.get(field)
            if article_val and (isinstance(article_val, list) and len(article_val) > 0):
                s[field] = article_val
                needs_update = True
    
    if needs_update:
        updated += 1

# Also add concepts for 贝特瑞 (835185) if missing
if '835185' in stocks and not stocks['835185'].get('concepts'):
    stocks['835185']['concepts'] = ['锂电池负极', '天然石墨', '人造石墨', '硅基负极', '固态电解质', '三元正极', '钠电池', '燃料电池']

# Fix last_updated
today = '2026-06-01'
for code in ['603659','600884','300890','835185','300035','001301']:
    if code in stocks:
        stocks[code]['last_updated'] = today

master['stocks'] = stocks
with open(master_path, 'w', encoding='utf-8') as f:
    json.dump(master, f, ensure_ascii=False, indent=2)

print(f"Updated {updated} stocks with propagated fields")

# Verify
with open(master_path, 'r', encoding='utf-8') as f:
    verify = json.load(f)
s = verify['stocks']

for code in ['603659','600884','300890','835185','300035','001301']:
    stock = s.get(code, {})
    has_cb = bool(stock.get('core_business'))
    has_ip = bool(stock.get('industry_position'))
    has_ch = bool(stock.get('chain'))
    has_pt = bool(stock.get('partners'))
    has_co = bool(stock.get('concepts'))
    print(f"  {code} {stock.get('name','?')}: cb={has_cb} ip={has_ip} ch={has_ch} pt={has_pt} co={has_co}")
print(f"\nTotal: {len(s)} stocks")