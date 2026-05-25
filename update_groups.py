#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 只保留一个分组，合并所有股票

import json

# 读取分组数据
groups_file = "data/groups/groups.json"
with open(groups_file, 'r', encoding='utf-8') as f:
    groups = json.load(f)

# 过滤掉刚才新增的3个分组，只保留原有的分组
filtered_groups = []
for group in groups['groups']:
    if group['id'] not in ["group_20260520150001", "group_20260520150002", "group_20260520150003"]:
        filtered_groups.append(group)

# 添加一个合并后的新分组
new_group = {
    "id": "group_20260520150000",
    "name": "平头哥芯片上市",
    "description": "阿里巴巴平头哥芯片业务单独上市受益标的，涵盖芯片设计、制造封测、生态适配全产业链",
    "color": "#f59e0b",
    "icon": "🔌",
    "stocks": [
        "全志科技", "芯原股份", "纳思达", "乐鑫科技", "中科蓝讯",
        "国芯科技", "寒武纪", "翱捷科技", "东软载波", "兆易创新",
        "中芯国际", "长电科技", "通富微电", "利扬芯片",
        "润和软件", "软通动力", "青云科技", "云天励飞"
    ],
    "created_at": "2026-05-20",
    "updated_at": "2026-05-20"
}

filtered_groups.append(new_group)
groups['groups'] = filtered_groups

# 保存
with open(groups_file, 'w', encoding='utf-8') as f:
    json.dump(groups, f, ensure_ascii=False, indent=2)

print(f"✅ 分组已更新，现在有 {len(filtered_groups)} 个分组")
print(f"✅ 新增分组：{new_group['name']}（{len(new_group['stocks'])} 只股票）")
