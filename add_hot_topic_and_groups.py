#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 新增平头哥芯片上市热点和分组

import json
from datetime import datetime

# 1. 更新热点数据
hot_topics_file = "data/hot_topics/hot_topics.json"
with open(hot_topics_file, 'r', encoding='utf-8') as f:
    hot_topics = json.load(f)

# 添加新的热点
new_topic = {
    "id": "topic_20260520150000",
    "name": "平头哥芯片上市",
    "drivers": "阿里巴巴准备推进旗下芯片业务\"平头哥\"单独上市，摩根大通研报测算潜在估值在250亿至620亿美元之间，约占阿里当前市值的6%到14%。平头哥芯片业务涵盖RISC-V架构、服务器CPU、AI芯片等领域，相关产业链公司将受益。",
    "stocks": [
        "全志科技", "芯原股份", "纳思达", "乐鑫科技", "中科蓝讯",
        "国芯科技", "寒武纪", "翱捷科技", "东软载波", "兆易创新",
        "中芯国际", "长电科技", "通富微电", "利扬芯片",
        "润和软件", "软通动力", "青云科技", "云天励飞"
    ],
    "display": True,
    "created_at": "2026-05-20",
    "updated_at": "2026-05-20"
}

hot_topics["topics"].append(new_topic)

with open(hot_topics_file, 'w', encoding='utf-8') as f:
    json.dump(hot_topics, f, ensure_ascii=False, indent=2)

print(f"✅ 已添加热点：{new_topic['name']}")

# 2. 更新分组数据
groups_file = "data/groups/groups.json"
with open(groups_file, 'r', encoding='utf-8') as f:
    groups = json.load(f)

# 添加新的分组
new_groups = [
    {
        "id": "group_20260520150001",
        "name": "RISC-V芯片",
        "description": "RISC-V架构芯片设计与IP授权相关标的，受益于平头哥芯片生态",
        "color": "#f59e0b",
        "icon": "🔌",
        "stocks": [
            "全志科技", "芯原股份", "纳思达", "乐鑫科技", "中科蓝讯",
            "国芯科技", "寒武纪", "翱捷科技", "东软载波", "兆易创新"
        ],
        "created_at": "2026-05-20",
        "updated_at": "2026-05-20"
    },
    {
        "id": "group_20260520150002",
        "name": "芯片制造封测",
        "description": "芯片制造与封测相关标的，为平头哥提供代工和封测服务",
        "color": "#10b981",
        "icon": "🏭",
        "stocks": [
            "中芯国际", "长电科技", "通富微电", "利扬芯片"
        ],
        "created_at": "2026-05-20",
        "updated_at": "2026-05-20"
    },
    {
        "id": "group_20260520150003",
        "name": "芯片生态适配",
        "description": "芯片生态适配与软件服务相关标的，深度参与平头哥生态建设",
        "color": "#3b82f6",
        "icon": "🔧",
        "stocks": [
            "润和软件", "软通动力", "青云科技", "云天励飞"
        ],
        "created_at": "2026-05-20",
        "updated_at": "2026-05-20"
    }
]

for group in new_groups:
    groups["groups"].append(group)
    print(f"✅ 已添加分组：{group['name']}")

with open(groups_file, 'w', encoding='utf-8') as f:
    json.dump(groups, f, ensure_ascii=False, indent=2)

print("\n🎉 热点和分组添加完成！")
print(f"- 新增热点：1个")
print(f"- 新增分组：3个")
