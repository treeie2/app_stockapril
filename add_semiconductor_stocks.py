#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从半导体全产业链文章提取10只个股信息添加到投研数据库"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / ".trae" / "skills" / "wechat-fetch-research-embedded" / "scripts"))

from incremental_update import IncrementalUpdater

# 半导体全产业链10家核心龙头企业
stocks_to_add = [
    {
        "code": "002371",
        "name": "北方华创",
        "board": "SZ",
        "industry": "电子-半导体设备-半导体设备",
        "concepts": ["半导体设备", "刻蚀设备", "薄膜沉积", "清洗设备", "热处理设备", "国产替代", "14nm", "7nm"],
        "products": ["刻蚀设备", "薄膜沉积设备", "清洗设备", "热处理设备", "半导体前道设备"],
        "core_business": ["半导体前道全流程设备", "刻蚀设备", "薄膜沉积", "清洗设备", "热处理设备"],
        "industry_position": ["国内唯一前道全流程设备龙头", "国内覆盖刻蚀、沉积、清洗、热处理等半导体前道全流程的设备企业", "14nm设备稳定供货，7nm设备研发突破", "部分产品打入台积电、三星供应链"],
        "chain": ["半导体-上游-设备", "晶圆制造-上游-前道设备"],
        "partners": ["台积电", "三星"],
        "mention_count": 1,
        "articles": [{
            "title": "业绩为王！电子半导体全产业链：10家核心龙头企业深度梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/osXuox5ED3O_dMFXOntgdw",
            "accidents": ["预计2025年归母净利润96-100亿元，同比增长45%-55%", "新增订单285亿元，订单排至2027年"],
            "insights": ["产品贯通晶圆制造全环节，同时布局泛半导体、新能源装备", "形成独一无二的全产业链覆盖能力", "技术比肩国际巨头，是国产设备替代的绝对标杆"],
            "key_metrics": ["预计归母净利润96-100亿元同比+45%-55%", "新增订单285亿元", "订单排至2027年"],
            "target_valuation": []
        }]
    },
    {
        "code": "688012",
        "name": "中微公司",
        "board": "SH",
        "industry": "电子-半导体设备-半导体设备",
        "concepts": ["半导体设备", "刻蚀设备", "介质刻蚀", "MOCVD", "5nm", "3nm", "2nm", "台积电"],
        "products": ["刻蚀设备", "介质刻蚀机", "MOCVD设备"],
        "core_business": ["刻蚀设备研发制造", "介质刻蚀设备", "MOCVD设备"],
        "industry_position": ["全球第四大刻蚀设备商", "全球介质刻蚀设备龙头", "台积电3nm、2nm制程扩产刚需供应商", "先进制程国产替代标杆"],
        "chain": ["半导体-上游-设备", "晶圆制造-上游-刻蚀设备"],
        "partners": ["台积电"],
        "mention_count": 1,
        "articles": [{
            "title": "业绩为王！电子半导体全产业链：10家核心龙头企业深度梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/osXuox5ED3O_dMFXOntgdw",
            "accidents": ["2025年营收123.85亿元，同比增长36.62%", "归母净利润21.11亿元，同比增长30.69%"],
            "insights": ["5nm介质刻蚀机通过国际大厂验证", "MOCVD设备市占率超60%", "毛利率稳定48%以上，国内无直接竞争对手"],
            "key_metrics": ["营收123.85亿元同比+36.62%", "归母净利润21.11亿元同比+30.69%", "MOCVD市占率超60%", "毛利率48%+"],
            "target_valuation": []
        }]
    },
    {
        "code": "688981",
        "name": "中芯国际",
        "board": "SH",
        "industry": "电子-半导体-晶圆代工",
        "concepts": ["晶圆代工", "成熟制程", "先进制程", "28nm", "14nm", "国产替代", "大基金"],
        "products": ["晶圆代工服务", "28nm制程", "14nm制程"],
        "core_business": ["晶圆代工", "成熟制程芯片制造", "先进制程研发"],
        "industry_position": ["中国大陆规模最大、技术最全面的晶圆代工企业", "国内80%以上成熟制程芯片依赖其产能", "大基金重点持股"],
        "chain": ["半导体-中游-晶圆代工", "芯片制造-中游-代工服务"],
        "partners": ["华为", "高通", "联发科"],
        "mention_count": 1,
        "articles": [{
            "title": "业绩为王！电子半导体全产业链：10家核心龙头企业深度梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/osXuox5ED3O_dMFXOntgdw",
            "accidents": ["2025年营收673.23亿元，同比增长16.49%", "归母净利润50.41亿元，同比增长36.29%"],
            "insights": ["覆盖28nm成熟制程与14nm先进制程（良率超90%）", "华为、高通、联发科等头部企业核心供应商", "享受政策与产能双重红利"],
            "key_metrics": ["营收673.23亿元同比+16.49%", "归母净利润50.41亿元同比+36.29%", "14nm良率超90%"],
            "target_valuation": []
        }]
    },
    {
        "code": "688347",
        "name": "华虹公司",
        "board": "SH",
        "industry": "电子-半导体-晶圆代工",
        "concepts": ["晶圆代工", "特色工艺", "功率半导体", "MCU", "传感器", "8英寸", "12英寸"],
        "products": ["晶圆代工服务", "功率半导体代工", "MCU代工", "传感器代工"],
        "core_business": ["特色工艺晶圆代工", "功率半导体制造", "MCU制造", "传感器制造"],
        "industry_position": ["国内特色工艺晶圆代工龙头", "汽车电子、工业控制芯片核心制造服务商", "产能规模国内第二"],
        "chain": ["半导体-中游-晶圆代工", "功率半导体-中游-制造"],
        "partners": [],
        "mention_count": 1,
        "articles": [{
            "title": "业绩为王！电子半导体全产业链：10家核心龙头企业深度梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/osXuox5ED3O_dMFXOntgdw",
            "accidents": ["2025年营收172.91亿元，同比增长20.18%", "归母净利润3.77亿元"],
            "insights": ["上海、无锡、金桥三大基地协同", "8英寸、12英寸产线产能利用率持续超100%", "聚焦功率半导体、MCU、传感器等成熟制程"],
            "key_metrics": ["营收172.91亿元同比+20.18%", "归母净利润3.77亿元", "产能利用率超100%"],
            "target_valuation": []
        }]
    },
    {
        "code": "600584",
        "name": "长电科技",
        "board": "SH",
        "industry": "电子-半导体-封装测试",
        "concepts": ["封装测试", "先进封装", "HBM封装", "Chiplet", "AI芯片"],
        "products": ["封装测试服务", "HBM封装", "Chiplet封装", "先进封装"],
        "core_business": ["封装测试", "先进封装", "HBM封装", "Chiplet方案"],
        "industry_position": ["全球封测行业TOP3、国内第一", "HBM封装技术全球第一梯队", "国内封测产能规模最大"],
        "chain": ["半导体-中游-封测", "先进封装-中游-封装服务"],
        "partners": ["英伟达", "AMD", "海力士"],
        "mention_count": 1,
        "articles": [{
            "title": "业绩为王！电子半导体全产业链：10家核心龙头企业深度梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/osXuox5ED3O_dMFXOntgdw",
            "accidents": ["机构预计2025年营收420亿元，同比增长16.8%", "预计归母净利润16.5亿元"],
            "insights": ["Chiplet方案适配AI芯片高密度集成需求", "深度绑定英伟达、AMD、海力士等全球巨头", "先进封装产能利用率超90%"],
            "key_metrics": ["预计营收420亿元同比+16.8%", "预计归母净利润16.5亿元", "先进封装产能利用率超90%"],
            "target_valuation": []
        }]
    },
    {
        "code": "002156",
        "name": "通富微电",
        "board": "SZ",
        "industry": "电子-半导体-封装测试",
        "concepts": ["封装测试", "先进封装", "Chiplet", "HBM封装", "AMD", "AI芯片"],
        "products": ["封装测试服务", "Chiplet封装", "HBM封装", "AI芯片封测"],
        "core_business": ["封装测试", "先进封装", "Chiplet封装", "HBM封装"],
        "industry_position": ["国内封测龙头", "AMD全球核心封测唯一合作伙伴", "Chiplet、HBM封装技术国内领先"],
        "chain": ["半导体-中游-封测", "先进封装-中游-封装服务"],
        "partners": ["AMD"],
        "mention_count": 1,
        "articles": [{
            "title": "业绩为王！电子半导体全产业链：10家核心龙头企业深度梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/osXuox5ED3O_dMFXOntgdw",
            "accidents": ["预计2025年归母净利润11-13.5亿元，同比增长62.34%-99.24%"],
            "insights": ["AI芯片封测订单饱满", "先进封装产能持续扩张", "直接受益AI算力爆发", "技术壁垒与客户壁垒双重巩固"],
            "key_metrics": ["预计归母净利润11-13.5亿元同比+62.34%-99.24%"],
            "target_valuation": []
        }]
    },
    {
        "code": "605358",
        "name": "立昂微",
        "board": "SH",
        "industry": "电子-半导体材料-硅片",
        "concepts": ["半导体硅片", "12英寸硅片", "功率器件", "模拟芯片", "国产替代"],
        "products": ["半导体硅片", "12英寸硅片", "功率器件", "模拟芯片"],
        "core_business": ["半导体硅片研发生产", "功率器件", "模拟芯片"],
        "industry_position": ["国内半导体硅片龙头", "12英寸硅片量产突破海外垄断"],
        "chain": ["半导体-上游-材料", "硅片-中游-制造"],
        "partners": ["中芯国际", "华虹"],
        "mention_count": 1,
        "articles": [{
            "title": "业绩为王！电子半导体全产业链：10家核心龙头企业深度梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/osXuox5ED3O_dMFXOntgdw",
            "accidents": ["2025年营收35.95亿元，同比增长16.26%", "归母净利润亏损1.21亿元，同比减亏54.47%"],
            "insights": ["12英寸硅片量产突破海外垄断", "硅片业务深度绑定中芯国际、华虹", "功率器件受益新能源汽车、光伏爆发", "形成全产业链协同"],
            "key_metrics": ["营收35.95亿元同比+16.26%", "亏损1.21亿元同比减亏54.47%"],
            "target_valuation": []
        }]
    },
    {
        "code": "688126",
        "name": "沪硅产业",
        "board": "SH",
        "industry": "电子-半导体材料-硅片",
        "concepts": ["半导体硅片", "12英寸大硅片", "8英寸硅片", "国产替代", "大基金"],
        "products": ["12英寸大硅片", "8英寸硅片", "半导体硅片"],
        "core_business": ["半导体硅片研发生产", "12英寸大硅片", "8英寸硅片"],
        "industry_position": ["国内12英寸大硅片龙头", "国内晶圆厂核心硅片供应商", "大基金重点持股"],
        "chain": ["半导体-上游-材料", "硅片-中游-制造"],
        "partners": [],
        "mention_count": 1,
        "articles": [{
            "title": "业绩为王！电子半导体全产业链：10家核心龙头企业深度梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/osXuox5ED3O_dMFXOntgdw",
            "accidents": ["2025年营收37.16亿元，同比增长9.69%", "归母净利润亏损14.76亿元"],
            "insights": ["产品覆盖12英寸、8英寸硅片", "国内12英寸硅片国产化率不足5%，公司替代空间巨大", "订单排至2027年"],
            "key_metrics": ["营收37.16亿元同比+9.69%", "亏损14.76亿元", "订单排至2027年"],
            "target_valuation": []
        }]
    },
    {
        "code": "688008",
        "name": "澜起科技",
        "board": "SH",
        "industry": "电子-半导体-芯片设计",
        "concepts": ["内存接口芯片", "DDR5", "HBM3", "AI服务器", "内存接口芯片"],
        "products": ["内存接口芯片", "DDR5接口芯片", "HBM3控制器"],
        "core_business": ["内存接口芯片设计", "DDR5全品类接口芯片", "HBM控制器"],
        "industry_position": ["全球唯一覆盖DDR5全品类接口芯片的企业", "DDR5接口芯片全球市占率46%", "全球内存接口芯片垄断者"],
        "chain": ["半导体-设计-芯片设计", "内存接口-上游-接口芯片"],
        "partners": [],
        "mention_count": 1,
        "articles": [{
            "title": "业绩为王！电子半导体全产业链：10家核心龙头企业深度梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/osXuox5ED3O_dMFXOntgdw",
            "accidents": ["2025年营收54.56亿元，同比增长49.94%", "归母净利润22.36亿元，同比增长58.35%"],
            "insights": ["HBM3控制器完成认证", "AI服务器单台需求是传统服务器3-5倍，直接受益算力爆发", "毛利率长期超70%，技术壁垒不可复制"],
            "key_metrics": ["营收54.56亿元同比+49.94%", "归母净利润22.36亿元同比+58.35%", "DDR5全球市占率46%", "毛利率超70%"],
            "target_valuation": []
        }]
    },
    {
        "code": "603986",
        "name": "兆易创新",
        "board": "SH",
        "industry": "电子-半导体-芯片设计",
        "concepts": ["存储芯片", "NOR Flash", "MCU", "利基DRAM", "车规级MCU", "AI服务器"],
        "products": ["NOR Flash", "MCU", "利基DRAM", "LPDDR5X"],
        "core_business": ["存储芯片设计", "MCU设计", "NOR Flash", "利基DRAM"],
        "industry_position": ["国内存储+MCU双领域龙头", "NOR Flash全球市占前三", "利基DRAM国内第一"],
        "chain": ["半导体-设计-芯片设计", "存储-上游-存储芯片", "MCU-上游-MCU芯片"],
        "partners": [],
        "mention_count": 1,
        "articles": [{
            "title": "业绩为王！电子半导体全产业链：10家核心龙头企业深度梳理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/osXuox5ED3O_dMFXOntgdw",
            "accidents": ["2025年营收92.03亿元，同比增长25.12%", "归母净利润16.48亿元，同比增长49.47%"],
            "insights": ["车规级MCU打入头部车企", "2025年存储周期反转", "自研LPDDR5X对接AI服务器需求", "全品类布局抗风险能力极强"],
            "key_metrics": ["营收92.03亿元同比+25.12%", "归母净利润16.48亿元同比+49.47%", "NOR Flash全球市占前三", "利基DRAM国内第一"],
            "target_valuation": []
        }]
    }
]

def main():
    """主函数：批量添加个股"""
    print("🚀 从半导体全产业链文章提取10只个股信息到投研数据库...\n")
    
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
    print(f"\n📊 涉及文章: 业绩为王！电子半导体全产业链：10家核心龙头企业深度梳理")

if __name__ == "__main__":
    main()
