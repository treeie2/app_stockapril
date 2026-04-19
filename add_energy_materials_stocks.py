#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从能源材料相关微信公众号文章提取的个股信息添加到投研数据库"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / ".trae" / "skills" / "wechat-fetch-research-embedded" / "scripts"))

from incremental_update import IncrementalUpdater

# 文章1: 圣阳股份 - 算力备电/固态电池
stocks_article_1 = [
    {
        "code": "002580",
        "name": "圣阳股份",
        "board": "SZ",
        "industry": "电力设备-电池-蓄电池",
        "concepts": ["算力备电", "固态电池", "液冷储能", "数据中心", "铅酸电池", "锂电", "山东国资"],
        "products": ["铅酸备用电源", "锂电池", "固态电池", "全浸没液冷方舱UPS", "储能系统"],
        "core_business": ["数据中心备电系统", "固态电池研发", "液冷储能解决方案", "通信基站储能"],
        "industry_position": ["国内数据中心铅酸备用电源市场约40%份额", "算力备电龙头", "山东国资控股"],
        "chain": ["算力-上游-备电系统", "储能-中游-储能系统", "固态电池-中游-电池制造"],
        "partners": ["阿里", "腾讯", "字节跳动", "三大运营商"],
        "mention_count": 1,
        "articles": [{
            "title": "山东国资控股，固态电池新锐，算力备电龙头业绩爆发",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/4y7lsah1DPjfRpIQ2RSsjQ",
            "accidents": ["前三季度营收26.02亿元，同比增长15.43%", "经营性现金流同比增长119.86%", "2025年上半年数据中心业务收入同比暴增216%", "自主研发的固态电池已完成第三方权威检测机构验证测试", "收购深圳达人高科51%股权"],
            "insights": ["国内数据中心铅酸备用电源市场占有约40%份额", "2025年上半年数据中心业务占总营收比重从9.37%跃升至24.75%", "3GWh专用产能满产满销，订单排到2026年下半年", "采用复合氧化物技术路线，良品率达到92%", "全浸没液冷方舱UPS功率密度可达单机柜600kVA以上，PUE能逼近1.1", "液冷系统在手订单8.3亿元，数据中心备电订单排至2026年9月", "海外中标东南亚、中东AI算力项目，订单超过8亿元", "2021年山东国惠控股，实控人变为山东省国资委"],
            "key_metrics": ["营收26.02亿元同比+15.43%", "经营性现金流同比+119.86%", "数据中心业务收入同比+216%", "毛利率24.08%", "3GWh产能满产满销", "液冷系统在手订单8.3亿元", "海外订单超8亿元", "固态电池良品率92%"],
            "target_valuation": []
        }]
    }
]

# 文章2: 宝丽迪 - COFs材料
stocks_article_2 = [
    {
        "code": "300905",
        "name": "宝丽迪",
        "board": "SZ",
        "industry": "基础化工-化学纤维-纤维母粒",
        "concepts": ["COFs材料", "共价有机框架", "固态电池", "纤维母粒", "新材料", "量产"],
        "products": ["纤维母粒", "COFs材料（共价有机框架材料）", "化纤色母粒"],
        "core_business": ["纤维母粒研发生产", "COFs材料研发量产", "化纤新材料"],
        "industry_position": ["纤维母粒业务国内市场产销量领先", "COFs材料吨级量产国内领先"],
        "chain": ["化工-中游-纤维母粒", "新材料-上游-COFs材料", "固态电池-上游-材料"],
        "partners": ["恒逸", "桐昆"],
        "mention_count": 1,
        "articles": [{
            "title": "COFs材料从概念走向量产的估值重构",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/QyJTzhCzRp5e2P8xIpMmbg",
            "accidents": ["2026年4月17日再度以20%涨幅封板，实现两连板", "预计2025年全年净利润为1.45-1.52亿元，同比增长27.17%-33.30%", "子公司耀科新材料实现COFs吨级量产", "耀科200吨COFs新建项目已完成立项"],
            "insights": ["纤维母粒业务市占率超过30%，与恒逸、桐昆等化纤龙头长期稳定合作", "COFs材料已实现吨级量产，200吨产线环评审批及场地建设正有序推进", "目前已处于客户验证推广阶段，应用验证主要集中在石化催化、气体分离、储能材料等方向", "COFs产品尚未开展固态电池领域相关验证", "日产汽车计划2025年3月启动全固态电池生产，2028年实现量产目标"],
            "key_metrics": ["2025年净利润1.45-1.52亿元同比+27.17%-33.30%", "纤维母粒市占率超30%", "COFs吨级量产", "200吨COFs产线立项"],
            "target_valuation": []
        }]
    },
    {
        "code": "000819",
        "name": "岳阳兴长",
        "board": "SZ",
        "industry": "石油石化-炼化及贸易-石化产品",
        "concepts": ["MOFs材料", "金属有机框架", "新材料", "中试"],
        "products": ["MOFs材料", "石化产品"],
        "core_business": ["MOFs材料研发", "石化产品生产"],
        "industry_position": ["MOFs材料中试先行者"],
        "chain": ["新材料-上游-MOFs材料", "化工-中游-石化产品"],
        "partners": [],
        "mention_count": 1,
        "articles": [{
            "title": "COFs材料从概念走向量产的估值重构",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/QyJTzhCzRp5e2P8xIpMmbg",
            "accidents": ["已建设100吨/年的MOFs材料中试生产装置", "与岳阳县高新技术产业开发区签署合作协议打造MOFs材料产业化基地"],
            "insights": ["拥有多种MOFs材料的自主知识产权", "正在同步验证和拓展下游应用领域", "MOFs中试规模在国内处于领先地位"],
            "key_metrics": ["100吨/年MOFs材料中试产能"],
            "target_valuation": []
        }]
    }
]

def main():
    """主函数：批量添加个股"""
    print("🚀 从能源材料相关文章提取个股信息到投研数据库...\n")
    
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
    print(f"   1. 圣阳股份：算力备电/固态电池")
    print(f"   2. 宝丽迪/岳阳兴长：COFs/MOFs材料")

if __name__ == "__main__":
    main()
