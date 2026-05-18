#!/usr/bin/env python3
"""
Fill missing first-layer fields in stocks_master.json.
Sources: stocks_master.min.json (board), code prefix derivation.
"""
import json
from pathlib import Path

BASE = Path(__file__).parent
MASTER = BASE / 'data' / 'stocks' / 'stocks_master.json'
MIN_MASTER = BASE / 'data' / 'stocks' / 'stocks_master.min.json'

def derive_board(code):
    c = code[0]
    if c == '6': return 'SH'
    if c in ('0','1','2','3'): return 'SZ'
    if c in ('8','9','4'): return 'BJ'
    return ''

with open(MASTER, 'r', encoding='utf-8') as f:
    master = json.load(f)
with open(MIN_MASTER, 'r', encoding='utf-8') as f:
    min_m = json.load(f)

min_lookup = {}
for code, s in min_m.get('stocks', {}).items():
    min_lookup[code] = s

first_layer = ['board','products','core_business','industry_position','chain','partners']
changes = []

for code, s in master['stocks'].items():
    name = s.get('name','')
    modified = False
    filled_fields = []

    for field in first_layer:
        if field not in s or not s.get(field):
            if code in min_lookup and field in min_lookup[code] and min_lookup[code][field]:
                s[field] = min_lookup[code][field]
            elif field == 'board':
                s[field] = derive_board(code)
            else:
                s[field] = []
            filled_fields.append(field)
            modified = True

    if modified:
        changes.append({'code': code, 'name': name, 'fields': filled_fields})

master['last_updated'] = '2026-05-18T16:20:00+08:00'
with open(MASTER, 'w', encoding='utf-8') as f:
    json.dump(master, f, ensure_ascii=False, indent=2)

print('Filled first-layer for %d stocks:\n' % len(changes))
for c in changes:
    print('  %s (%s): %s' % (c['name'], c['code'], ', '.join(c['fields'])))
print('\nTotal: %d stocks modified' % len(changes))
