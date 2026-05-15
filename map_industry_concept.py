#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从同花顺行业和所属概念文件映射数据到 stocks_master.json
"""

import json
import pandas as pd
from datetime import date
from pathlib import Path

def load_mapping_files():
    """加载行业和概念映射文件"""
    base_dir = Path(__file__).parent / 'archived'
    
    # 加载行业映射
    industry_df = pd.read_excel(base_dir / '同花顺行业.xls')
    industry_map = {}
    for _, row in industry_df.iterrows():
        code = str(row['股票代码']).split('.')[0]  # 去掉.SZ/.SH 后缀
        industry_map[code] = row['所属同花顺行业']
    
    print(f"✅ 加载行业映射：{len(industry_map)} 只股票")
    
    # 加载概念映射
    concept_df = pd.read_excel(base_dir / '所属概念.xls')
    concept_map = {}
    for _, row in concept_df.iterrows():
        code = str(row['股票代码']).split('.')[0]  # 去掉.SZ/.SH 后缀
        concepts = str(row['所属概念']).split(';') if pd.notna(row['所属概念']) else []
        concepts = [c.strip() for c in concepts if c.strip()]
        concept_map[code] = concepts
    
    print(f"✅ 加载概念映射：{len(concept_map)} 只股票")
    
    return industry_map, concept_map

def update_stocks_master(industry_map, concept_map):
    """更新 stocks_master.json 中的行业和概念信息"""
    master_file = Path('data/stocks/stocks_master.json')
    
    with open(master_file, 'r', encoding='utf-8') as f:
        master = json.load(f)
    
    updated_count = 0
    missing_count = 0
    today_str = date.today().isoformat()
    
    for code, stock in master['stocks'].items():
        updated = False
        
        # 更新行业
        if code in industry_map and industry_map[code]:
            industry = industry_map[code]
            if industry and industry != stock.get('industry', ''):
                print(f"📊 {code} {stock['name']}: 行业更新 '{stock.get('industry', '')}' → '{industry}'")
                stock['industry'] = industry
                updated = True
        
        # 更新概念
        if code in concept_map and concept_map[code]:
            concepts = concept_map[code]
            if concepts:
                # 合并现有概念和新概念
                existing_concepts = set(stock.get('concepts', []))
                new_concepts = set(concepts)
                all_concepts = existing_concepts | new_concepts
                
                if len(all_concepts) > len(existing_concepts):
                    print(f"💡 {code} {stock['name']}: 概念新增 {len(all_concepts) - len(existing_concepts)} 个")
                    stock['concepts'] = sorted(list(all_concepts))
                    updated = True
        
        if updated:
            stock['last_updated'] = today_str
            updated_count += 1
        else:
            missing_count += 1
    
    # 保存更新后的数据
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(master, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 更新完成：{updated_count} 只股票已更新，{missing_count} 只股票无需更新")
    return master

if __name__ == '__main__':
    print("🚀 开始映射行业和概念数据...")
    industry_map, concept_map = load_mapping_files()
    update_stocks_master(industry_map, concept_map)
    print("\n✨ 全部完成！")
