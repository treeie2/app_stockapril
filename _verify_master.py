import json, sys
sys.stdout.reconfigure(encoding='utf-8')
try:
    d = json.load(open('data/stocks/stocks_master.json','r',encoding='utf-8'))
    stocks = d.get('stocks', {})
    print(f'OK: {len(stocks)} stocks, updated={d.get("updated_at","N/A")}')
    for code in ['001269','002184','601702']:
        s = stocks.get(code)
        if s:
            print(f'  {code} {s["name"]}: articles={len(s.get("articles",[]))}, last_updated={s.get("last_updated","")}')
        else:
            print(f'  {code}: MISSING')
except Exception as e:
    print(f'ERROR: {e}')
    with open('data/stocks/stocks_master.json','r',encoding='utf-8') as f:
        head = f.read(200)
    print(f'File starts with: {repr(head[:100])}')