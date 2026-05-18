#!/usr/bin/env python3
"""
补齐 stocks_master.json 中缺失的行业和概念信息。
数据来源：archived/同花顺行业.xls + 所属概念.xls
仅填充缺失字段，不修改已有数据。
"""
import json, pandas as pd
from pathlib import Path

BASE = Path(__file__).parent
MASTER = BASE / 'data' / 'stocks' / 'stocks_master.json'
IND_XLS = BASE / 'archived' / '同花顺行业.xls'
CON_XLS = BASE / 'archived' / '所属概念.xls'
BOARD_AS_IND = {'创业板','科创板','深市主板','沪市主板','北交所'}

# 1. Load master
with open(MASTER, 'r', encoding='utf-8') as f:
    master = json.load(f)
stocks = master.get('stocks', {})
print('Loaded %d stocks' % len(stocks))

# 2. Build lookup maps from Excel
ind_map = {}
for _, row in pd.read_excel(IND_XLS, sheet_name=0).iterrows():
    k = str(row['股票代码']).split('.')[0]
    v = str(row['所属同花顺行业']).strip()
    if v and v != 'nan': ind_map[k] = v

con_map = {}
for _, row in pd.read_excel(CON_XLS, sheet_name=0).iterrows():
    k = str(row['股票代码']).split('.')[0].strip()
    cs = str(row['所属概念']).strip()
    if cs and cs != 'nan':
        con_map[k] = [c.strip() for c in cs.split(';') if c.strip()]

print('Industry map: %d items' % len(ind_map))
print('Concept map:  %d items' % len(con_map))

# 3. Fill missing fields
filled_ind = filled_con = 0
for code, s in stocks.items():
    ind = s.get('industry', '')
    concepts = s.get('concepts', [])
    name = s.get('name', '')
    
    if (not ind or ind in BOARD_AS_IND) and code in ind_map:
        s['industry'] = ind_map[code]
        filled_ind += 1
        print('  [industry] %s (%s): %s -> %s' % (name, code, ind, s['industry']))
    
    if not concepts and code in con_map:
        s['concepts'] = con_map[code]
        filled_con += 1
        print('  [concepts] %s (%s): %d concepts added' % (name, code, len(s['concepts'])))

print()
print('Filled: %d industry, %d concepts' % (filled_ind, filled_con))
print('Remaining missing industry: %d' % sum(1 for s in stocks.values() if not s.get('industry','') or s['industry'] in BOARD_AS_IND))
print('Remaining missing concepts: %d' % sum(1 for s in stocks.values() if not s.get('concepts',[])))

# 4. Save
master['last_updated'] = '2026-05-18T16:00:00+08:00'
with open(MASTER, 'w', encoding='utf-8') as f:
    json.dump(master, f, ensure_ascii=False, indent=2)
print('Saved stocks_master.json')
