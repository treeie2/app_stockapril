#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path

p = Path("e:/github/stock-research-backup/data/stocks")
jsons = sorted(p.glob("2026-*.json"))
print(f"股票数据分片文件数: {len(jsons)}\n")

total_unique = set()
for f in jsons:
    data = json.load(open(f, encoding="utf-8"))
    stocks = data.get("stocks", {})
    print(f"  {f.name}: {len(stocks)} 只")
    total_unique.update(stocks.keys())

print(f"\n所有分片去重后总个股数: {len(total_unique)}")

# 读取 index
idx = json.load(open(p / "stocks_index.json", encoding="utf-8"))
print(f"\nstocks_index.json 收录: {idx.get('total_stocks', '?')} 只")

# 读取 master
master = json.load(open(p / "stocks_master.json", encoding="utf-8"))
print(f"stocks_master.json 收录: {len(master.get('stocks', {}))} 只 (有详情数据的)")