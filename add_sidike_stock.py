#!/usr/bin/env python3
"""
添加斯迪克股票到数据库
"""
import json
from pathlib import Path
from datetime import datetime

# 股票信息
stock_info = {
    "code": "300806",
    "name": "斯迪克",
    "industry": "功能性薄膜材料",
    "concepts": ["磁电存储", "华为概念", "新材料", "存储芯片", "纳米涂布"],
    "drivers": "深度绑定H家：合资落地意味着斯迪克联合H家共研、生产、销售磁电存储相关产品确定性为100%，彻底打消市场先前质疑。H面向AI场景打造'SSD+MED'双层存储架构，MED国内市场空间约1200亿，H占MED市场预计超过80%，千亿市场空间。斯迪克具备纳米级涂布工艺，独家负责电磁涂布，在磁电存储中价值量占比超60%（毛利率高达60%～70%）。",
    "valuation": {
        "target_market_cap": "1000亿",
        "current_market_cap": None,
        "upside": None
    },
    "articles": [
        {
            "title": "斯迪克深度绑定H家磁电存储",
            "date": "2026-04-19",
            "insights": [
                "合资落地确定性100%",
                "MED市场空间约1200亿",
                "价值量占比超60%，毛利率60-70%",
                "目标市值1000亿"
            ]
        }
    ],
    "created_at": "2026-04-19",
    "updated_at": "2026-04-19"
}

def add_stock():
    """添加股票到数据库"""
    base_dir = Path(__file__).parent
    master_file = base_dir / 'data' / 'master' / 'stocks_master.json'
    
    # 读取现有数据
    with open(master_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', {})
    
    # 检查是否已存在
    if stock_info['code'] in stocks:
        print(f"⚠️ 股票 {stock_info['code']} ({stock_info['name']}) 已存在，更新信息...")
        # 更新现有股票
        stocks[stock_info['code']].update(stock_info)
    else:
        print(f"✅ 添加新股票: {stock_info['code']} ({stock_info['name']})")
        stocks[stock_info['code']] = stock_info
    
    # 保存
    data['stocks'] = stocks
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完成！共 {len(stocks)} 只股票")

if __name__ == '__main__':
    add_stock()
