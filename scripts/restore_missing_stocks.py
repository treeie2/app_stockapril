#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恢复丢失的股票：蜀道装备(300540)、美新科技(301588)，
并从 2026-05-31.xls 补充它们的概念。
"""
import json, pandas as pd
from pathlib import Path

MASTER_FILE = Path('E:/github/stock-research-backup/data/stocks/stocks_master.json')
XLS_FILE = Path('E:/github/stock-research-backup/2026-05-31.xls')

# 读取 XLS
dfs = pd.read_html(str(XLS_FILE), encoding='utf-8')
df = dfs[0]

# 构建概念映射
concept_map = {}
for _, row in df.iterrows():
    raw_code = str(row[0]).strip()
    code = raw_code.split('.')[0]
    name = str(row[1]).strip()
    concept_str = str(row[5]).strip()
    concepts = [c.strip() for c in concept_str.split(';') if c.strip() and c != '--'] if concept_str else []
    concept_map[code] = {'name': name, 'concepts': concepts, 'raw_code': raw_code}

# 读取 master
with open(MASTER_FILE, 'r', encoding='utf-8') as f:
    master = json.load(f)

# 检查哪些股票丢失
missing = []
for code in ['300540', '301588']:
    if code not in master['stocks']:
        info = concept_map.get(code)
        if info:
            missing.append((code, info))
            print(f"❌ {code} {info['name']} - 在 XLS 中但在 master 中丢失")
        else:
            print(f"❌ {code} - 在 XLS 中也找不到")

# 从 XLS 恢复丢失的股票
if missing:
    print(f"\n🔄 从 XLS 恢复 {len(missing)} 只股票...")
    for code, info in missing:
        master['stocks'][code] = {
            'name': info['name'],
            'code': code,
            'concepts': info['concepts'],
            'last_updated': '2026-05-31'
        }
        print(f"  ✅ 已恢复 {code} {info['name']} ({len(info['concepts'])} 个概念)")

    # 保存
    master['updated_at'] = '2026-05-31'
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(master, f, ensure_ascii=False, indent=2)
    print(f"\n✅ master 已保存，共 {len(master['stocks'])} 只股票")

    # 验证
    for code in ['300540', '301588']:
        s = master['stocks'].get(code, {})
        print(f"  {code} {s.get('name')}: concepts={s.get('concepts', '❌')[:5]}... (共{len(s.get('concepts',[]))}个)")