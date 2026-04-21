#!/usr/bin/env python3
"""
添加爱施德 (002416) 到数据库
"""
import json
from pathlib import Path
from datetime import datetime

def add_aishide():
    """添加爱施德股票数据"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 爱施德详细数据
    stock_data = {
        "code": "002416",
        "name": "爱施德",
        "board": "SZ",
        "industry": "商贸零售 - 专业连锁 - 专业连锁",
        "concepts": [
            "荣耀产业链",
            "机器人",
            "消费电子",
            "5G",
            "物联网"
        ],
        "products": [
            "消费电子分销",
            "机器人销售",
            "智能终端"
        ],
        "core_business": [
            "消费电子渠道分销",
            "荣耀机器人全国总代理",
            "智能终端销售与服务"
        ],
        "industry_position": [
            "荣耀机器人全国独家总代理",
            "消费电子渠道龙头",
            "荣耀股东（通过星盟信息持股约 25.55%）"
        ],
        "chain": [
            "商贸零售 - 中游 - 消费电子分销",
            "机器人 - 下游 - 销售与服务"
        ],
        "partners": [
            "荣耀",
            "苹果",
            "华为",
            "云深处科技"
        ],
        "mention_count": 1,
        "articles": [
            {
                "title": "荣耀机器人 IPO 核心标的，爱施德深度绑定荣耀产业链",
                "date": today,
                "source": "manual_input",
                "accidents": [
                    "荣耀机器人启动 A 股 IPO",
                    "荣耀机器人半马 50 分 26 秒破人类纪录",
                    "爱施德是荣耀机器人全国独家总代理"
                ],
                "insights": [
                    "子公司持有荣耀母公司星盟信息约 25.55% 股权，是荣耀机器人最核心受益标的",
                    "荣耀机器人全国独家总代理，直接受益于机器人商业化落地",
                    "通过智城基金投资云深处科技（四足机器人龙头）1.27% 股份，双机器人概念",
                    "消费电子渠道龙头，与荣耀业务深度绑定"
                ],
                "key_metrics": [
                    "荣耀机器人全国总代理",
                    "持股星盟信息 25.55%",
                    "投资云深处科技 1.27%"
                ],
                "target_valuation": []
            }
        ],
        "last_updated": today
    }
    
    # 写入当天分片文件
    daily_file = Path("data/master/stocks") / f"{today}.json"
    
    if daily_file.exists():
        with open(daily_file, 'r', encoding='utf-8') as f:
            daily_data = json.load(f)
    else:
        daily_data = {"date": today, "update_count": 0, "stocks": {}}
    
    daily_data['stocks']['002416'] = stock_data
    daily_data['update_count'] = len(daily_data['stocks'])
    
    with open(daily_file, 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已添加爱施德 (002416) 到 {today}.json")
    
    # 更新索引
    index_file = Path("data/master/stocks_index.json")
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    index_data['stocks']['002416'] = {
        "name": "爱施德",
        "last_updated": today,
        "file": f"{today}.json"
    }
    index_data['total_stocks'] = len(index_data['stocks'])
    index_data['last_updated'] = today
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新 stocks_index.json")
    
    # 合并到主文件
    master_file = Path("data/master/stocks_master.json")
    with open(master_file, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    master_stocks = master_data.get('stocks', {})
    master_stocks['002416'] = stock_data
    
    master_data['stocks'] = master_stocks
    
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已合并到 stocks_master.json")
    print(f"\n📊 总计：{len(master_stocks)} 只股票")

if __name__ == "__main__":
    add_aishide()
