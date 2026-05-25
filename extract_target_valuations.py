#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 提取所有有目标估值的个股

import json
from pathlib import Path

# 读取主数据文件
master_file = Path("data/stocks/stocks_master.json")
with open(master_file, 'r', encoding='utf-8') as f:
    master = json.load(f)

results = []

# 遍历所有股票
for code, stock in master['stocks'].items():
    name = stock.get('name', '')
    articles = stock.get('articles', [])
    
    # 收集所有目标估值
    all_target_valuations = []
    for article in articles:
        target_valuation = article.get('target_valuation', [])
        if target_valuation:
            all_target_valuations.extend(target_valuation)
    
    # 只保留有目标估值的股票
    if all_target_valuations:
        # 去重
        unique_valuations = list(set(all_target_valuations))
        results.append({
            'code': code,
            'name': name,
            'valuations': unique_valuations
        })

# 按股票代码排序
results.sort(key=lambda x: x['code'])

# 输出表格
print("=" * 80)
print(f"{'序号':<4} {'股票代码':<8} {'股票名称':<12} {'目标估值'}")
print("=" * 80)

for i, result in enumerate(results, 1):
    valuations_str = '\n'.join(result['valuations'])
    print(f"{i:<4} {result['code']:<8} {result['name']:<12}")
    for v in result['valuations']:
        print(f"     {' '*8} {' '*12} {v}")
    print("-" * 80)

print(f"\n总计：{len(results)} 只个股有目标估值")

# 保存到文件
output_file = "target_valuations.md"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# 个股目标估值汇总\n\n")
    f.write(f"| 序号 | 股票代码 | 股票名称 | 目标估值 |\n")
    f.write(f"|:---:|:---:|:---|---|\n")
    for i, result in enumerate(results, 1):
        valuations_str = '；'.join(result['valuations'])
        f.write(f"| {i} | {result['code']} | {result['name']} | {valuations_str} |\n")

print(f"\n✅ 已保存到 {output_file}")
