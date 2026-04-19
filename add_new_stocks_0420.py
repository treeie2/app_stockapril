#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从微信公众号文章提取的个股信息添加到投研数据库"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / ".trae" / "skills" / "wechat-fetch-research-embedded" / "scripts"))

from incremental_update import IncrementalUpdater

# 文章1: 北京利尔 - 耐火材料龙头布局固态电池和商业航天
stocks_article_1 = [
    {
        "code": "002392",
        "name": "北京利尔",
        "board": "SZ",
        "industry": "建筑材料-耐火材料-耐火材料制品",
        "concepts": ["耐火材料", "固态电池", "商业航天", "航空航天", "锆基材料", "复合氧化锆", "新能源"],
        "products": ["不定形高温材料", "机压定型高温材料", "预制型高温材料", "功能性高温材料", "复合氧化锆", "锆基材料"],
        "core_business": ["耐火材料制造", "复合氧化锆生产", "锆基材料研发", "新能源材料", "航空航天材料"],
        "industry_position": ["耐火材料龙头", "国内领先的高温材料企业"],
        "chain": ["建筑材料-中游-耐火材料", "新能源-上游-固态电池材料", "航空航天-上游-高温材料"],
        "partners": [],
        "mention_count": 1,
        "articles": [{
            "title": "耐火材料龙头，布局固态电池和商业航天",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/b5_jNQOgT_9LNduzhCcXKw",
            "accidents": ["拟募集资金总额不超过10.34亿元", "年产3万吨复合氧化锆及新能源与航空航天用锆基材料项目", "越南耐火材料生产基地建设项目"],
            "insights": ["正式跳出传统耐火材料的存量竞争，向高附加值新兴领域突围", "锆基材料不仅是高端耐火材料的关键原料，更是前沿产业不可或缺的核心材料", "在新能源领域，锆基材料凭借较高的离子电导率和界面稳定性，已成为当前全固态电池的主流电解质方案之一", "在航空航天领域，其高熔点、低热导率、优异的抗热震性及高温稳定性，使其广泛应用于热障涂层、航空喷丸、火箭喷嘴、热防护罩"],
            "key_metrics": ["募集资金总额不超过10.34亿元", "年产3万吨复合氧化锆", "项目总投资约3.65亿元", "旗下拥有20多家子公司", "产品涵盖八大系列近300个品种"],
            "target_valuation": []
        }]
    }
]

# 文章2: 四会富仕 - 工控复苏叠加机器人全新增量
stocks_article_2 = [
    {
        "code": "300852",
        "name": "四会富仕",
        "board": "SZ",
        "industry": "电子-元件-印制电路板",
        "concepts": ["PCB", "工控", "机器人", "人形机器人", "汽车电子", "泰国基地", "伺服电机"],
        "products": ["高多层板", "HDI板", "厚铜板", "金属基板", "陶瓷基板", "软硬结合板", "高频高速板", "埋嵌铜块基板", "PCB电机定子"],
        "core_business": ["高品质PCB研发与制造", "工控PCB", "汽车电子PCB", "机器人PCB", "通信设备PCB", "医疗器械PCB"],
        "industry_position": ["专注于高品质PCB的研发与制造", "内资企业中较早实现在泰国投产"],
        "chain": ["电子-中游-PCB", "工控-上游-核心部件", "机器人-上游-执行器", "汽车-上游-电子部件"],
        "partners": ["三花智控"],
        "mention_count": 1,
        "articles": [{
            "title": "工控复苏叠加机器人全新增量",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/HM9TndjKdOBkUphUr4khEg",
            "accidents": ["2024年实现营业收入14.13亿元，同比增长7.49%", "汽车电子领域收入增长约22%", "泰国生产基地2024年下半年正式投产", "有部分产品在人形机器人执行器上有应用"],
            "insights": ["公司产品主要应用于机器人执行机构的伺服电机和减速装置，控制系统的控制器、伺服驱动器、无框力矩电机、空心杯电机、编码器、传感器等", "PCB方案替代绕线组定子，实现电机体积进一步缩小，重量进一步减轻，适配具身机器人", "随着具身机器人出货量的不断增长，以及轴向电机渗透率的不断提升，定子PCB市场空间有望迎来快速成长", "2025年Q1和Q2，公司国内产能基本满产，泰国产能逐步爬坡，整体业绩逐步进入成长趋势"],
            "key_metrics": ["营业收入14.13亿元同比增长7.49%", "汽车电子领域收入增长约22%", "净利率9.93%", "机器人执行器应用产品营收占比小于1%"],
            "target_valuation": []
        }]
    }
]

def main():
    """主函数：批量添加个股"""
    print("🚀 从微信公众号文章提取个股信息到投研数据库...\n")
    
    updater = IncrementalUpdater(base_dir=str(Path(__file__).parent / "data" / "master"))
    
    all_stocks = stocks_article_1 + stocks_article_2
    added_count = 0
    updated_count = 0
    
    for stock in all_stocks:
        code = stock["code"]
        name = stock["name"]
        
        stock_data = {
            "name": name,
            "board": stock["board"],
            "industry": stock["industry"],
            "concepts": stock["concepts"],
            "products": stock["products"],
            "core_business": stock["core_business"],
            "industry_position": stock["industry_position"],
            "chain": stock["chain"],
            "partners": stock["partners"],
            "mention_count": stock["mention_count"],
            "articles": stock["articles"]
        }
        
        result = updater.update_single_stock(code, stock_data)
        
        if result["action"] == "added":
            added_count += 1
            print(f"  ➕ 新增: {name} ({code})")
        else:
            updated_count += 1
            print(f"  🔄 更新: {name} ({code})")
    
    print(f"\n✅ 批量添加完成!")
    print(f"   ➕ 新增: {added_count} 只")
    print(f"   🔄 更新: {updated_count} 只")
    print(f"   📅 日期: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"\n📊 涉及文章:")
    print(f"   1. 耐火材料龙头，布局固态电池和商业航天")
    print(f"   2. 四会富仕：工控复苏叠加机器人全新增量")

if __name__ == "__main__":
    main()
