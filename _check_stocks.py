import json
d = json.load(open('data/stocks/stocks_master.json','r',encoding='utf-8'))
s = d.get('stocks',{})
print(f'Total: {len(s)}')
codes = ['001269','002184','601702']
for c in codes:
    if c in s:
        stock = s[c]
        print(f'{c}: {stock.get("name","?")} (articles: {len(stock.get("articles",[]))}, updated: {stock.get("last_updated","")})')
    else:
        print(f'{c}: NOT FOUND')