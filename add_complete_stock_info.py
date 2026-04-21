#!/usr/bin/env python3
"""
补充今日更新股票的核心业务、行业地位、产业链位置字段
"""
import json
from pathlib import Path

MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")

# 股票的完整信息
STOCK_INFO = {
    # 航天轴承 + 金刚石散热
    '002046': {
        'core_business': ['航天轴承', '金刚石散热片', '半导体设备'],
        'industry_position': ['国内金刚石领域第一梯队，航天领域市占率 90% 以上'],
        'chain': ['中游 - 航天轴承', '中游 - 金刚石散热', '中游 - 半导体设备']
    },
    '603019': {
        'core_business': ['AI 服务器', '液冷服务器', '云计算设备'],
        'industry_position': ['国内 AI 服务器龙头'],
        'chain': ['中游 -AI 服务器制造']
    },
    '000977': {
        'core_business': ['AI 服务器', '云计算设备', '存储服务器'],
        'industry_position': ['国内服务器行业领先企业'],
        'chain': ['中游 - 服务器制造']
    },
    '603118': {
        'core_business': ['通信设备', '物联网终端', '车联网'],
        'industry_position': ['国内通信设备行业领先企业'],
        'chain': ['中游 - 通信设备制造']
    },
    
    # 磷化铟产业链
    '000960': {
        'core_business': ['铟产品', '磷化铟', '稀有金属'],
        'industry_position': ['全国最大的铟产品生产商'],
        'chain': ['上游 - 铟矿开采', '中游 - 磷化铟材料']
    },
    '600961': {
        'core_business': ['锌冶炼', '铟产品', '稀有金属回收'],
        'industry_position': ['国内铟回收龙头企业'],
        'chain': ['上游 - 铟矿开采', '中游 - 磷化铟材料']
    },
    '600531': {
        'core_business': ['铅冶炼', '铟产品', '贵金属回收'],
        'industry_position': ['国内重要的铟产品供应商'],
        'chain': ['上游 - 铟矿开采', '中游 - 磷化铟材料']
    },
    '002428': {
        'core_business': ['锗产品', '磷化铟', '红外光学'],
        'industry_position': ['国内锗行业龙头'],
        'chain': ['上游 - 锗矿开采', '中游 - 磷化铟衬底']
    },
    '002975': {
        'core_business': ['检测设备', '磷化铟检测', '半导体测试'],
        'industry_position': ['国内检测设备领先企业'],
        'chain': ['上游 - 检测设备制造']
    },
    '600206': {
        'core_business': ['半导体材料', '靶材', '磷化铟'],
        'industry_position': ['国内半导体材料领先企业'],
        'chain': ['中游 - 磷化铟靶材']
    },
    '600703': {
        'core_business': ['LED 芯片', '化合物半导体', '磷化铟'],
        'industry_position': ['国内 LED 芯片龙头'],
        'chain': ['中游 - 磷化铟外延片', '下游-LED 芯片']
    },
    '688498': {
        'core_business': ['光芯片', '磷化铟激光器', '光通信'],
        'industry_position': ['国内光芯片领先企业'],
        'chain': ['中游 - 磷化铟光芯片']
    },
    '600105': {
        'core_business': ['光纤光缆', '光通信设备', '磷化铟'],
        'industry_position': ['国内光纤光缆行业领先企业'],
        'chain': ['下游 - 光通信设备']
    },
    '688048': {
        'core_business': ['激光芯片', '磷化铟激光器', '光通信'],
        'industry_position': ['国内激光芯片领先企业'],
        'chain': ['中游 - 磷化铟激光芯片']
    },
    '002023': {
        'core_business': ['航空技术', '空管设备', '军工电子'],
        'industry_position': ['国内航空空管设备龙头'],
        'chain': ['下游 - 航空设备']
    },
    '688313': {
        'core_business': ['光芯片', '磷化铟光器件', '光通信'],
        'industry_position': ['国内光器件领先企业'],
        'chain': ['中游 - 磷化铟光器件']
    },
    '002281': {
        'core_business': ['光器件', '光模块', '磷化铟'],
        'industry_position': ['国内光器件行业领先企业'],
        'chain': ['中游 - 磷化铟光器件', '下游 - 光模块']
    },
    '000988': {
        'core_business': ['激光设备', '光通信器件', '磷化铟'],
        'industry_position': ['国内激光设备领先企业'],
        'chain': ['中游 - 光通信器件']
    },
    '002725': {
        'core_business': ['汽车零部件', '车轮', '铝合金'],
        'industry_position': ['国内车轮行业领先企业'],
        'chain': ['下游 - 汽车零部件']
    },
    '300316': {
        'core_business': ['光伏设备', '晶体生长设备', '半导体设备'],
        'industry_position': ['国内光伏设备龙头'],
        'chain': ['上游 - 光伏设备', '中游 - 半导体设备']
    },
    '002371': {
        'core_business': ['半导体设备', '刻蚀机', '薄膜沉积设备'],
        'industry_position': ['国内半导体设备龙头'],
        'chain': ['上游 - 半导体设备制造']
    },
    
    # TGV 技术
    '603005': {
        'core_business': ['半导体封测', 'TGV 技术', '晶圆级封装'],
        'industry_position': ['国内半导体封测领先企业'],
        'chain': ['中游 - 半导体封测']
    }
}

def add_stock_info():
    """补充股票信息"""
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        stocks_master = json.load(f)
    
    updated_count = 0
    
    for code, info in STOCK_INFO.items():
        if code in stocks_master:
            stock = stocks_master[code]
            
            # 更新 core_business
            if info['core_business']:
                if 'core_business' not in stock or not stock['core_business']:
                    stock['core_business'] = info['core_business']
                    updated_count += 1
                    print(f"✅ {code} {stock.get('name', '')}: core_business = {info['core_business']}")
            
            # 更新 industry_position
            if info['industry_position']:
                if 'industry_position' not in stock or not stock['industry_position']:
                    stock['industry_position'] = info['industry_position']
                    print(f"   industry_position = {info['industry_position']}")
            
            # 更新 chain
            if info['chain']:
                if 'chain' not in stock or not stock['chain']:
                    stock['chain'] = info['chain']
                    print(f"   chain = {info['chain']}")
    
    # 保存更新后的数据
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(stocks_master, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！更新了 {updated_count} 只股票的核心业务字段")

if __name__ == '__main__':
    add_stock_info()
