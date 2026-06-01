"""Fix stock-level first-tier fields from the latest article"""
import json
from pathlib import Path

master_path = Path('data/stocks/stocks_master.json')
with open(master_path, 'r', encoding='utf-8') as f:
    master = json.load(f)

stocks = master.get('stocks', {})

propagate_fields = ['core_business', 'industry_position', 'chain', 'partners']

# Also check the data file to see exact article 5 structure
with open('data/stocks/2026-06-01.json', 'r', encoding='utf-8') as f:
    shard = json.load(f)

updated = 0
for code, s in stocks.items():
    articles = s.get('articles', [])
    if not articles:
        continue
    
    needs_update = False
    
    # Look at ALL articles for field values
    for field in propagate_fields:
        stock_val = s.get(field)
        if not stock_val or (isinstance(stock_val, list) and len(stock_val) == 0):
            for a in reversed(articles):  # newest first
                article_val = a.get(field)
                if article_val and isinstance(article_val, list) and len(article_val) > 0:
                    # Check if not just empty strings
                    non_empty = [x for x in article_val if x.strip()]
                    if non_empty:
                        s[field] = article_val
                        needs_update = True
                        break
    
    if needs_update:
        updated += 1

# Also add concepts for 贝特瑞 (835185) if still missing
if '835185' in stocks and not stocks['835185'].get('concepts'):
    stocks['835185']['concepts'] = ['锂电池负极', '天然石墨', '人造石墨', '硅基负极', '固态电解质', '三元正极', '钠电池', '燃料电池']

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
    cb = stock.get('core_business', [])
    ip = stock.get('industry_position', [])
    ch = stock.get('chain', [])
    pt = stock.get('partners', [])
    co = stock.get('concepts', [])
    print(f"  {code} {stock.get('name','?')}: cb={len(cb)} ip={len(ip)} ch={len(ch)} pt={len(pt)} co={len(co)}")
    if cb: print(f"     core_business: {cb}")
    if ip: print(f"     industry_position: {ip}")
    if ch: print(f"     chain: {ch}")
    if pt: print(f"     partners: {pt}")
print(f"\nTotal: {len(s)} stocks")