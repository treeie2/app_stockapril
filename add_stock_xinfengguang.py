#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""添加新风光个股信息到投研数据库"""

import json
import sys
from datetime import datetime
from pathlib import Path

# 添加技能脚本路径
sys.path.insert(0, str(Path(__file__).parent / ".trae" / "skills" / "wechat-fetch-research-embedded" / "scripts"))

from incremental_update import IncrementalUpdater

# 新风光个股数据
stock_data = {
    "name": "新风光",
    "board": "SH",
    "industry": "电力设备-电网设备-输变电设备",
    "concepts": ["固态变压器", "SST", "AIDC", "AI基建", "数据中心", "高压直流配电", "新能源", "储能"],
    "products": ["固态变压器SST", "高压SVG", "高压级联储能"],
    "core_business": ["固态变压器SST研发制造", "高压SVG", "高压级联储能产品", "电力电子设备"],
    "industry_position": ["固态变压器SST领先企业", "高压SVG大规模商用厂商"],
    "chain": ["电力设备-中游-输变电设备", "AIDC基础设施-上游-电源设备"],
    "partners": [],
    "mention_count": 1,
    "articles": [
        {
            "title": "SST成功下线，卡位AI基建核心节点",
            "date": "2026-04-19",
            "source": "manual_input",
            "accidents": [
                "新一代固态变压器SST正式下线",
                "10kV输入/800V直流输出，单机功率2500kW",
                "SST体积重量仅为传统变压器1/3-1/2，供电效率提升2%-4%"
            ],
            "insights": [
                "SST锚定AIDC高景气度赛道，高压直流配电被NV视为关键升级技术方向",
                "拓扑架构、驱动设计到控制算法完全自主研发，共享现有产线实现快速量产",
                "构网能力适配高比例新能源接入场景，单元冗余设计适配高难度复杂应用",
                "预计2030年SST市场规模达784亿元（复合增速120%）"
            ],
            "key_metrics": [
                "10kV输入/800V直流输出",
                "单机功率2500kW",
                "电压覆盖至13.8kV",
                "供电效率提升2%-4%",
                "SST渗透率从1.5%提升至20%",
                "单价从3.5元/W量产至2.8元/W"
            ],
            "target_valuation": ["2030年市场规模784亿元"]
        }
    ]
}

# 初始化更新器
updater = IncrementalUpdater(base_dir=str(Path(__file__).parent / "data" / "master"))

# 添加个股
result = updater.update_single_stock("688663", stock_data)

print(f"\n✅ 新风光(688663) 已成功添加到投研数据库")
print(f"   操作: {result['action']}")
print(f"   日期: {result['date']}")
