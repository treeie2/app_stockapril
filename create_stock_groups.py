#!/usr/bin/env python3
"""
创建股票分组：磷化铟、TGV
"""
import json
from pathlib import Path

GROUPS_FILE = Path("data/groups/stock_groups.json")

# 磷化铟产业链相关股票
INP_STOCKS = {
    '000960': '锡业股份',      # 铟产品龙头
    '600961': '株冶集团',      # 铟回收
    '600531': '豫光金铅',      # 铟产品
    '002428': '云南锗业',      # 磷化铟衬底
    '002975': '博杰股份',      # 磷化铟检测
    '600206': '有研新材',      # 磷化铟靶材
    '600703': '三安光电',      # 磷化铟外延片
    '688498': '源杰科技',      # 磷化铟光芯片
    '600105': '永鼎股份',      # 光通信
    '688048': '长光华芯',      # 磷化铟激光芯片
    '688313': '仕佳光子',      # 磷化铟光器件
    '002281': '光迅科技',      # 磷化铟光器件
    '000988': '华工科技',      # 光通信器件
}

# TGV 技术相关股票
TGV_STOCKS = {
    '603005': '晶方科技',      # TGV 封测
    '002046': '国机精工',      # TGV 相关
    '300316': '晶盛机电',      # TGV 设备
    '002371': '北方华创',      # TGV 设备
}

def create_groups():
    """创建股票分组"""
    
    # 确保目录存在
    GROUPS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # 加载现有分组
    if GROUPS_FILE.exists():
        with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
            groups = json.load(f)
        print(f"📂 加载现有分组文件")
    else:
        groups = {}
        print(f"📝 创建新分组文件")
    
    # 创建磷化铟分组
    groups['磷化铟'] = {
        'name': '磷化铟',
        'description': '磷化铟产业链相关股票，包括铟矿开采、磷化铟材料、光芯片、光器件等',
        'stocks': list(INP_STOCKS.keys()),
        'stock_details': {code: {'name': name} for code, name in INP_STOCKS.items()},
        'count': len(INP_STOCKS),
        'created_at': '2026-04-21',
        'updated_at': '2026-04-21'
    }
    
    print(f"✅ 创建分组【磷化铟】：{len(INP_STOCKS)} 只股票")
    for code, name in INP_STOCKS.items():
        print(f"   - {code} {name}")
    
    # 创建 TGV 分组
    groups['TGV'] = {
        'name': 'TGV',
        'description': 'TGV（Through Glass Via）玻璃通孔技术相关股票，包括设备、封测等',
        'stocks': list(TGV_STOCKS.keys()),
        'stock_details': {code: {'name': name} for code, name in TGV_STOCKS.items()},
        'count': len(TGV_STOCKS),
        'created_at': '2026-04-21',
        'updated_at': '2026-04-21'
    }
    
    print(f"\n✅ 创建分组【TGV】：{len(TGV_STOCKS)} 只股票")
    for code, name in TGV_STOCKS.items():
        print(f"   - {code} {name}")
    
    # 保存分组文件
    with open(GROUPS_FILE, 'w', encoding='utf-8') as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 分组文件已保存到：{GROUPS_FILE}")
    print(f"📊 总计：{len(groups)} 个分组")

if __name__ == '__main__':
    create_groups()
