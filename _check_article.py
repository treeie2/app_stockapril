import json
with open('data/stocks/stocks_master.json','r',encoding='utf-8') as f:
    master = json.load(f)
s = master['stocks']

# Check article fields for 603659 璞泰来
stock = s.get('603659', {})
print('=== 603659 璞泰来 stock fields ===')
for k,v in stock.items():
    if k != 'articles':
        val = v
        if isinstance(v, list):
            val = f'{len(v)} items' + (f': {v[:2]}' if v else '')
        print(f'  {k}: {val}')

print(f'\nArticles: {len(stock.get("articles",[]))}')
for i, a in enumerate(stock['articles']):
    print(f'\n--- Article {i} fields ---')
    for k,v in a.items():
        if isinstance(v, list):
            print(f'  {k} ({len(v)}): {v if len(v)<=2 else str(v[:2])+"..."}')
        else:
            print(f'  {k}: {v}')
    break  # just first article