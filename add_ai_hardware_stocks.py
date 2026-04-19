#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从AI硬件相关微信公众号文章提取的个股信息添加到投研数据库"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / ".trae" / "skills" / "wechat-fetch-research-embedded" / "scripts"))

from incremental_update import IncrementalUpdater

# 文章1: 芯碁微装调研纪要 - PCB曝光机/先进封装/激光钻
stocks_article_1 = [
    {
        "code": "688630",
        "name": "芯碁微装",
        "board": "SH",
        "industry": "电子-专用设备-半导体设备",
        "concepts": ["PCB曝光机", "先进封装", "激光直写", "二氧化碳激光钻", "硅桥", "半导体设备"],
        "products": ["PCB曝光机", "先进封装设备", "激光直写设备", "二氧化碳激光钻", "硅桥产品"],
        "core_business": ["PCB曝光机制造", "先进封装设备", "激光直写技术", "激光钻孔设备"],
        "industry_position": ["PCB曝光机国内龙头", "先进封装设备领先厂商"],
        "chain": ["半导体-上游-设备", "PCB-上游-曝光设备", "先进封装-上游-设备"],
        "partners": ["鹏鼎控股", "深南电路"],
        "mention_count": 1,
        "articles": [{
            "title": "芯碁微装调研纪要",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/TvXrpqjooxTOgmGBP2OB3g",
            "accidents": ["2026年一季度新签订单接近9亿元，创公司成立11年来单季度历史新高", "首次一季度营收、净利润双双环比四季度正增长，净利润同比翻倍以上", "先进封装硅桥产品量产时间提前至2026年Q3初", "大客户产能上修幅度超两倍"],
            "insights": ["PCB曝光机每周交付上限25台、3月已近满产", "先进封装2027年60台交付上限已提前备料30套", "2026年全球二氧化碳激光钻需求接近2000台，供给缺口超1000台", "鹏鼎+深南合计公告投资超460亿元，直接决定曝光机未来2-3年需求能见度", "2026年曝光机计划交付900-1000台（较2025年翻倍），单价已涨至200万元以上"],
            "key_metrics": ["一季度新签订单接近9亿元", "在手订单约7亿元", "经营现金流超1亿元", "PCB曝光机每周交付上限25台", "先进封装2027年交付上限60台", "2026年曝光机计划交付900-1000台", "2027年收入增速目标不低于50%"],
            "target_valuation": []
        }]
    }
]

# 文章2: 精智达 - 存储芯片测试设备
stocks_article_2 = [
    {
        "code": "688627",
        "name": "精智达",
        "board": "SH",
        "industry": "电子-专用设备-半导体测试设备",
        "concepts": ["存储芯片测试", "DRAM测试", "HBM测试", "探针卡", "半导体设备", "国产替代"],
        "products": ["MEMS探针卡", "DRAM CP/FT测试机", "老化测试及修复设备", "高速DRAM FT测试机", "通用测试验证系统(UDS)"],
        "core_business": ["新型显示器件检测设备", "半导体存储器件测试设备", "DRAM测试解决方案"],
        "industry_position": ["存储芯片测试设备领先厂商", "长鑫存储核心供应商"],
        "chain": ["半导体-上游-测试设备", "存储芯片-上游-测试机", "DRAM-上游-检测设备"],
        "partners": ["长鑫存储", "睿力集成", "沛顿科技", "晋华集成", "京东方", "TCL科技", "维信诺", "深天马"],
        "mention_count": 1,
        "articles": [{
            "title": "她是不是存储芯片涨价的卖铲人",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/6M7GZoJuUGUP7nIrzxDlMQ",
            "accidents": ["公布高达13亿客户订单", "爱德万交付周期拉长至18个月以上，超过2000台订单无法承接"],
            "insights": ["高端高速测试机是DRAM存储最大卡点", "HBM和COWOS的引入使测试轮次显著提升，进一步拉动测试机台需求", "长鑫作为大陆最大DRAM原厂，加速国内测试机设备验证并放量下单的诉求极强", "预计大陆存储测试机需求到2028年将达到150亿元以上，其中超过65%来自于长鑫需求"],
            "key_metrics": ["公布客户订单13亿元", "爱德万交付周期18个月以上", "2000台以上订单无法承接", "大陆存储测试机需求2028年达150亿元", "长鑫需求占比超过65%"],
            "target_valuation": ["按照50%份额测算，25-30%净利率，展望15亿利润", "配套业务20亿收入，显示业务10亿收入，5-6亿利润贡献", "合计20亿利润，给予中期40倍估值，市值展望800亿元"]
        }]
    }
]

# 文章3: AI硬件公司业绩整理 - 大族数控/中际旭创
stocks_article_3 = [
    {
        "code": "301200",
        "name": "大族数控",
        "board": "SZ",
        "industry": "电子-专用设备-PCB设备",
        "concepts": ["PCB设备", "钻孔设备", "机械钻孔", "激光钻孔", "AI硬件", "铲子股"],
        "products": ["钻孔类设备", "检测类设备", "机械钻孔机", "激光钻孔机"],
        "core_business": ["PCB钻孔设备", "PCB检测设备", "PCB制造设备"],
        "industry_position": ["PCB产业链上游核心铲子股", "PCB钻孔设备龙头"],
        "chain": ["PCB-上游-钻孔设备", "AI硬件-上游-PCB设备"],
        "partners": [],
        "mention_count": 1,
        "articles": [{
            "title": "AI硬件公司业绩整理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/sUw3Xbmas_LY76Fj6m7nXQ",
            "accidents": ["2025年全年实现营收57.73亿元，同比+72.68%", "归母净利润8.24亿元，同比+173.68%", "2025Q4合同负债198.42亿元，环比Q3增长355.82%", "2025Q4新增合同负债154.89亿元"],
            "insights": ["PCB钻孔是所有设备中通胀最明显环节", "公司在PCB机械钻孔/激光钻孔领域均已彻底打开成长空间", "钻孔类设备收入41.67亿元，同比+98%，占公司收入比重72.19%", "毛利率同比+8.7pct，贡献公司主要营收利润来源"],
            "key_metrics": ["营收57.73亿元同比+72.68%", "归母净利润8.24亿元同比+173.68%", "扣非归母净利润8.21亿元同比+290.92%", "毛利率35.12%同比+7.01pct", "合同负债198.42亿元环比+355.82%", "钻孔类设备收入41.67亿元同比+98%"],
            "target_valuation": []
        }]
    },
    {
        "code": "300308",
        "name": "中际旭创",
        "board": "SZ",
        "industry": "通信-通信设备-光通信设备",
        "concepts": ["光模块", "800G", "1.6T", "硅光模块", "NPO", "CPO", "OCS", "AI算力"],
        "products": ["800G光模块", "1.6T光模块", "硅光模块", "NPO模块", "CPO组件", "OCS光交换机"],
        "core_business": ["光模块研发制造", "硅光技术", "光电互联解决方案"],
        "industry_position": ["全球光模块龙头", "AI光模块核心供应商"],
        "chain": ["光通信-中游-光模块", "AI算力-上游-光互联"],
        "partners": [],
        "mention_count": 1,
        "articles": [{
            "title": "AI硬件公司业绩整理",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/sUw3Xbmas_LY76Fj6m7nXQ",
            "accidents": ["2025年全年实现归母净利润107.97亿元", "2025Q4收入132.35亿元，环比+29.56%", "2025Q4归母净利润36.65亿元，环比+16.85%", "毛利率44.48%，环比+1.69pct"],
            "insights": ["1.6T、硅光模块等高利润产品放量带来利润水平提升", "2026年800G/1.6T需求量预计6000万+/2500万+只", "2027年行业需求翻倍且置信度大幅提升", "2028年客户锁定光芯片产能时显示需求再翻倍增长", "2027年是光入柜内元年，NPO行业需求实现0-1放量，总量超过1000万只", "卡位ELSFP模组、Fiber Kit、FAU等多个CPO核心价值环节"],
            "key_metrics": ["归母净利润107.97亿元", "Q4收入132.35亿元环比+29.56%", "Q4归母净利润36.65亿元环比+16.85%", "毛利率44.48%环比+1.69pct", "2026年800G/1.6T需求6000万+/2500万+只"],
            "target_valuation": []
        }]
    }
]

# 文章4: 长芯博创 - 光通信/高速铜缆
stocks_article_4 = [
    {
        "code": "300548",
        "name": "长芯博创",
        "board": "SZ",
        "industry": "通信-通信设备-光通信设备",
        "concepts": ["光通信", "高速铜缆", "AEC", "DAC", "AOC", "硅光模块", "光模块", "MPO连接器"],
        "products": ["高速铜缆(AEC/DAC/ACC)", "有源光缆(AOC)", "硅光模块(400G/800G/1.6T)", "MPO连接器", "光连接开关(OCS)"],
        "core_business": ["光通信器件", "高速铜缆", "硅光模块", "有源光缆", "光连接产品"],
        "industry_position": ["光通信+AI算力互联核心标的", "全球AOC/AEC份额第三", "MPO连接器全球第二", "国内首家PLC光分路器公司"],
        "chain": ["光通信-中游-光器件", "AI算力-上游-高速互联", "数据中心-上游-连接方案"],
        "partners": ["谷歌", "Meta", "微软", "英伟达", "中国移动", "联通", "电信", "华为", "中兴"],
        "mention_count": 1,
        "articles": [{
            "title": "长坡厚雪之长芯博创",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/jkXyv51CN_PFuCUq54cZaw",
            "accidents": ["2025年全年营业总收入25.33亿元，同比增长44.93%", "归母净利润3.349亿元，同比增长364.62%", "2025年境外收入15.05亿元，占总营收59.44%，同比增长94.29%", "印尼基地二期投产"],
            "insights": ["1.6T AEC领先行业1-2年，适配GPU集群短距互联", "收购德国Silicon Line掌握硅光引擎、SerDes、TIA核心芯片", "国内首条1.6T硅光模块产线，良率92%（行业领先）", "800G批量供货海外云厂商", "长芯盛自研多通道光电收发芯片，量产良率超99.5%", "光连接开关(OCS)全球份额16%，数据中心高密度布线国内第一", "谷歌占长芯盛收入超40%"],
            "key_metrics": ["营收25.33亿元同比+44.93%", "归母净利润3.349亿元同比+364.62%", "境外收入15.05亿元占比59.44%", "10G PON OLT模块国内份额28%排名第一", "DWDM-AWG国内25%排名第二", "全球AOC/AEC份额第三", "MPO连接器全球第二", "1.6T硅光模块良率92%"],
            "target_valuation": ["券商预测2026年利润为8.03亿元", "当前市值652.54亿元，市盈率194.87倍"]
        }]
    }
]

def main():
    """主函数：批量添加个股"""
    print("🚀 从AI硬件相关文章提取个股信息到投研数据库...\n")
    
    updater = IncrementalUpdater(base_dir=str(Path(__file__).parent / "data" / "master"))
    
    all_stocks = stocks_article_1 + stocks_article_2 + stocks_article_3 + stocks_article_4
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
    print(f"   1. 芯碁微装调研纪要")
    print(f"   2. 精智达：存储芯片测试设备")
    print(f"   3. AI硬件公司业绩整理（大族数控/中际旭创）")
    print(f"   4. 长坡厚雪之长芯博创")

if __name__ == "__main__":
    main()
