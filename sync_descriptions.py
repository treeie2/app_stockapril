#!/usr/bin/env python3
"""
Sync descriptions from SQLite to stocks_master.json
"""
import json
import sqlite3
from pathlib import Path

# Paths
MASTER_FILE = Path(__file__).parent / 'data' / 'master' / 'stocks_master.json'
DB_FILE = Path(__file__).parent / 'data' / 'stock_research.db'

def sync_descriptions():
    print("🔄 Syncing descriptions from SQLite to stocks_master.json...")
    
    # Load master data
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    master_stocks = master_data.get('stocks', [])
    
    # Connect to SQLite
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all stocks with descriptions from SQLite
    cursor.execute('''
        SELECT code, name, description 
        FROM stocks 
        WHERE description IS NOT NULL 
        AND description != ''
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    print(f"Found {len(rows)} stocks with descriptions in SQLite")
    
    # Create code-to-stock mapping for faster lookup
    stock_map = {s.get('code'): s for s in master_stocks}
    
    updated_count = 0
    for row in rows:
        code = row['code']
        description = row['description']
        
        if code in stock_map and description:
            stock = stock_map[code]
            # Set description field
            stock['description'] = description
            
            # Also ensure it's in core_business
            if 'core_business' not in stock:
                stock['core_business'] = []
            if description not in stock['core_business']:
                stock['core_business'].append(description)
            
            updated_count += 1
            print(f"  ✓ {code} {row['name']}: description synced")
    
    # Save updated master data
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Sync complete! Updated {updated_count} stocks in stocks_master.json")
    
    # Verify
    desc_count = sum(1 for s in master_stocks if s.get('description'))
    print(f"📊 Total stocks with description field: {desc_count}")

if __name__ == '__main__':
    sync_descriptions()
