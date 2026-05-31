#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 2026-05-31.xls (HTML格式) 解析所有股票概念，
更新 stocks_master.json，并生成概念MD文档。
"""
import json, re
from pathlib import Path
from datetime import date
from html.parser import HTMLParser

XLS_FILE = Path('E:/github/stock-research-backup/2026-05-31.xls')
MASTER_FILE = Path('E:/github/stock-research-backup/data/stocks/stocks_master.json')
CONCEPT_MD_FILE = Path('E:/github/stock-research-backup/docs/个股概念数据库.md')

# ========== 1. 解析 HTML 表格 ==========
class StockTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_tr = False
        self.in_td = False
        self.current_row = []
        self.current_cell = ''
        self.headers = []
        self.rows = []
        self.col_index = 0
        self.is_header = False

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.in_table = True
        elif tag == 'tr' and self.in_table:
            self.in_tr = True
            self.current_row = []
            self.col_index = 1  # Skip first col (row number)
        elif tag == 'td' and self.in_tr:
            self.in_td = True
            self.current_cell = ''
            cls = ''
            for attr in attrs:
                if attr[0] == 'class':
                    cls = attr[1]
            self.is_header = 'Title' in cls or 'title' in cls

    def handle_endtag(self, tag):
        if tag == 'td' and self.in_td:
            self.in_td = False
            text = self.current_cell.strip()
            if self.col_index <= 7:  # We only care about first 8 columns
                self.current_row.append(text)
            self.col_index += 1
        elif tag == 'tr':
            self.in_tr = False
            if self.current_row and len(self.current_row) >= 6:
                self.rows.append(self.current_row)
        elif tag == 'table':
            self.in_table = False

    def handle_data(self, data):
        if self.in_td:
            self.current_cell += data

parser = StockTableParser()
with open(XLS_FILE, 'r', encoding='utf-8') as f:
    html_content = f.read()
parser.feed(html_content)

print(f"解析到 {len(parser.rows)} 行数据")

# ========== 2. 构建概念映射表 ==========
concept_map = {}  # code -> {name, concepts, market_type}
row_count = 0
for row in parser.rows:
    if len(row) < 6:
        continue
    raw_code = row[0].strip()
    name = row[1].strip()
    market_type = row[4].strip()
    concept_str = row[5].strip()
    
    code = raw_code.split('.')[0]
    code = code.strip()
    
    concepts = []
    if concept_str and concept_str != '--':
        concepts = [c.strip() for c in concept_str.split(';') if c.strip()]
    
    concept_map[code] = {
        'name': name,
        'raw_code': raw_code,
        'concepts': concepts,
        'market_type': market_type
    }
    row_count += 1

print(f"有效记录: {row_count} 只股票")

# ========== 3. 更新 stocks_master.json ==========
with open(MASTER_FILE, 'r', encoding='utf-8') as f:
    master = json.load(f)

today_str = date.today().isoformat()
updated_master_count = 0
updated_stocks_list = []

for code, stock in master['stocks'].items():
    if code in concept_map:
        new_concepts = concept_map[code]['concepts']
        existing_concepts = set(stock.get('concepts', []) or [])
        new_set = set(new_concepts)
        
        if existing_concepts != new_set:
            stock['concepts'] = sorted(list(new_set))
            stock['last_updated'] = today_str
            updated_master_count += 1
            updated_stocks_list.append(code)

# 检查不在 master 但有概念的股票（可能的新股票）
new_stocks_from_xls = []
for code, info in concept_map.items():
    if code not in master['stocks'] and info['concepts']:
        new_stocks_from_xls.append((code, info['name']))

print(f"\n已更新 stocks_master.json: {updated_master_count} 只股票")
print(f"XLS中有但master中不存在的股票: {len(new_stocks_from_xls)} 只")
for code, name in new_stocks_from_xls[:10]:
    print(f"  新股票: {code} {name}")

# 更新 master 文件的 top-level updated_at
master['updated_at'] = today_str

with open(MASTER_FILE, 'w', encoding='utf-8') as f:
    json.dump(master, f, ensure_ascii=False, indent=2)

print(f"✅ stocks_master.json 已保存")

# ========== 4. 生成概念 Markdown 文档 ==========
# 按概念分组统计
concept_to_stocks = {}
for code, info in concept_map.items():
    for c in info['concepts']:
        if c not in concept_to_stocks:
            concept_to_stocks[c] = []
        concept_to_stocks[c].append((code, info['name']))

# 构建 MD 内容
lines = []
lines.append('# 个股概念数据库')
lines.append('')
lines.append(f'> **数据来源**: 2026-05-31.xls（同花顺数据）')
lines.append(f'> **更新日期**: {today_str}')
lines.append(f'> **总股票数**: {len(concept_map)} | **总概念数**: {len(concept_to_stocks)}')
lines.append('')
lines.append('---')
lines.append('')
lines.append('## 目录')
lines.append('')
lines.append('- [1. 按概念分类](#1-按概念分类)')
lines.append('- [2. 按个股概念列表](#2-按个股概念列表)')
lines.append('- [3. 统计信息](#3-统计信息)')
lines.append('')
lines.append('---')
lines.append('')

# ===== 1. 按概念分类 =====
lines.append('## 1. 按概念分类')
lines.append('')
lines.append(f'共 **{len(concept_to_stocks)}** 个概念，按股票数量降序排列')
lines.append('')
lines.append('| 概念 | 股票数量 | 个股 |')
lines.append('|------|---------|------|')

sorted_concepts = sorted(concept_to_stocks.items(), key=lambda x: -len(x[1]))
for concept, stocks in sorted_concepts:
    stock_str = '、'.join([f'`{code}` {name}' for code, name in stocks])
    lines.append(f'| **{concept}** | {len(stocks)} | {stock_str} |')

lines.append('')
lines.append('---')
lines.append('')

# ===== 2. 按个股概念列表 =====
lines.append('## 2. 按个股概念列表')
lines.append('')
lines.append(f'共 **{len(concept_map)}** 只股票，按股票代码升序排列')
lines.append('')
lines.append('| 股票代码 | 股票简称 | 市场类型 | 概念数量 | 所属概念 |')
lines.append('|---------|---------|---------|---------|---------|')

sorted_stocks = sorted(concept_map.items(), key=lambda x: x[0])
for code, info in sorted_stocks:
    concepts = info['concepts']
    concept_str = '、'.join([f'`{c}`' for c in concepts]) if concepts else '--'
    market = info.get('market_type', '')
    lines.append(f'| {code} | {info["name"]} | {market} | {len(concepts)} | {concept_str} |')

lines.append('')
lines.append('---')
lines.append('')

# ===== 3. 统计信息 =====
lines.append('## 3. 统计信息')
lines.append('')
lines.append(f'- **总股票数**: {len(concept_map)}')
lines.append(f'- **总概念数**: {len(concept_to_stocks)}')
lines.append(f'- **平均概念数/股**: {sum(len(v["concepts"]) for v in concept_map.values()) / len(concept_map):.1f}')

# 概念最多的股票
top_stocks = sorted(concept_map.items(), key=lambda x: -len(x[1]['concepts']))[:10]
lines.append('')
lines.append(f'### 概念最多的股票 Top 10')
lines.append('')
lines.append('| 排名 | 股票代码 | 股票简称 | 概念数量 |')
lines.append('|------|---------|---------|---------|')
for i, (code, info) in enumerate(top_stocks, 1):
    lines.append(f'| {i} | {code} | {info["name"]} | {len(info["concepts"])} |')

# 股票最多的概念 Top 20
lines.append('')
lines.append(f'### 包含股票最多的概念 Top 20')
lines.append('')
lines.append('| 排名 | 概念 | 股票数量 |')
lines.append('|------|------|---------|')
for i, (concept, stocks) in enumerate(sorted_concepts[:20], 1):
    lines.append(f'| {i} | {concept} | {len(stocks)} |')

lines.append('')
lines.append('---')
lines.append('')
lines.append(f'> 本文档由脚本自动生成，数据来源: `2026-05-31.xls`')

md_content = '\n'.join(lines)

# 确保目录存在
CONCEPT_MD_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(CONCEPT_MD_FILE, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"✅ 概念MD文档已生成: {CONCEPT_MD_FILE}")
print(f"   - {len(concept_map)} 只股票")
print(f"   - {len(concept_to_stocks)} 个概念")

# 输出今日更新的24只股票概念检查
today_codes = ['601101','688234','301611','000636','300408','600589','002126','300617',
               '301588','301565','300540','605376','002859','300285','300179','002046',
               '688028','000519','600176','603256','301526','002080','605006','300975']

print(f"\n今日24只股票概念检查:")
for code in today_codes:
    info = concept_map.get(code)
    if info:
        print(f"  ✅ {code} {info['name']}: {len(info['concepts'])} 个概念")
    else:
        print(f"  ❌ {code}: 不在2026-05-31.xls中")

# 检查哪些更新了
print(f"\nMaster中更新的股票: {updated_master_count} 只")
print("示例:")
for code in updated_stocks_list[:5]:
    s = master['stocks'].get(code, {})
    print(f"  {code} {s.get('name')}: concepts={s.get('concepts', [])[:5]}...")