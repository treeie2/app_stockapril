#!/usr/bin/env python3
"""Extract products/core_business/industry_position/chain/partners from raw_material and fill stocks_master.json."""
import json
from pathlib import Path

BASE = Path(__file__).parent
MASTER = BASE / 'data' / 'stocks' / 'stocks_master.json'

with open(MASTER, 'r', encoding='utf-8') as f:
    master = json.load(f)

stocks = master['stocks']

# Structured extraction from raw_material files
extracted = {
    '300161': {  # 华中数控
        'products': ['数控系统'],
        'core_business': ['中高档数控系统研发制造'],
        'industry_position': ['国内中高档数控系统绝对龙头', '军工领域市占率超25%'],
        'chain': ['中游 - 数控系统'],
    },
    '688305': {  # 科德数控
        'products': ['五轴联动数控机床', 'GNC系列数控系统'],
        'core_business': ['数控系统+关键功能部件+整机全产业链'],
        'industry_position': ['国内少数实现全产业链自主可控的五轴联动企业'],
        'chain': ['全产业链 - 数控系统到整机'],
    },
    '688697': {  # 纽威数控
        'products': ['立式加工中心', '卧式加工中心', '龙门加工中心'],
        'core_business': ['中高端数控机床整机研发制造'],
        'industry_position': ['中高端数控机床整机领军者'],
        'chain': ['中游 - 数控机床整机'],
    },
    '300124': {  # 汇川技术
        'products': ['伺服系统', 'PLC'],
        'core_business': ['工业自动化及伺服系统'],
        'industry_position': ['国内工控市占率居首'],
        'chain': ['中游 - 核心驱动部件'],
    },
    '000837': {  # 秦川机床
        'products': ['齿轮加工机床', '精密磨床', '滚珠丝杠', '行星滚柱丝杠'],
        'core_business': ['齿轮加工机床和精密磨床龙头', '精密丝杠制造'],
        'industry_position': ['国内齿轮加工机床和精密磨床龙头', '汉江机床螺纹磨床市占率60%-80%'],
        'chain': ['中游 - 核心功能部件'],
    },
    '002915': {  # 中欣氟材
        'products': ['电子级氢氟酸', 'PEEK新材料', '氟精细化学品'],
        'core_business': ['全产业链氟化工'],
        'industry_position': ['全产业链氟化工龙头'],
        'chain': ['上游 - 萤石矿到高端材料全链条'],
    },
    '000066': {  # 中国长城
        'products': ['AI服务器', '通用服务器', '服务器电源', '飞腾CPU'],
        'core_business': ['计算硬件(服务器/CPU)+电源设备'],
        'industry_position': ['服务器电源国内第一国际前三'],
        'chain': ['中游 - 计算硬件与电源'],
    },
    '002254': {  # 泰和新材
        'products': ['芳纶', '氨纶', '芳纶纸'],
        'core_business': ['高性能纤维材料'],
        'industry_position': ['民士达(持股66%)国内芳纶纸市占率超一半'],
        'chain': ['上游 - 高性能纤维材料'],
    },
}

target_fields = ['products', 'core_business', 'industry_position', 'chain', 'partners']
filled = []

for code, data in extracted.items():
    if code not in stocks:
        continue
    s = stocks[code]
    name = s.get('name', '')
    modified = False
    fields = []
    for field in target_fields:
        if field not in s or not s.get(field):
            if field in data and data[field]:
                s[field] = data[field]
            else:
                s[field] = []
            fields.append(field)
            modified = True
    if modified:
        filled.append({'code': code, 'name': name, 'fields': fields})

master['last_updated'] = '2026-05-18T16:30:00+08:00'
with open(MASTER, 'w', encoding='utf-8') as f:
    json.dump(master, f, ensure_ascii=False, indent=2)

print('Filled for %d stocks:\n' % len(filled))
for c in filled:
    print('  %s (%s): %s' % (c['name'], c['code'], ', '.join(c['fields'])))
print('\nTotal: %d stocks' % len(filled))
