#!/usr/bin/env python3
import json

with open('data/master/stocks_master.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

stock = d.get('002046', {})
print('Name:', stock.get('name'))
print('Code:', stock.get('code'))
print('Board:', stock.get('board'))
print('Industry:', stock.get('industry', 'EMPTY'))
print('Concepts count:', len(stock.get('concepts', [])))
print('Core business:', stock.get('core_business', []))
print('Industry position:', stock.get('industry_position', []))
print('Chain:', stock.get('chain', []))
print('Articles count:', len(stock.get('articles', [])))
print('\nArticles:')
for i, a in enumerate(stock.get('articles', [])):
    print(f"  {i+1}. title='{a.get('title', 'EMPTY')}', date='{a.get('date')}', source='{a.get('source', 'EMPTY')}'")
    print(f"     target_valuation={a.get('target_valuation', [])}")
