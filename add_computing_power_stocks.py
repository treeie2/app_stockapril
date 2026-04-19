#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从算力租赁文章提取的个股信息添加到投研数据库"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / ".trae" / "skills" / "wechat-fetch-research-embedded" / "scripts"))

from incremental_update import IncrementalUpdater

# 算力租赁领域10家公司
stocks_to_add = [
    {
        "code": "300442",
        "name": "润泽科技",
        "board": "SZ",
        "industry": "计算机-IT服务-数据中心",
        "concepts": ["算力租赁", "AIDC", "智算中心", "液冷", "字节跳动", "算电协同"],
        "products": ["智算中心", "IDC服务", "液冷解决方案"],
        "core_business": ["园区级IDC与AIDC运营", "智算基础设施", "算力调度平台"],
        "industry_position": ["全国算力枢纽布局绝对龙头", "国内领先的园区级IDC与AIDC运营商", "唯一通过NCP认证的第三方AIDC运营商"],
        "chain": ["算力租赁-中游-智算中心", "AI基础设施-中游-数据中心"],
        "partners": ["字节跳动"],
        "mention_count": 1,
        "articles": [{
            "title": "算力租赁领域最有价值的10家公司",
            "date": "2026-04-19",
            "source": "https://mp.weixin.qq.com/s/OL-WAgIVrrRo-mJIenntmg",
            "accidents": ["2025年度预计实现归母净利润50-53亿元，同比增长179%-196%", "成功发行国内首单数据中心REITs", "交付行业领先的单体100MW智算中心"],
            "insights": ["已在京津冀、长三角、粤港澳大湾区建成7个AIDC集群，共61栋智算中心，机柜总规模约32万架", "深度服务字节跳动等头部互联网巨头，上架率长期保持90%以上", "大规模应用液冷技术，PUE指标处于行业尖端水平", "算电协同首次入规，算力中心将从被动用电者转变为电网的柔性负荷"],
            "key_metrics": ["市值约1522亿元", "7个AIDC集群61栋智算中心", "机柜总规模约32万架", "上架率90%以上", "归母净利润50-53亿元同比增长179%-196%"],
            "target_valuation": []
        }]
    },
    {
        "code": "603629",
        "name": "利通电子",
        "board": "SH",
        "industry": "计算机-IT服务-算力租赁",
        "concepts": ["算力租赁", "英伟达", "腾讯", "AI云伙伴"],
        "products": ["AI算力租赁", "GPU云服务"],
        "core_business": ["AI算力租赁服务", "GPU云算力调度"],
        "industry_position": ["英伟达顶级AI云伙伴", "算力规模领跑者", "可调度算力规模行业第一"],
        "chain": ["算力租赁-中游-算力服务", "AI基础设施-中游-算力运营"],
        "partners": ["英伟达", "腾讯"],
        "mention_count": 1,
        "articles": [{
            "title": "算力租赁领域最有价值的10家公司",
            "date": "2026-04-19",
            "source": "https://mp.weixin.qq.com/s/OL-WAgIVrrRo-mJIenntmg",
            "accidents": ["与英伟达深度绑定获优先供货权", "与腾讯签订50亿3年期大单"],
            "insights": ["英伟达顶级AI云伙伴，可调度算力规模行业第一", "与腾讯签订50亿3年期大单锁定长期收益", "毛利率超60%"],
            "key_metrics": ["与腾讯签订50亿3年期大单", "毛利率超60%"],
            "target_valuation": []
        }]
    },
    {
        "code": "002229",
        "name": "鸿博股份",
        "board": "SZ",
        "industry": "计算机-IT服务-算力租赁",
        "concepts": ["算力租赁", "英伟达", "智算中心", "GPU租赁"],
        "products": ["高端GPU算力租赁", "智算中心服务"],
        "core_business": ["高端算力租赁", "GPU集群运营", "智算中心建设"],
        "industry_position": ["英伟达生态核心企业", "高端算力租赁标杆", "A股最接近纯GPU租赁商的公司"],
        "chain": ["算力租赁-中游-算力服务", "AI基础设施-中游-算力运营"],
        "partners": ["英伟达"],
        "mention_count": 1,
        "articles": [{
            "title": "算力租赁领域最有价值的10家公司",
            "date": "2026-04-19",
            "source": "https://mp.weixin.qq.com/s/OL-WAgIVrrRo-mJIenntmg",
            "accidents": ["北京智算中心部署高端GPU集群", "已落地超4000P算力"],
            "insights": ["英伟达生态标杆企业", "A股最接近纯GPU租赁商的公司"],
            "key_metrics": ["已落地超4000P算力"],
            "target_valuation": []
        }]
    },
    {
        "code": "300857",
        "name": "协创数据",
        "board": "SZ",
        "industry": "计算机-IT服务-算力租赁",
        "concepts": ["算力租赁", "AI算力", "大模型训练", "次新"],
        "products": ["AI算力服务", "高性能算力租赁"],
        "core_business": ["AI算力服务", "大模型训练算力租赁"],
        "industry_position": ["AI算力服务新锐", "次新算力黑马"],
        "chain": ["算力租赁-中游-算力服务", "AI基础设施-中游-算力运营"],
        "partners": [],
        "mention_count": 1,
        "articles": [{
            "title": "算力租赁领域最有价值的10家公司",
            "date": "2026-04-19",
            "source": "https://mp.weixin.qq.com/s/OL-WAgIVrrRo-mJIenntmg",
            "accidents": ["与头部AI公司深度合作", "订单饱满"],
            "insights": ["专注为大模型训练提供高性能算力租赁", "轻资产运营，周转效率高"],
            "key_metrics": [],
            "target_valuation": []
        }]
    },
    {
        "code": "002602",
        "name": "世纪华通",
        "board": "SZ",
        "industry": "传媒-游戏-游戏服务",
        "concepts": ["算力租赁", "游戏", "腾讯", "数据中心", "AI训练"],
        "products": ["游戏运营", "数据中心", "算力集群"],
        "core_business": ["游戏业务", "自建数据中心", "算力集群运营"],
        "industry_position": ["游戏巨头跨界算力", "腾讯深度合作伙伴"],
        "chain": ["游戏-下游-游戏运营", "算力租赁-中游-算力服务"],
        "partners": ["腾讯"],
        "mention_count": 1,
        "articles": [{
            "title": "算力租赁领域最有价值的10家公司",
            "date": "2026-04-19",
            "source": "https://mp.weixin.qq.com/s/OL-WAgIVrrRo-mJIenntmg",
            "accidents": ["自建数据中心+算力集群", "长三角/粤港澳资源优势明显"],
            "insights": ["算力规模稳步增长，重点布局AI训练场景", "2025年算力业务贡献显著增量"],
            "key_metrics": ["2025年算力业务贡献显著增量"],
            "target_valuation": []
        }]
    },
    {
        "code": "002261",
        "name": "拓维信息",
        "board": "SZ",
        "industry": "计算机-软件开发-IT服务",
        "concepts": ["算力租赁", "华为昇腾", "英伟达", "国产算力", "自主可控"],
        "products": ["算力服务", "国产算力解决方案", "AI算力平台"],
        "core_business": ["华为昇腾+英伟达双轮驱动", "国产算力自主可控", "算力调度服务"],
        "industry_position": ["国产算力领军", "华为昇腾核心合作伙伴"],
        "chain": ["算力租赁-中游-算力服务", "AI基础设施-中游-算力运营"],
        "partners": ["华为", "英伟达"],
        "mention_count": 1,
        "articles": [{
            "title": "算力租赁领域最有价值的10家公司",
            "date": "2026-04-19",
            "source": "https://mp.weixin.qq.com/s/OL-WAgIVrrRo-mJIenntmg",
            "accidents": ["可调度算力规模约1.2万P", "国产算力占比超40%"],
            "insights": ["华为昇腾+英伟达双轮驱动，国产算力自主可控标杆", "客户覆盖互联网、金融、政务等多领域"],
            "key_metrics": ["可调度算力规模约1.2万P", "国产算力占比超40%"],
            "target_valuation": []
        }]
    },
    {
        "code": "603220",
        "name": "中贝通信",
        "board": "SH",
        "industry": "通信-通信服务-通信工程",
        "concepts": ["算力租赁", "华为", "英伟达", "通信工程", "智算中心"],
        "products": ["通信工程服务", "算力租赁", "智算中心运营"],
        "core_business": ["通信工程服务", "算力租赁", "智算中心建设运营"],
        "industry_position": ["通信工程服务商跨界算力租赁", "华为+英伟达双技术路线布局"],
        "chain": ["通信-中游-通信服务", "算力租赁-中游-算力服务"],
        "partners": ["华为", "英伟达"],
        "mention_count": 1,
        "articles": [{
            "title": "算力租赁领域最有价值的10家公司",
            "date": "2026-04-19",
            "source": "https://mp.weixin.qq.com/s/OL-WAgIVrrRo-mJIenntmg",
            "accidents": ["已投产算力1.8万P", "2026年底计划扩至3万P"],
            "insights": ["华为+英伟达双路线布局", "客户包括互联网大厂与AI创业公司"],
            "key_metrics": ["已投产算力1.8万P", "2026年底计划扩至3万P"],
            "target_valuation": []
        }]
    }
]

def main():
    """主函数：批量添加个股"""
    print("🚀 从算力租赁文章提取个股信息到投研数据库...\n")
    
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
    print(f"\n📊 涉及文章: 算力租赁领域最有价值的10家公司")

if __name__ == "__main__":
    main()
