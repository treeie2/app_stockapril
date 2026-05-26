import json

data = json.load(open('data/stocks/stocks_master.json', 'r', encoding='utf-8'))
stocks = data['stocks']
code = '300658'
s = stocks[code]

print(f'{code} {s.get("name")} 的第一层信息:')
print(f'  产品：{s.get("products", [])}')
print(f'  核心业务：{s.get("core_business", [])}')
print(f'  行业地位：{s.get("industry_position", [])}')
print(f'  产业链：{s.get("chain", [])}')
print(f'  合作伙伴：{s.get("partners", [])}')
