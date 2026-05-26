import json

# 加载数据
master = json.load(open('data/stocks/stocks_master.json', 'r', encoding='utf-8'))['stocks']
raw = json.load(open('raw_material/stocks_from_raw_materials_complete_2026-04-23.json', 'r', encoding='utf-8'))['stocks']

# 获取股票代码
raw_codes = {s['code'] for s in raw if s.get('code')}
master_codes = set(master.keys())

print(f'raw_material 中的股票代码数：{len(raw_codes)}')
print(f'在 master 中已存在：{len(raw_codes & master_codes)}')
print(f'在 master 中缺失：{len(raw_codes - master_codes)}')

print('\n缺失的股票:')
missing = [s for s in raw if s.get('code') and s['code'] not in master_codes]
for s in missing:
    print(f'  - {s["code"]} {s["name"]}')

print(f'\n总共缺失：{len(missing)} 只')
