import json
d = json.load(open('data/stocks/stocks_master.json','r',encoding='utf-8'))
s = d.get('stocks',{})
for c in ['001269','601702']:
    if c in s:
        stock = s[c]
        print(f'=== {c} {stock.get("name","")} ===')
        print(f'  industry: {stock.get("industry","")}')
        print(f'  concepts: {stock.get("concepts",[])}')
        print(f'  products: {stock.get("products",[])}')
        print(f'  core_business: {stock.get("core_business",[])}')
        print(f'  industry_position: {stock.get("industry_position",[])}')
        print(f'  chain: {stock.get("chain",[])}')
        print(f'  partners: {stock.get("partners",[])}')
        for a in stock.get('articles', []):
            print(f'  article: {a.get("title","")[:40]} ({a.get("date","")}) source={a.get("source","")[:60]}')
        print()