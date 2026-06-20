#!/usr/bin/env python3
"""Look up stock codes for HarmonyOS 7.0 article stocks"""
import pandas as pd
import json
from pathlib import Path

base_dir = Path(__file__).parent
stock_xls = pd.read_excel(base_dir / 'assets/全部个股.xls')
industry_df = pd.read_excel(base_dir / 'assets/同花顺行业.xls')
concept_df = pd.read_excel(base_dir / 'assets/所属概念.xls')

targets = ['润和软件', '诚迈科技', '软通动力', '智微智能', '法本信息', 
           '瑞芯微', '广和通', '恒玄科技', '乐鑫科技', '晶晨股份']

master_path = Path(__file__).parents[3] / 'data' / 'stocks' / 'stocks_master.json'
master = json.loads(master_path.read_text(encoding='utf-8'))
master_stocks = master.get('stocks', {})

for name in targets:
    stock_row = stock_xls[stock_xls['股票简称'].str.contains(name, na=False)]
    if len(stock_row) > 0:
        code = str(stock_row.iloc[0]['股票代码']).split('.')[0]
        
        industry_row = industry_df[industry_df['股票简称'].str.contains(name, na=False)]
        industry = industry_row.iloc[0]['所属同花顺行业'] if len(industry_row) > 0 else '其他'
        
        board = 'SH' if code.startswith('6') or code.startswith('9') else 'SZ'
        
        # Check in master
        in_master = code in master_stocks
        existing_articles = len(master_stocks[code].get('articles', [])) if in_master else 0
        
        print(f'{code} {name} | {board} | {industry} | master={"是" if in_master else "否"}({existing_articles}篇)')
    else:
        print(f'?? {name} | NOT FOUND')