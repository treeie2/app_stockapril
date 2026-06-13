#!/usr/bin/env python3
"""Merge HarmonyOS 7.0 article into stocks_master.json"""
import json, sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
PROJECT_DIR = SKILL_DIR.parents[2]


def merge_harmony(today='2026-06-08'):
    """Merge HarmonyOS 7.0 article into stocks_master.json"""
    # 1. Merge into skill data/master using incremental_update
    print("=== Merging into skill data/master ===")
    sys.path.insert(0, str(SKILL_DIR / 'scripts'))
    from incremental_update import IncrementalUpdater

    updater = IncrementalUpdater()
    result = updater.merge_from_json(str(SKILL_DIR / 'data' / f'stocks_master_{today}_harmony.json'))
    print()

    # 2. Merge into project stocks_master.json
    print("=== Merging into project stocks_master.json ===")
    master_path = PROJECT_DIR / 'data' / 'stocks' / 'stocks_master.json'
    master = json.loads(master_path.read_text(encoding='utf-8'))
    stocks = master.get('stocks', {})

    harmony_path = SKILL_DIR / 'data' / f'stocks_master_{today}_harmony.json'
    harmony_data = json.loads(harmony_path.read_text(encoding='utf-8'))
    harmony_stocks = harmony_data.get('stocks', [])

    new_count = 0
    update_count = 0
    for new_stock in harmony_stocks:
        code = new_stock['code']
        if code in stocks:
            existing = stocks[code]
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
    print(f"\n[OK] Master merged: {new_count} new, {update_count} updated, {len(stocks)} total")

    # Also update today's daily shard
    today_path = PROJECT_DIR / 'data' / 'stocks' / f'{today}.json'
    if today_path.exists():
        today_data = json.loads(today_path.read_text(encoding='utf-8'))
        today_stocks = today_data.get('stocks', {})
        for new_stock in harmony_stocks:
            code = new_stock['code']
            if code in today_stocks:
                existing = today_stocks[code]
                existing_articles = existing.get('articles', [])
                existing_keys = {(a['title'], a['source']) for a in existing_articles}
                for a in new_stock.get('articles', []):
                    key = (a['title'], a['source'])
                    if key not in existing_keys:
                        existing_articles.append(a)
                existing['articles'] = existing_articles
                existing['mention_count'] = len(existing_articles)
                for field in ['concepts', 'products', 'core_business', 'industry_position', 'chain', 'partners']:
                    if new_stock.get(field):
                        existing_set = set(existing.get(field, []))
                        existing_set.update(new_stock[field])
                        existing[field] = list(existing_set)
                today_stocks[code] = existing
            else:
                today_stocks[code] = new_stock
        today_data['stocks'] = today_stocks
        today_data['update_count'] = len(today_stocks)
        today_path.write_text(json.dumps(today_data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"[OK] Daily shard {today}.json updated ({len(today_stocks)} stocks)")


if __name__ == '__main__':
    merge_harmony()