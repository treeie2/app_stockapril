#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从第三代半导体文章提取7只个股信息添加到投研数据库"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / ".trae" / "skills" / "wechat-fetch-research-embedded" / "scripts"))

from incremental_update import IncrementalUpdater

# 第三代半导体7家龙头股
stocks_to_add = [
    {
        "code": "600703",
        "name": "三安光电",
        "board": "SH",
        "industry": "电子-半导体-LED",
        "concepts": ["第三代半导体", "碳化硅", "氮化镓", "化合物半导体", "IDM模式", "MicroLED", "国产替代"],
        "products": ["碳化硅衬底", "碳化硅外延", "氮化镓器件", "MicroLED", "光通讯器件"],
        "core_business": ["化合物半导体研发制造", "碳化硅全产业链", "氮化镓器件", "LED芯片", "光通讯"],
        "industry_position": ["国内化合物半导体龙头", "第三代半导体全产业链布局", "IDM模式领先"],
        "chain": ["第三代半导体-上游-衬底/外延", "第三代半导体-中游-器件"],
        "partners": ["清华", "中国移动"],
        "mention_count": 1,
        "articles": [{
            "title": "第三代半导体成热点，7家龙头股全面梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/CvVGCnaaYEA6EHAL9-XyWQ",
            "accidents": ["2025年第三代半导体业务营收占比超20%", "与清华、中国移动合作推进高速光通讯研发", "布局专利400余件"],
            "insights": ["国内化合物半导体龙头，构建IDM模式", "覆盖碳化硅、氮化镓衬底、外延、器件全环节", "深度受益广东政策红利"],
            "key_metrics": ["第三代半导体业务营收占比超20%", "布局专利400余件"],
            "target_valuation": []
        }]
    },
    {
        "code": "688234",
        "name": "天岳先进",
        "board": "SH",
        "industry": "电子-半导体材料-半导体材料",
        "concepts": ["第三代半导体", "碳化硅衬底", "半绝缘型", "导电型", "国产替代"],
        "products": ["碳化硅衬底", "半绝缘型衬底", "导电型衬底", "8英寸衬底", "12英寸衬底"],
        "core_business": ["碳化硅衬底研发制造", "半绝缘型衬底", "导电型衬底"],
        "industry_position": ["全球碳化硅衬底领军企业", "半绝缘与导电型双路线领先", "8英寸规模化量产", "12英寸送样验证"],
        "chain": ["第三代半导体-上游-衬底"],
        "partners": [],
        "mention_count": 1,
        "articles": [{
            "title": "第三代半导体成热点，7家龙头股全面梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/CvVGCnaaYEA6EHAL9-XyWQ",
            "accidents": ["2025年碳化硅衬底业务营收占比超85%", "已实现8英寸规模化量产", "12英寸送样验证"],
            "insights": ["受益14英寸碳化硅技术突破，大尺寸升级红利显著", "产能持续扩张，良率稳步提升", "订单饱满"],
            "key_metrics": ["碳化硅衬底业务营收占比超85%", "8英寸规模化量产", "12英寸送样验证"],
            "target_valuation": []
        }]
    },
    {
        "code": "300316",
        "name": "晶盛机电",
        "board": "SZ",
        "industry": "电力设备-光伏设备-光伏设备",
        "concepts": ["第三代半导体", "碳化硅设备", "长晶设备", "大尺寸衬底加工", "光伏设备"],
        "products": ["碳化硅长晶设备", "大尺寸衬底加工设备", "12英寸产线设备"],
        "core_business": ["长晶设备研发制造", "大尺寸衬底加工", "碳化硅设备"],
        "industry_position": ["长晶设备与大尺寸衬底加工领域领先", "12英寸产线核心设备100%国产化"],
        "chain": ["第三代半导体-上游-设备"],
        "partners": ["天岳先进", "天成半导体"],
        "mention_count": 1,
        "articles": [{
            "title": "第三代半导体成热点，7家龙头股全面梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/CvVGCnaaYEA6EHAL9-XyWQ",
            "accidents": ["2025年半导体设备业务营收占比超30%", "碳化硅长晶设备市占率居国内前列"],
            "insights": ["为14英寸碳化硅产业化提供关键装备支撑", "深度配套天岳先进、天成半导体等企业", "订单持续落地"],
            "key_metrics": ["半导体设备业务营收占比超30%", "12英寸产线核心设备100%国产化"],
            "target_valuation": []
        }]
    },
    {
        "code": "603290",
        "name": "斯达半导",
        "board": "SH",
        "industry": "电子-半导体-分立器件",
        "concepts": ["第三代半导体", "碳化硅模块", "车规级功率模块", "新能源汽车", "800V平台"],
        "products": ["碳化硅功率模块", "IGBT模块", "车规级功率器件"],
        "core_business": ["车规级功率模块研发制造", "碳化硅模块", "IGBT模块"],
        "industry_position": ["国内车规级功率模块领军企业", "碳化硅模块技术领先", "深度配套特斯拉、比亚迪"],
        "chain": ["第三代半导体-中游-器件/模块"],
        "partners": ["特斯拉", "比亚迪"],
        "mention_count": 1,
        "articles": [{
            "title": "第三代半导体成热点，7家龙头股全面梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/CvVGCnaaYEA6EHAL9-XyWQ",
            "accidents": ["2025年碳化硅模块营收同比增长超60%", "业务占比超25%"],
            "insights": ["直接受益上游碳化硅材料突破与成本下降", "加速800V平台渗透率提升", "订单稳步增长"],
            "key_metrics": ["碳化硅模块营收同比增长超60%", "业务占比超25%"],
            "target_valuation": []
        }]
    },
    {
        "code": "600460",
        "name": "士兰微",
        "board": "SH",
        "industry": "电子-半导体-分立器件",
        "concepts": ["第三代半导体", "碳化硅功率芯片", "氮化镓", "功率半导体", "光伏储能", "国产替代"],
        "products": ["碳化硅功率芯片", "氮化镓功率芯片", "功率半导体器件"],
        "core_business": ["功率半导体研发制造", "碳化硅功率芯片", "氮化镓功率芯片"],
        "industry_position": ["国内功率半导体龙头", "碳化硅功率芯片产能持续释放", "良率稳定在90%以上"],
        "chain": ["第三代半导体-中游-器件"],
        "partners": [],
        "mention_count": 1,
        "articles": [{
            "title": "第三代半导体成热点，7家龙头股全面梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/CvVGCnaaYEA6EHAL9-XyWQ",
            "accidents": ["2025年第三代半导体相关业务营收占比超18%", "良率稳定在90%以上"],
            "insights": ["布局碳化硅、氮化镓功率芯片", "覆盖新能源、工业控制等下游场景", "受益于国内第三代半导体规模化应用"],
            "key_metrics": ["第三代半导体相关业务营收占比超18%", "良率稳定在90%以上"],
            "target_valuation": []
        }]
    },
    {
        "code": "300373",
        "name": "扬杰科技",
        "board": "SZ",
        "industry": "电子-半导体-分立器件",
        "concepts": ["第三代半导体", "氮化镓", "GaN分立器件", "消费电子快充", "光伏逆变器"],
        "products": ["氮化镓分立器件", "GaN芯片", "功率器件"],
        "core_business": ["氮化镓分立器件研发制造", "功率半导体器件"],
        "industry_position": ["国内氮化镓分立器件领军企业", "产品覆盖消费电子、新能源领域"],
        "chain": ["第三代半导体-中游-器件"],
        "partners": [],
        "mention_count": 1,
        "articles": [{
            "title": "第三代半导体成热点，7家龙头股全面梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/CvVGCnaaYEA6EHAL9-XyWQ",
            "accidents": ["2025年氮化镓业务营收占比超15%", "产能利用率维持高位"],
            "insights": ["聚焦消费电子快充、光伏逆变器领域", "拓展新能源汽车车载快充场景", "受益于下游需求爆发"],
            "key_metrics": ["氮化镓业务营收占比超15%", "产能利用率维持高位"],
            "target_valuation": []
        }]
    },
    {
        "code": "600745",
        "name": "闻泰科技",
        "board": "SH",
        "industry": "电子-消费电子-消费电子",
        "concepts": ["第三代半导体", "碳化硅功率模块", "氮化镓射频器件", "半导体模块", "5G"],
        "products": ["碳化硅功率模块", "氮化镓射频器件", "半导体器件"],
        "core_business": ["碳化硅功率模块研发制造", "氮化镓射频器件", "芯片设计", "封装测试"],
        "industry_position": ["半导体模块整合龙头", "具备芯片设计、封装测试一体化能力"],
        "chain": ["第三代半导体-中游-器件/模块"],
        "partners": [],
        "mention_count": 1,
        "articles": [{
            "title": "第三代半导体成热点，7家龙头股全面梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/CvVGCnaaYEA6EHAL9-XyWQ",
            "accidents": ["2025年第三代半导体相关业务营收占比超16%"],
            "insights": ["通过整合产业链资源，提升模块竞争力", "推进碳化硅模块国产化替代", "适配14英寸材料升级带来的成本优势"],
            "key_metrics": ["第三代半导体相关业务营收占比超16%"],
            "target_valuation": []
        }]
    }
]

def main():
    """主函数：批量添加个股"""
    print("🚀 从第三代半导体文章提取7只个股信息到投研数据库...\n")
    
    updater = IncrementalUpdater(base_dir=str(Path(__file__).parent / "data" / "master"))
    
    added_count = 0
    updated_count = 0
    
    for stock in stocks_to_add:
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
    print(f"\n📊 涉及文章: 第三代半导体成热点，7家龙头股全面梳理")

if __name__ == "__main__":
    main()
