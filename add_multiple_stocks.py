#!/usr/bin/env python3
"""
批量添加多只股票到数据库
"""
import json
from pathlib import Path
from datetime import datetime

# 股票列表
stocks_to_add = [
    {
        "code": "002796",
        "name": "世嘉科技",
        "industry": "通信设备-光通信设备-光模块",
        "concepts": ["光模块", "AMD概念", "光通信", "800G光模块", "1.6T光模块", "CPO"],
        "drivers": "通过光彩芯辰供货AMD光模块，独创SOG光路集成核心技术，产品覆盖100G至800G及1.6T系列光模块。",
        "valuation": {"target_market_cap": None},
    },
    {
        "code": "300857",
        "name": "协创数据",
        "industry": "电子-消费电子-消费电子零部件及组装",
        "concepts": ["消费电子", "数据中心", "存储"],
        "drivers": "",
        "valuation": {"target_market_cap": "2000亿"},
    },
    {
        "code": "301396",
        "name": "宏景科技",
        "industry": "计算机-IT服务-IT服务",
        "concepts": ["AI算力", "智慧城市", "IT服务"],
        "drivers": "当前PE仅13.6x，目标市值800亿，市值空间80.18%。",
        "valuation": {"target_market_cap": "800亿", "current_pe": "13.6x", "upside": "80.18%"},
    },
    {
        "code": "603629",
        "name": "利通电子",
        "industry": "电子-消费电子-消费电子零部件及组装",
        "concepts": ["算力租赁", "东阳光合作"],
        "drivers": "最低成本拿货渠道，与东阳光设立合资公司，2027年利润预计31亿，目标市值620亿，市值空间148%。",
        "valuation": {"target_market_cap": "620亿", "current_market_cap": "251亿", "upside": "148%"},
    },
    {
        "code": "002990",
        "name": "盛视科技",
        "industry": "计算机-软件开发-垂直应用软件",
        "concepts": ["AI算力", "算力租赁", "智慧口岸", "GPU"],
        "drivers": "11亿IT设备采购（GPU等算力硬件），230亿综合授信，算力租赁布局，智慧口岸+算力底座。",
        "valuation": {"target_market_cap": None},
    },
    {
        "code": "600105",
        "name": "永鼎股份",
        "industry": "通信-通信设备-通信线缆及配套",
        "concepts": ["光纤", "可控核聚变", "鼎芯"],
        "drivers": "光纤业务200亿+传统业务50亿+可控核聚变150亿+鼎芯（持股50%），总体看到750亿。",
        "valuation": {"target_market_cap": "750亿"},
    },
    {
        "code": "002824",
        "name": "和胜股份",
        "industry": "有色金属-工业金属-铝",
        "concepts": ["NV概念", "液冷", "Busbar", "富士康"],
        "drivers": "NV液冷Busbar独家供应商（通过富士康FIT），单柜价值量1900美金，2027年目标市值150亿。",
        "valuation": {"target_market_cap": "150亿"},
    },
    {
        "code": "603031",
        "name": "安孚科技",
        "industry": "电力设备-电池-其他电池",
        "concepts": ["硅光芯片", "CPO", "薄膜铌酸锂", "南孚电池"],
        "drivers": "投资苏州易缆微（硅光芯片），南孚电池持股46%，投资国产GPU象帝先。",
        "valuation": {"target_market_cap": None},
    },
    {
        "code": "300782",
        "name": "卓胜微",
        "industry": "电子-半导体-模拟芯片设计",
        "concepts": ["射频芯片", "硅光芯片", "IDM", "AI算力"],
        "drivers": "国内唯一化合物+锗硅+SOI三大材料全自主IDM，射频芯片400亿市值打底，光芯片年收入75亿。",
        "valuation": {"target_market_cap": "400亿+"},
    },
    {
        "code": "603005",
        "name": "晶方科技",
        "industry": "电子-半导体-集成电路封测",
        "concepts": ["TSV封装", "光模块封装", "先进封装"],
        "drivers": "TSV封装收入占比超70%，与旭创等头部光模块公司合作，目标市值578亿。",
        "valuation": {"target_market_cap": "578亿", "base_value": "150亿"},
    },
]

def add_stocks():
    """批量添加股票到数据库"""
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
                    "accidents": [stock_info['drivers']] if stock_info['drivers'] else [],
                    "insights": [stock_info['drivers']] if stock_info['drivers'] else [],
                    "key_metrics": [],
                    "target_valuation": [f"目标市值: {stock_info['valuation']['target_market_cap']}"] if stock_info['valuation'].get('target_market_cap') else []
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
