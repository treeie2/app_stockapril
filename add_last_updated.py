#!/usr/bin/env python3
"""
为今日更新的股票添加 last_updated 字段
"""
import json
from pathlib import Path
from datetime import datetime

MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")
TODAY = datetime.now().strftime('%Y-%m-%d')

# 今日更新的股票代码
TODAY_STOCKS = [
    '002046', '603019', '000977', '603118',
    '000960', '600961', '600531', '002428', '002975', '600206', '600703',
    '688498', '600105', '688048', '002023', '688313', '002281', '000988',
    '002725', '300316', '002371', '603005'
]

def add_last_updated():
    """添加 last_updated 字段"""
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        stocks_master = json.load(f)
    
    updated_count = 0
    
    for code in TODAY_STOCKS:
        if code in stocks_master:
            stock = stocks_master[code]
            stock['last_updated'] = TODAY
            updated_count += 1
            print(f"✅ {code} {stock.get('name', '')}: last_updated = {TODAY}")
    
    # 保存更新后的数据
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(stocks_master, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！更新了 {updated_count} 只股票的 last_updated 字段")

if __name__ == '__main__':
    add_last_updated()
