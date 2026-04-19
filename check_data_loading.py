#!/usr/bin/env python3
"""
检查数据加载情况
"""
import json
from pathlib import Path

# 检查 stocks_master.json
master_file = Path("e:/github/stock-research-backup/data/master/stocks_master.json")
if master_file.exists():
    with open(master_file, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    master_stocks = master_data.get('stocks', {})
    print(f"✅ stocks_master.json 存在")
    print(f"   包含 {len(master_stocks)} 只个股")
    
    # 检查宁德时代
    if '300750' in master_stocks:
        print(f"   ✅ 宁德时代 (300750) 在 master 中")
    else:
        print(f"   ❌ 宁德时代 (300750) 不在 master 中")
    
    # 检查比亚迪
    if '002594' in master_stocks:
        print(f"   ✅ 比亚迪 (002594) 在 master 中")
    else:
        print(f"   ❌ 比亚迪 (002594) 不在 master 中")
else:
    print(f"❌ stocks_master.json 不存在")

# 检查今日数据
today_file = Path("e:/github/stock-research-backup/data/master/stocks/2026-04-19.json")
if today_file.exists():
    with open(today_file, 'r', encoding='utf-8') as f:
        today_data = json.load(f)
    today_stocks = today_data.get('stocks', {})
    print(f"\n✅ 2026-04-19.json 存在")
    print(f"   包含 {len(today_stocks)} 只个股")
    
    # 检查宁德时代
    if '300750' in today_stocks:
        print(f"   ✅ 宁德时代 (300750) 在今日数据中")
    else:
        print(f"   ❌ 宁德时代 (300750) 不在今日数据中")
    
    # 检查比亚迪
    if '002594' in today_stocks:
        print(f"   ✅ 比亚迪 (002594) 在今日数据中")
    else:
        print(f"   ❌ 比亚迪 (002594) 不在今日数据中")
        
    # 检查北方华创
    if '002371' in today_stocks:
        print(f"   ✅ 北方华创 (002371) 在今日数据中")
    else:
        print(f"   ❌ 北方华创 (002371) 不在今日数据中")
else:
    print(f"\n❌ 2026-04-19.json 不存在")

# 检查索引
index_file = Path("e:/github/stock-research-backup/data/master/stocks_index.json")
if index_file.exists():
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    total = index_data.get('total_stocks', 0)
    stocks_dict = index_data.get('stocks', {})
    print(f"\n✅ stocks_index.json 存在")
    print(f"   索引显示: {total} 只个股")
    print(f"   实际条目: {len(stocks_dict)} 只个股")
    
    # 检查宁德时代
    if '300750' in stocks_dict:
        print(f"   ✅ 宁德时代 (300750) 在索引中")
    else:
        print(f"   ❌ 宁德时代 (300750) 不在索引中")
else:
    print(f"\n❌ stocks_index.json 不存在")
