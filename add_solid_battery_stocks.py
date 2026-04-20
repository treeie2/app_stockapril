#!/usr/bin/env python3
"""
添加固态电池产业链股票到数据库
"""
import json
from pathlib import Path
from datetime import datetime

# 股票列表
stocks_to_add = [
    {
        "code": "301662",
        "name": "宏工科技",
        "industry": "电力设备-电池-锂电设备",
        "concepts": ["固态电池设备", "干法电极", "锂电设备", "混合纤维化"],
        "drivers": "干法前段（混合/纤维化）核心突破，与清研电子成立合资推进产业化；2024年已签订数千万元固态产线及设备订单，定位固态上料/输送/搅拌核心供应商；多渠道反馈其在宁德小试/中试与干法环节有订单记录，4-5月前段设备招标最直接受益。",
        "valuation": {"target_market_cap": None},
    },
    {
        "code": "832522",
        "name": "纳科诺尔",
        "industry": "电力设备-电池-锂电设备",
        "concepts": ["固态电池设备", "辊压设备", "干法电极", "等静压"],
        "drivers": "辊压龙头，热辊压技术指标领先，固态关键设备已交付头部客户；公司在干法电极成膜/压延、电解质成膜/转印、等静压多点布局，享受干法必选+辊压升级量价双重红利。",
        "valuation": {"target_market_cap": None},
    },
    {
        "code": "688155",
        "name": "先惠技术",
        "industry": "电力设备-电池-锂电设备",
        "concepts": ["固态电池设备", "干法电极", "PACK自动化", "智能制造"],
        "drivers": "在干法电极设备与PACK自动化装配领域拥有布局，受益于固态叠片/封装段对自动化与制程一体化的更高要求，作为整线/分段自动化的补强值得跟踪（与整线厂协同概率高）。",
        "valuation": {"target_market_cap": None},
    },
    {
        "code": "300490",
        "name": "华自科技",
        "industry": "电力设备-电池-锂电设备",
        "concepts": ["固态电池设备", "等静压", "高压化成", "锂电装备"],
        "drivers": "后段高压化成分容延伸至等静压上下料/协同，已落地等静压方向的合作伙伴与合资公司，处于固态中段工艺生态的系统解决方案位置，随等静压导入节奏具备β。",
        "valuation": {"target_market_cap": None},
    },
    {
        "code": "688778",
        "name": "厦钨新能",
        "industry": "电力设备-电池-电池材料",
        "concepts": ["固态电池材料", "硫化锂", "正极材料", "固态电解质"],
        "drivers": "硫化锂中试取得显著成果并规划扩大产能（一年内优化装备材质，目标规模化），同时在正极（含NL新结构）与固态电解质（硫化物/氧化物）均有布局，已与头部客户开展共研与送样；材料端可靠性+降本路径清晰后，订单催化可期。",
        "valuation": {"target_market_cap": None},
    },
    {
        "code": "688560",
        "name": "明冠新材",
        "industry": "电力设备-电池-电池材料",
        "concepts": ["固态电池材料", "铝塑膜", "软包电池", "国产替代"],
        "drivers": "铝塑膜国产替代加速、固态软包路线带来新增量，公司在铝塑膜赛道深耕，随固态软包路线推进度受益。",
        "valuation": {"target_market_cap": None},
    },
    {
        "code": "301150",
        "name": "中一科技",
        "industry": "有色金属-工业金属-铜",
        "concepts": ["固态电池材料", "铜箔", "复合集流体", "锂金属负极"],
        "drivers": "固态适配铜箔/复合集流体，已开展锂-铜金属一体化复合负极材料相关技术并与客户协同研发；固态/半固态用铜箔行业已见小批量/批量供货案例（同业对比），客户验证推进后放量可期。",
        "valuation": {"target_market_cap": None},
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
        
        # 判断交易所
        if code.startswith('6'):
            board = "SH"
        elif code.startswith('8'):
            board = "BJ"  # 北交所
        else:
            board = "SZ"
        
        # 构建股票数据结构
        stock_data = {
            "code": code,
            "name": stock_info['name'],
            "board": board,
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
                    "target_valuation": []
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
