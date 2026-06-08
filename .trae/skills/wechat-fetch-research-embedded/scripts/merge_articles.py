#!/usr/bin/env python3
"""Merge the three articles into project stocks_master.json and skill data/master"""
import json
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
PROJECT_DIR = SKILL_DIR.parents[2]

today = '2026-06-08'

# 1. Merge into skill data/master using incremental_update
print("=== Merging into skill data/master ===")
import sys
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from incremental_update import IncrementalUpdater

updater = IncrementalUpdater()
result = updater.merge_from_json(str(SKILL_DIR / 'data' / f'stocks_master_{today}.json'))
print()

# 2. Merge into project root stocks_master.json
print("=== Merging into project stocks_master.json ===")
master_path = PROJECT_DIR / 'data' / 'stocks' / 'stocks_master.json'
master = json.loads(master_path.read_text(encoding='utf-8'))
stocks = master.get('stocks', {})

# Read today's data
today_path = PROJECT_DIR / 'data' / 'stocks' / f'{today}.json'
today_data = json.loads(today_path.read_text(encoding='utf-8'))
today_stocks = today_data.get('stocks', {})

new_count = 0
update_count = 0
for code, new_stock in today_stocks.items():
    if code in stocks:
        existing = stocks[code]
        # Merge articles (dedup by title+source)
        existing_articles = existing.get('articles', [])
        existing_keys = {(a['title'], a['source']) for a in existing_articles}
        for a in new_stock.get('articles', []):
            key = (a['title'], a['source'])
            if key not in existing_keys:
                existing_articles.append(a)
                existing_keys.add(key)
        existing['articles'] = existing_articles
        existing['mention_count'] = len(existing_articles)
        existing['last_updated'] = today
        
        # Merge other list fields
        for field in ['concepts', 'products', 'core_business', 'industry_position', 'chain', 'partners']:
            if new_stock.get(field):
                existing_set = set(existing.get(field, []))
                new_set = set(new_stock[field])
                combined = list(existing_set | new_set)
                existing[field] = combined
        
        stocks[code] = existing
        update_count += 1
        print(f"  Updated: {code} {existing['name']} (total {len(existing_articles)} articles)")
    else:
        stocks[code] = new_stock
        new_count += 1
        print(f"  New: {code} {new_stock['name']}")

master['stocks'] = stocks
master['last_updated'] = today
master['total_stocks'] = len(stocks)

master_path.write_text(json.dumps(master, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"\n✅ Master merged: {new_count} new, {update_count} updated, {len(stocks)} total")
print(f"   File: {master_path}")