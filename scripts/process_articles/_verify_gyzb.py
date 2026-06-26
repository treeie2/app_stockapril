#!/usr/bin/env python3
"""Verify gyzb processing results"""
import json

# Check gyzb output
g = json.load(open(r'e:\github\stock-research-backup\temp11\gyzb_output.json', encoding='utf-8'))
g_stocks = g.get('stocks', {})

# Check master
m = json.load(open(r'e:\github\stock-research-backup\data\stocks\stocks_master.json', encoding='utf-8'))
m_stocks = m.get('stocks', {})

# Compare
gyzb_codes = set(g_stocks.keys())
master_codes = set(m_stocks.keys())
new_codes = gyzb_codes - master_codes
common_codes = gyzb_codes & master_codes

print(f'gyzb 独立JSON: {len(gyzb_codes)} 只股票')
print(f'stocks_master: {len(master_codes)} 只股票')
print(f'其中新股票(不在master中): {len(new_codes)} 只')

if new_codes:
    for c in sorted(list(new_codes))[:15]:
        print(f'  新: {c} -> {g_stocks[c]["name"]}')

# Check bad names in gyzb output
bad = [(c, s['name']) for c, s in g_stocks.items() if '\u25cb' in s.get('name','')]
print(f'\ngyzb输出中名称含○的: {len(bad)} 只')
for c, n in bad[:10]:
    print(f'  {c}: {n}')

# Check name quality
bad_names = [(c, s['name']) for c, s in g_stocks.items() 
             if not s['name'][0].isupper() and not '\u4e00' <= s['name'][0] <= '\u9fff']
print(f'\ngyzb输出中名称首字符非中文非英文的: {len(bad_names)} 只')
for c, n in bad_names[:10]:
    print(f'  {c}: {n!r}')

# Show common stocks with name check
mismatch = 0
for c in sorted(list(common_codes))[:10]:
    g_name = g_stocks[c]['name']
    m_name = m_stocks[c]['name']
    if g_name != m_name:
        print(f'  名称差异 {c}: gyzb={g_name!r}, master={m_name!r}')
        mismatch += 1
if mismatch == 0:
    print(f'\n前10个共有股票名称全部一致')