#!/usr/bin/env python3
"""
补充今日更新股票的 industry 字段
"""
import json
from pathlib import Path

MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")

# 股票的 industry 信息
STOCK_INDUSTRIES = {
    # 航天轴承 + 金刚石散热
    '002046': '机械设备-通用设备-磨具磨料',
    '603019': '计算机-计算机设备-其他计算机设备',
    '000977': '计算机-计算机设备-其他计算机设备',
    '603118': '通信-通信设备-其他通信设备',
    
    # 磷化铟产业链
    '000960': '有色金属-稀有金属-其他稀有金属',
    '600961': '有色金属-稀有金属-其他稀有金属',
    '600531': '有色金属-稀有金属-其他稀有金属',
    '002428': '电子-电子化学品-电子化学品',
    '002975': '机械设备-仪器仪表-仪器仪表',
    '600206': '电子-电子化学品-电子化学品',
    '600703': '电子-光学光电子-LED',
    '688498': '电子-半导体-数字芯片设计',
    '600105': '通信-通信设备-通信网络设备及器件',
    '688048': '电子-半导体-模拟芯片设计',
    '002023': '国防军工-航空装备-航空装备',
    '688313': '电子-半导体-数字芯片设计',
    '002281': '通信-通信设备-通信网络设备及器件',
    '000988': '计算机-计算机设备-其他计算机设备',
    '002725': '汽车零部件-其他汽车零部件',
    '300316': '机械设备-光伏设备-光伏设备',
    '002371': '电子-半导体-半导体设备',
    
    # TGV 技术
    '603005': '电子-半导体-半导体封测',
}

def add_industries():
    """补充 industry 字段"""
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        stocks_master = json.load(f)
    
    updated_count = 0
    
    for code, industry in STOCK_INDUSTRIES.items():
        if code in stocks_master:
            stock = stocks_master[code]
            if not stock.get('industry'):
                stock['industry'] = industry
                updated_count += 1
                print(f"✅ {code} {stock.get('name', '')}: {industry}")
    
    # 保存更新后的数据
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(stocks_master, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！更新了 {updated_count} 只股票的 industry 字段")

if __name__ == '__main__':
    add_industries()
