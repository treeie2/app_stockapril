#!/usr/bin/env python3
import json
from pathlib import Path

# Load master data
with open('data/master/stocks_master.json', 'r', encoding='utf-8') as f:
    master_data = json.load(f)

# Find 301085
for stock in master_data.get('stocks', []):
    if stock.get('code') == '301085':
        print('Stock 301085 in stocks_master.json:')
        print(f"  core_business: {stock.get('core_business')}")
        print(f"  products: {stock.get('products')}")
        print(f"  partners: {stock.get('partners')}")
        print(f"  chain: {stock.get('chain')}")
        print(f"  industry_position: {stock.get('industry_position')}")
        break
