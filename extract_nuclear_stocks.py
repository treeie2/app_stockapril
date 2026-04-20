#!/usr/bin/env python3
"""
从核电+特高压文章中提取股票信息并更新到数据库
"""
import json
from pathlib import Path
from datetime import datetime

# 文章中提到的10只股票
stocks_data = [
    {
        "code": "600089",
        "name": "特变电工",
        "industry": "电力设备-输变电设备",
        "concepts": ["核电", "特高压", "变压器", "电力装备"],
        "drivers": "全球变压器龙头，产品同时覆盖核电站用变压器与特高压变压器。2025年三季报归母净利润约54.84亿元，同比增长27.55%。已完成从上游材料到输变电装备的全产业链布局。",
        "core_business": ["变压器制造", "输变电装备", "核电变压器", "特高压变压器"],
        "industry_position": ["全球变压器龙头", "核电变压器核心供应商"],
        "chain": ["中游 - 电力设备", "中游 - 输变电设备"]
    },
    {
        "code": "601179",
        "name": "中国西电",
        "industry": "电力设备-输配电装备",
        "concepts": ["核电", "特高压", "输配电", "电力装备"],
        "drivers": "电力装备综合巨头，国内领先的输配电装备供应商，产品广泛应用于核电与特高压电网。2025年三季报营收同比增长11.54%，净利润增长19.29%。2026年初斩获国家电网14.47亿元订单，特高压设备国内市场占有率超过40%。",
        "core_business": ["输配电装备", "特高压设备", "核电设备"],
        "industry_position": ["电力装备综合巨头", "特高压设备市占率超40%"],
        "chain": ["中游 - 电力设备", "中游 - 输配电装备"]
    },
    {
        "code": "600550",
        "name": "保变电气",
        "industry": "电力设备-变压器",
        "concepts": ["核电", "变压器", "核电设备", "AP1000", "CAP1400"],
        "drivers": "核电变压器专家，国内核电站用变压器的核心供应商，产品适配AP1000、CAP1400等三代核电技术。2025年三季报营收同比增长41.9%，归母净利润同比大幅增长72.91%。",
        "core_business": ["核电变压器", "核电站用变压器", "特种变压器"],
        "industry_position": ["核电变压器专家", "三代核电技术供应商"],
        "chain": ["中游 - 电力设备", "中游 - 变压器"]
    },
    {
        "code": "600312",
        "name": "平高电气",
        "industry": "电力设备-开关设备",
        "concepts": ["核电", "特高压", "开关设备", "GIS/GIL"],
        "drivers": "特高压开关龙头，专注于超特高压交直流开关设备（GIS/GIL），为漳州核电等重大项目提供关键设备。2025年中报归母净利润同比增长24.59%，是中国电气装备集团旗下的核心企业。",
        "core_business": ["超特高压开关设备", "GIS/GIL", "核电开关设备"],
        "industry_position": ["特高压开关龙头", "中国电气装备集团旗下核心企业"],
        "chain": ["中游 - 电力设备", "中游 - 开关设备"]
    },
    {
        "code": "002130",
        "name": "沃尔核材",
        "industry": "电力设备-电缆附件",
        "concepts": ["核电", "电缆附件", "1E级电缆", "华龙一号"],
        "drivers": "核电电缆附件核心供应商，核电站用1E级电缆附件及特种材料的核心供应商，应用于华龙一号等自主三代核电项目。2025年三季报净利润同比增长25.45%，毛利率长期稳定在30%以上，净利率达14.52%。",
        "core_business": ["核电电缆附件", "1E级电缆附件", "特种材料"],
        "industry_position": ["核电电缆附件核心供应商", "华龙一号供应商"],
        "chain": ["上游 - 电缆材料", "中游 - 电缆附件"]
    },
    {
        "code": "603308",
        "name": "应流股份",
        "industry": "机械设备-铸锻件",
        "concepts": ["核电", "铸锻件", "泵壳", "阀门"],
        "drivers": "高端铸锻件供应商，为核电项目提供泵壳、阀门等关键铸锻件，技术门槛高。2025年三季报毛利率高达36.92%，净利润同比增长29.59%，盈利能力强劲。",
        "core_business": ["高端铸锻件", "核电泵壳", "核电阀门"],
        "industry_position": ["高端铸锻件供应商", "核电关键部件供应商"],
        "chain": ["上游 - 铸锻件", "中游 - 核电部件"]
    },
    {
        "code": "600973",
        "name": "宝胜股份",
        "industry": "电力设备-核级电缆",
        "concepts": ["核电", "核级电缆", "中核", "中广核"],
        "drivers": "核级电缆领军者，拥有国内最全的核级电缆生产许可证，产品全面进入中核、中广核供应链。2025年中报归母净利润同比大幅增长265.54%，业绩弹性巨大。",
        "core_business": ["核级电缆", "核电电缆", "特种电缆"],
        "industry_position": ["核级电缆领军者", "国内最全核级电缆许可证"],
        "partners": ["中核", "中广核"],
        "chain": ["上游 - 电缆材料", "中游 - 核级电缆"]
    },
    {
        "code": "300617",
        "name": "安靠智电",
        "industry": "电力设备-智能输电",
        "concepts": ["核电", "智能输电", "地下输电"],
        "drivers": "地下智能输电先锋，主营地下智能输电系统，产品应用于核电站等重要场所的电力输送。2025年三季报营收增长30.5%，净利润增长35.2%，净利率高达17.7%。",
        "core_business": ["地下智能输电系统", "智能输电", "核电输电"],
        "industry_position": ["地下智能输电先锋"],
        "chain": ["中游 - 智能输电", "中游 - 电力系统"]
    },
    {
        "code": "600268",
        "name": "国电南自",
        "industry": "电力设备-电力自动化",
        "concepts": ["核电", "电力自动化", "发电机组保护", "国产替代"],
        "drivers": "电力自动化专家，国内电力自动化领先企业，其发电机组保护装置在核电领域实现重大国产化突破。2025年中报归母净利润同比增长197.03%，成长性显著。打破了核电核心控制保护系统长期依赖进口的局面。",
        "core_business": ["电力自动化", "发电机组保护装置", "核电控制系统"],
        "industry_position": ["电力自动化专家", "核电国产替代标杆"],
        "chain": ["中游 - 电力自动化", "中游 - 控制系统"]
    },
    {
        "code": "002112",
        "name": "三变科技",
        "industry": "电力设备-特种变压器",
        "concepts": ["核电", "特种变压器", "电网", "光伏"],
        "drivers": "专注特种变压器，主营变压器产品，服务于核电、电网、光伏等多场景。2025年三季报营收与净利润保持稳定增长，拥有64项相关专利。",
        "core_business": ["特种变压器", "核电变压器", "电网变压器"],
        "industry_position": ["特种变压器专业厂商"],
        "chain": ["中游 - 电力设备", "中游 - 变压器"]
    }
]

def update_stocks_master():
    """更新 stocks_master.json"""
    master_file = Path("e:/github/stock-research-backup/data/master/stocks_master.json")
    
    with open(master_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', {})
    today = datetime.now().strftime('%Y-%m-%d')
    
    added_count = 0
    updated_count = 0
    
    for stock_info in stocks_data:
        code = stock_info['code']
        
        # 判断交易所
        if code.startswith('6'):
            board = "SH"
        else:
            board = "SZ"
        
        # 构建文章数据
        article = {
            "title": "核电+特高压概念！盘点业绩领先的10家核心公司",
            "date": today,
            "source": "https://mp.weixin.qq.com/s/cJqK4aWM24AFml-5VyFeCA",
            "accidents": [stock_info['drivers']],
            "insights": [stock_info['drivers']],
            "key_metrics": [],
            "target_valuation": []
        }
        
        # 构建股票数据
        stock_data = {
            "code": code,
            "name": stock_info['name'],
            "board": board,
            "industry": stock_info['industry'],
            "concepts": stock_info['concepts'],
            "core_business": stock_info.get('core_business', []),
            "industry_position": stock_info.get('industry_position', []),
            "chain": stock_info.get('chain', []),
            "partners": stock_info.get('partners', []),
            "mention_count": 1,
            "articles": [article],
            "created_at": today,
            "updated_at": today
        }
        
        if code in stocks:
            # 更新现有股票
            existing = stocks[code]
            existing['concepts'] = list(set((existing.get('concepts') or []) + stock_info['concepts']))
            existing['core_business'] = list(set((existing.get('core_business') or []) + stock_info.get('core_business', [])))
            existing['industry_position'] = list(set((existing.get('industry_position') or []) + stock_info.get('industry_position', [])))
            existing['chain'] = list(set((existing.get('chain') or []) + stock_info.get('chain', [])))
            existing['partners'] = list(set((existing.get('partners') or []) + stock_info.get('partners', [])))
            existing['articles'] = existing.get('articles', []) + [article]
            existing['mention_count'] = existing.get('mention_count', 0) + 1
            existing['updated_at'] = today
            updated_count += 1
            print(f"  🔄 更新: {code} {stock_info['name']}")
        else:
            # 新增股票
            stocks[code] = stock_data
            added_count += 1
            print(f"  ➕ 新增: {code} {stock_info['name']}")
    
    # 保存回文件
    data['stocks'] = stocks
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！新增: {added_count}, 更新: {updated_count}")
    return added_count, updated_count

if __name__ == '__main__':
    print("🚀 开始提取核电+特高压股票并更新数据库...\n")
    update_stocks_master()
