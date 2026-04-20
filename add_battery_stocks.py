#!/usr/bin/env python3
"""
添加固态电池/锂电设备股票到数据库
"""
import json
from pathlib import Path
from datetime import datetime

# 股票列表
stocks_to_add = [
    {
        "code": "301325",
        "name": "曼恩斯特",
        "industry": "电力设备-电池-锂电设备",
        "concepts": ["涂布模头", "干法电极", "固态电池设备", "锂电设备"],
        "drivers": "湿法涂布模头市占率领先，成功切入干法电极整线设备，混料、纤维化、多辊成膜设备均已获订单，固态电池设备订单放量。",
        "valuation": {"target_price": "66.56元", "pe": "2026年52倍PE", "rating": "买入"},
    },
    {
        "code": "688006",
        "name": "杭可科技",
        "industry": "电力设备-电池-锂电设备",
        "concepts": ["化成分容", "高压化成", "固态电池", "锂电设备"],
        "drivers": "化成分容领域龙头，高压化成技术领先，适配多种固态电解质体系，与国内头部电池厂深度合作，加速全球化布局。2025年H1业绩重回增长，现金流大幅改善。",
        "valuation": {"target_price": "31.93元", "pe": "2025年31倍PE", "rating": "买入"},
    },
    {
        "code": "300450",
        "name": "先导智能",
        "industry": "电力设备-电池-锂电设备",
        "concepts": ["锂电设备", "固态电池设备", "叠片设备", "等静压设备"],
        "drivers": "锂电设备龙头，全固态电池设备全环节覆盖，叠片设备全球市占率第一，600MPa等静压设备、高压化成分容设备均已交付。2025年Q1-Q3归母净利同比增长94.97%。",
        "valuation": {"target_price": "66.65元", "pe": "2026年43倍PE", "rating": "买入"},
    },
]

def add_stocks():
    """添加股票到数据库"""
    base_dir = Path(__file__).parent
    master_file = base_dir / 'data' / 'master' / 'stocks_master.json'
    
    # 读取现有数据
    with open(master_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', {})
    added_count = 0
    updated_count = 0
    
    for stock_info in stocks_to_add:
        code = stock_info['code']
        
        # 构建股票数据结构
        stock_data = {
            "code": code,
            "name": stock_info['name'],
            "board": "SZ" if code.startswith('0') or code.startswith('3') else "SH",
            "industry": stock_info['industry'],
            "concepts": stock_info['concepts'],
            "mention_count": 1,
            "articles": [
                {
                    "title": f"{stock_info['name']}研究",
                    "date": "2026-04-20",
                    "source": "用户输入",
                    "accidents": [stock_info['drivers']],
                    "insights": [stock_info['drivers']],
                    "key_metrics": [],
                    "target_valuation": [f"目标价: {stock_info['valuation']['target_price']}", f"估值: {stock_info['valuation']['pe']}"]
                }
            ],
            "valuation": stock_info['valuation'],
            "created_at": "2026-04-20",
            "updated_at": "2026-04-20"
        }
        
        if code in stocks:
            print(f"⚠️ 更新股票: {code} ({stock_info['name']})")
            stocks[code].update(stock_data)
            updated_count += 1
        else:
            print(f"✅ 添加新股票: {code} ({stock_info['name']})")
            stocks[code] = stock_data
            added_count += 1
    
    # 保存
    data['stocks'] = stocks
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！新增 {added_count} 只，更新 {updated_count} 只，共 {len(stocks)} 只股票")

if __name__ == '__main__':
    add_stocks()
