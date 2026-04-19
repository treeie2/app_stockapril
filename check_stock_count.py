#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查数据库中的个股数量"""

import json
from pathlib import Path

# 读取索引文件
index_path = Path("data/master/stocks_index.json")
with open(index_path, 'r', encoding='utf-8') as f:
    index_data = json.load(f)

total_stocks = index_data.get("total_stocks", 0)
stocks_dict = index_data.get("stocks", {})

print(f"📊 数据库统计")
print(f"=" * 50)
print(f"索引显示总个股数: {total_stocks}")
print(f"索引中实际条目数: {len(stocks_dict)}")

# 按日期统计
date_counts = {}
for code, info in stocks_dict.items():
    date = info.get("last_updated", "unknown")
    date_counts[date] = date_counts.get(date, 0) + 1

print(f"\n📅 按日期分布:")
for date in sorted(date_counts.keys(), reverse=True)[:10]:
    print(f"  {date}: {date_counts[date]} 只")

# 检查今日数据
today = "2026-04-19"
today_file = Path(f"data/master/stocks/{today}.json")
if today_file.exists():
    with open(today_file, 'r', encoding='utf-8') as f:
        today_data = json.load(f)
    today_stocks = today_data.get("stocks", {})
    print(f"\n📁 今日({today})数据文件:")
    print(f"  包含个股数: {len(today_stocks)}")
    print(f"  更新计数: {today_data.get('update_count', 0)}")

# 检查宁德时代
catl_code = "300750"
if catl_code in stocks_dict:
    catl_info = stocks_dict[catl_code]
    print(f"\n🔋 宁德时代 ({catl_code}):")
    print(f"  名称: {catl_info.get('name')}")
    print(f"  最后更新: {catl_info.get('last_updated')}")
    print(f"  所在文件: {catl_info.get('file')}")
else:
    print(f"\n❌ 宁德时代 ({catl_code}) 不在索引中")

# 检查比亚迪
byd_code = "002594"
if byd_code in stocks_dict:
    byd_info = stocks_dict[byd_code]
    print(f"\n🚗 比亚迪 ({byd_code}):")
    print(f"  名称: {byd_info.get('name')}")
    print(f"  最后更新: {byd_info.get('last_updated')}")
    print(f"  所在文件: {byd_info.get('file')}")
else:
    print(f"\n❌ 比亚迪 ({byd_code}) 不在索引中")
