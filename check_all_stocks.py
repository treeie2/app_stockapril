#!/usr/bin/env python3
import json

with open('data/master/stocks_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

stocks = data.get('stocks', [])

# Count stocks with each field
core_biz = sum(1 for s in stocks if s.get('core_business'))
products = sum(1 for s in stocks if s.get('products'))
partners = sum(1 for s in stocks if s.get('partners'))
chain = sum(1 for s in stocks if s.get('chain'))
ind_pos = sum(1 for s in stocks if s.get('industry_position'))

print('Stocks with data in stocks_master.json:')
print(f'  core_business: {core_biz}')
print(f'  products: {products}')
print(f'  partners: {partners}')
print(f'  chain: {chain}')
print(f'  industry_position: {ind_pos}')

# Show a few examples
print('\nSample stocks with complete data:')
count = 0
for s in stocks:
    if s.get('core_business') and s.get('products') and s.get('partners'):
        print(f"  {s['code']} {s['name']}")
        count += 1
        if count >= 10:
            break

print(f'\nTotal stocks: {len(stocks)}')
