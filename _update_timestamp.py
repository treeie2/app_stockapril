import json
from datetime import date

today_str = date.today().isoformat()
path = 'data/stocks/stocks_master.json'

d = json.load(open(path, 'r', encoding='utf-8'))
d['updated_at'] = today_str
d['stock_count'] = len(d.get('stocks', {}))

with open(path, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print(f'✅ Updated at top-level: {d["updated_at"]}, total stocks: {d["stock_count"]}')

# Verify
d2 = json.load(open(path, 'r', encoding='utf-8'))
for code in ['001269','002184','601702']:
    s = d2['stocks'].get(code)
    if s:
        print(f'  {code} {s["name"]}: articles={len(s.get("articles",[]))}, updated={s.get("last_updated","")}')
    else:
        print(f'  {code}: MISSING')