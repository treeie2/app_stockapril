#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量添加个股信息到投研数据库"""

import json
import sys
from datetime import datetime
from pathlib import Path

# 添加技能脚本路径
sys.path.insert(0, str(Path(__file__).parent / ".trae" / "skills" / "wechat-fetch-research-embedded" / "scripts"))

from incremental_update import IncrementalUpdater

# 定义所有要添加的个股数据
stocks_to_add = [
    {
        "code": "600986",
        "name": "浙文互联",
        "board": "SH",
        "industry": "传媒-广告营销-营销代理",
        "concepts": ["AI营销", "数字藏品", "元宇宙", "字节跳动", "数字人", "区块链"],
        "products": ["数字营销服务", "数字藏品运营", "数字人商业化"],
        "core_business": ["数字营销", "数字藏品区块链技术与运营", "数字人商业化", "AI营销"],
        "industry_position": ["浙江国资旗下核心平台", "浙江文交所二股东", "字节跳动核心代理商"],
        "chain": ["传媒-中游-营销代理", "AI应用-下游-营销"],
        "partners": ["字节跳动", "巨量引擎"],
        "articles": [{
            "title": "浙江国资旗下核心平台，承接春晚数字藏品运营",
            "date": "2026-04-19",
            "source": "manual_input",
            "accidents": ["承接马年春晚数字藏品区块链技术与运营", "接入字节豆包相关系统拿下春晚营销订单"],
            "insights": ["与巨量引擎合作的数字人商业化成果显著，2025年消耗量同比5倍增长", "作为字节跳动核心代理商，叠加元宇宙与数字资产布局，短期热度与长期发展逻辑清晰"],
            "key_metrics": ["2025年数字人消耗量同比5倍增长"],
            "target_valuation": []
        }]
    },
    {
        "code": "300058",
        "name": "蓝色光标",
        "board": "SZ",
        "industry": "传媒-广告营销-营销代理",
        "concepts": ["AI营销", "出海业务", "智能体", "H股上市"],
        "products": ["BlueAI技术矩阵", "智能营销服务"],
        "core_business": ["AI营销", "出海营销服务", "智能体孵化"],
        "industry_position": ["AI营销领域先行者", "全球前十营销集团"],
        "chain": ["传媒-中游-营销代理", "AI应用-下游-营销"],
        "partners": [],
        "articles": [{
            "title": "AI营销领域先行者，BlueAI技术矩阵孵化100+垂直场景智能体",
            "date": "2026-04-19",
            "source": "manual_input",
            "accidents": ["BlueAI技术矩阵孵化100+垂直场景智能体", "推进H股上市引入战略投资者"],
            "insights": ["出海业务占比超80%，服务3000余家国际客户", "AI赋能与出海需求增长驱动业务持续扩张"],
            "key_metrics": ["出海业务占比超80%", "服务3000余家国际客户"],
            "target_valuation": []
        }]
    },
    {
        "code": "001267",
        "name": "汇绿生态",
        "board": "SZ",
        "industry": "建筑装饰-基础建设-园林工程",
        "concepts": ["光模块", "硅光技术", "CPO", "AI基建", "双主业"],
        "products": ["400G/800G硅光模块", "1.6T光模块"],
        "core_business": ["园林工程", "光模块制造", "硅光模块研发"],
        "industry_position": ["武汉钧恒具备400G/800G硅光模块批量生产能力"],
        "chain": ["通信设备-中游-光模块", "AI基础设施-上游-光通信"],
        "partners": [],
        "articles": [{
            "title": "转型光模块赛道，园林工程与光模块双主业",
            "date": "2026-04-19",
            "source": "manual_input",
            "accidents": ["控股子公司武汉钧恒具备400G/800G硅光模块批量生产能力", "1.6T产品已排产", "鄂州一期150万只/年产能即将投产"],
            "insights": ["二期及马来西亚海外基地持续落地，产能扩张节奏契合AI与数据中心建设带来的光模块需求增长"],
            "key_metrics": ["鄂州一期150万只/年产能", "400G/800G硅光模块批量生产", "1.6T产品已排产"],
            "target_valuation": []
        }]
    },
    {
        "code": "301377",
        "name": "鼎泰高科",
        "board": "SZ",
        "industry": "电子-元件-印制电路板",
        "concepts": ["PCB", "钻针", "具身机器人", "AI硬件", "泰国基地"],
        "products": ["PCB钻针", "精密部件"],
        "core_business": ["PCB钻针制造", "具身机器人核心精密部件"],
        "industry_position": ["PCB钻针订单充足"],
        "chain": ["电子-中游-PCB", "AI硬件-上游-零部件"],
        "partners": [],
        "articles": [{
            "title": "PCB钻针+机器人部件双曲线契合AI产业趋势",
            "date": "2026-04-19",
            "source": "manual_input",
            "accidents": ["钻针订单充足、均价稳中有升", "年内钻针总月产能将突破1亿支", "泰国基地进一步完善全球化布局"],
            "insights": ["受益于AI服务器等硬件升级带动的高端PCB需求激增", "子公司切入具身机器人核心精密部件领域"],
            "key_metrics": ["年内钻针总月产能将突破1亿支"],
            "target_valuation": []
        }]
    },
    {
        "code": "002498",
        "name": "汉缆股份",
        "board": "SZ",
        "industry": "电力设备-电网设备-线缆部件及其他",
        "concepts": ["特高压", "海缆", "海上风电", "电网升级", "双碳"],
        "products": ["高压电缆", "超高压电缆", "直流海底电缆"],
        "core_business": ["高压及超高压电缆制造", "海底电缆解决方案"],
        "industry_position": ["国内高压及超高压电缆核心供应商"],
        "chain": ["电力设备-中游-线缆", "新能源-上游-海缆"],
        "partners": [],
        "articles": [{
            "title": "推出±535kV直流海底电缆解决方案，适配全球海上风电需求",
            "date": "2026-04-19",
            "source": "manual_input",
            "accidents": ["推出±535kV直流海底电缆解决方案"],
            "insights": ["产品覆盖多领域，深度布局特高压、海底电缆等高端细分赛道", "紧密契合电网升级与新能源产业发展趋势，双碳目标下业务增长动力充足"],
            "key_metrics": ["±535kV直流海底电缆"],
            "target_valuation": []
        }]
    },
    {
        "code": "601168",
        "name": "西部矿业",
        "board": "SH",
        "industry": "有色金属-工业金属-铜",
        "concepts": ["铜", "有色金属", "新能源", "玉龙铜矿", "海外矿权"],
        "products": ["电解铜", "铜金属"],
        "core_business": ["铜矿开采", "电解铜生产"],
        "industry_position": ["青海国资控股的资源型企业", "拥有35万吨/年电解铜产能"],
        "chain": ["有色金属-上游-铜矿开采", "新能源-上游-铜材料"],
        "partners": [],
        "articles": [{
            "title": "玉龙铜矿三期投产将大幅提升铜产量",
            "date": "2026-04-19",
            "source": "manual_input",
            "accidents": ["玉龙铜矿三期投产后铜产量将大幅提升", "评估海外矿权收购机会"],
            "insights": ["铜金属资源储量丰富", "在新能源产业带动铜需求稳定增长的背景下，资源优势与产能扩张计划支撑业绩确定性"],
            "key_metrics": ["35万吨/年电解铜产能", "玉龙铜矿三期投产"],
            "target_valuation": []
        }]
    },
    {
        "code": "002895",
        "name": "川恒股份",
        "board": "SZ",
        "industry": "基础化工-农化制品-磷肥及磷化工",
        "concepts": ["磷化工", "磷矿", "储能", "磷酸铁", "高分红", "高股息"],
        "products": ["磷矿石", "磷酸铁"],
        "core_business": ["磷矿开采", "磷化工产品", "磷酸铁生产"],
        "industry_position": ["国内磷化工资源型领军企业", "手握多座高品位磷矿"],
        "chain": ["化工-上游-磷矿", "新能源-中游-磷酸铁锂"],
        "partners": [],
        "articles": [{
            "title": "磷矿稀缺属性强化叠加储能需求爆发拉动磷矿石消耗",
            "date": "2026-04-19",
            "source": "manual_input",
            "accidents": ["2025年权益磷矿石产能320万吨", "2027年后将突破850万吨"],
            "insights": ["磷矿稀缺属性强化叠加储能需求爆发拉动磷矿石消耗", "公司磷酸铁产能受益于锂电行业复苏，高分红高股息优势进一步增强投资价值"],
            "key_metrics": ["2025年权益磷矿石产能320万吨", "2027年后将突破850万吨"],
            "target_valuation": []
        }]
    },
    {
        "code": "600309",
        "name": "万华化学",
        "board": "SH",
        "industry": "基础化工-化学制品-聚氨酯",
        "concepts": ["苯胺", "化工", "一体化产业链", "涨价"],
        "products": ["苯胺", "MDI", "TDI"],
        "core_business": ["苯胺生产", "聚氨酯制造"],
        "industry_position": ["国内苯胺最大生产商", "产能占比超50%"],
        "chain": ["化工-中游-化学制品"],
        "partners": [],
        "articles": [{
            "title": "苯胺价格持续上涨，行业库存处于2024年以来低位",
            "date": "2026-04-19",
            "source": "manual_input",
            "accidents": ["苯胺价格持续上涨", "行业库存处于2024年以来低位", "供应偏紧叠加出口补单与下游需求复苏"],
            "insights": ["拥有一体化产业链与成本优势", "上游纯苯价格上涨形成成本支撑，公司将充分受益于供需格局改善"],
            "key_metrics": ["产能占比超50%"],
            "target_valuation": []
        }]
    },
    {
        "code": "002859",
        "name": "洁美科技",
        "board": "SZ",
        "industry": "电子-元件-被动元件",
        "concepts": ["电子元器件", "光刻机", "商业航天", "涨价", "离型膜"],
        "products": ["离型膜", "CPP膜", "塑料载带", "PET胶带", "纸质载带"],
        "core_business": ["电子元器件制造", "超精密光学加工装备"],
        "industry_position": ["国内稀缺的超精密光学加工装备厂商"],
        "chain": ["电子-中游-被动元件", "半导体-上游-光刻机设备"],
        "partners": ["福晶科技", "茂莱光学", "波长光电", "长光卫星", "至期光子"],
        "articles": [{
            "title": "主营产品全面涨价，拟收购埃福思进军光刻机和商业航天领域",
            "date": "2026-04-19",
            "source": "manual_input",
            "accidents": ["2026年4月1日起主营产品全面涨价，离型膜/CPP膜涨价30%-45%", "拟收购埃福思进军光刻机和商业航天领域"],
            "insights": ["埃福思是国内稀缺的超精密光学加工装备厂商，离子束抛光机居国内前列", "预计持续受益于国产光刻机和商业航天产业机遇"],
            "key_metrics": ["离型膜/CPP膜涨价30%-45%", "塑料载带涨价15%-25%", "PET胶带涨价25%-35%", "纸质载带上涨10-30%"],
            "target_valuation": []
        }]
    },
    {
        "code": "688663",
        "name": "新风光",
        "board": "SH",
        "industry": "电力设备-电网设备-输变电设备",
        "concepts": ["固态变压器", "SST", "AIDC", "AI基建", "数据中心", "高压直流配电", "新能源", "储能"],
        "products": ["固态变压器SST", "高压SVG", "高压级联储能"],
        "core_business": ["固态变压器SST研发制造", "高压SVG", "高压级联储能产品", "电力电子设备"],
        "industry_position": ["固态变压器SST领先企业", "高压SVG大规模商用厂商"],
        "chain": ["电力设备-中游-输变电设备", "AIDC基础设施-上游-电源设备"],
        "partners": [],
        "articles": [{
            "title": "SST成功下线，卡位AI基建核心节点",
            "date": "2026-04-19",
            "source": "manual_input",
            "accidents": ["新一代固态变压器SST正式下线", "10kV输入/800V直流输出，单机功率2500kW", "SST体积重量仅为传统变压器1/3-1/2，供电效率提升2%-4%"],
            "insights": ["SST锚定AIDC高景气度赛道，高压直流配电被NV视为关键升级技术方向", "拓扑架构、驱动设计到控制算法完全自主研发，共享现有产线实现快速量产", "构网能力适配高比例新能源接入场景，单元冗余设计适配高难度复杂应用"],
            "key_metrics": ["10kV输入/800V直流输出", "单机功率2500kW", "电压覆盖至13.8kV", "供电效率提升2%-4%", "SST渗透率从1.5%提升至20%", "单价从3.5元/W量产至2.8元/W"],
            "target_valuation": ["2030年市场规模784亿元"]
        }]
    }
]


def main():
    """主函数：批量添加个股"""
    print("🚀 批量添加个股信息到投研数据库...\n")
    
    # 初始化更新器
    updater = IncrementalUpdater(base_dir=str(Path(__file__).parent / "data" / "master"))
    
    added_count = 0
    updated_count = 0
    
    for stock in stocks_to_add:
        code = stock["code"]
        name = stock["name"]
        
        # 准备股票数据
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
            "mention_count": 1,
            "articles": stock["articles"]
        }
        
        # 添加/更新个股
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


if __name__ == "__main__":
    main()
