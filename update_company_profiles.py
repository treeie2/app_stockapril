#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 9 篇文章中手动提取公司画像字段并更新到今日 JSON 文件
"""
import json
from pathlib import Path

# 手动整理的公司画像数据（基于文章内容推断）
manual_updates = {
    "001233": {  # 海安集团
        "industry": "基础化工 - 橡胶和塑料 - 轮胎制造",
        "concepts": ["矿用轮胎", "工程机械", "大承包业务", "深市主板"],
        "products": ["矿用巨胎", "特种轮胎", "全钢子午线轮胎", "1k 轮胎"],
        "core_business": ["矿用轮胎研发、生产和销售", "大承包业务（按矿石采选量确收）"],
        "industry_position": [
            "国内矿用轮胎核心供应商",
            "矿用巨胎领先企业",
            "全球市占率 7%（CR3=80%）",
            "净利率 25%+"
        ],
        "chain": ["上游 - 天然橡胶", "中游 - 轮胎制造", "下游 - 矿山（紫金、江铜、兖矿）"],
        "partners": ["紫金矿业", "江西铜业", "兖矿集团"]
    },
    
    "688521": {  # 芯原股份
        "industry": "电子 - 半导体 - IC 设计服务",
        "concepts": ["国产算力", "AI 芯片", "ASIC", "芯片设计服务", "半导体"],
        "products": ["AI 芯片设计服务", "ASIC 芯片", "TPU/GPU 部署"],
        "core_business": ["芯片设计平台即服务（SiPaaS）", "AI 芯片解决方案"],
        "industry_position": [
            "国产算力龙头",
            "AI 芯片设计领先企业",
            "9 天新签 37 亿订单"
        ],
        "chain": ["上游 - IP 授权", "中游 - 芯片设计服务", "下游 - 云计算/CSP/模型厂商"],
        "partners": ["头部云厂商", "GPU 厂商", "模型厂商"]
    },
    
    "000066": {  # 中国长城
        "industry": "计算机 - 计算机设备 - 信创设备",
        "concepts": ["信创", "国产算力", "自主可控", "央企改革"],
        "products": ["信创服务器", "PC", "算力设备"],
        "core_business": ["信创产品研发、生产和销售", "算力基础设施建设"],
        "industry_position": ["信创国家队", "自主可控核心标的"],
        "chain": ["中游 - 信创设备制造", "下游 - 政府/企业客户"],
        "partners": []
    },
    
    "688020": {  # 方邦股份
        "industry": "电子 - 电子化学品",
        "concepts": ["电子材料", "半导体材料"],
        "products": ["电子化学品", "半导体材料"],
        "core_business": ["电子化学品研发和生产"],
        "industry_position": [],
        "chain": ["上游 - 化工原料", "中游 - 电子化学品", "下游 - 半导体/电子制造"],
        "partners": []
    },
    
    "688665": {  # 联讯仪器
        "industry": "仪器仪表 - 测试测量仪器",
        "concepts": ["光模块测试", "测试设备", "国产化"],
        "products": ["光模块测试设备", "测试仪器"],
        "core_business": ["光模块测试设备研发、生产和销售"],
        "industry_position": [
            "光模块测试设备龙头",
            "测试环节价值量从 20% 提升到 35%"
        ],
        "chain": ["中游 - 测试设备制造", "下游 - 光模块厂商"],
        "partners": []
    },
    
    "300322": {  # 硕贝德
        "industry": "电子 - 消费电子 - 天线",
        "concepts": [
            "商业航天", "卫星导航", "6G 概念", "毫米波雷达", "无线充电",
            "5G", "汽车电子", "华为概念", "特斯拉概念"
        ],
        "products": ["天线", "无线充电模组", "卫星通信天线"],
        "core_business": ["天线及射频器件研发、生产和销售"],
        "industry_position": ["细分龙头", "隐形冠军"],
        "chain": ["中游 - 天线制造", "下游 - 手机/汽车/卫星"],
        "partners": ["华为", "特斯拉"]
    },
    
    "688138": {  # 清溢光电
        "industry": "电子 - 光学光电子",
        "concepts": ["光电显示"],
        "products": ["光电显示材料"],
        "core_business": ["光电显示材料研发和生产"],
        "industry_position": [],
        "chain": ["中游 - 光电材料"],
        "partners": []
    },
    
    "002203": {  # 海亮股份
        "industry": "有色金属 - 工业金属 - 铜",
        "concepts": ["铜加工", "锂电池箔", "出海"],
        "products": ["铜管", "铜棒", "铜箔", "锂电池箔"],
        "core_business": [
            "铜管、铜棒等铜产品研发、生产和销售",
            "锂电池箔业务"
        ],
        "industry_position": [
            "铜管行业龙头",
            "全球铜管销量第一",
            "锂电池箔新进入者"
        ],
        "chain": ["上游 - 铜原料", "中游 - 铜加工", "下游 - 空调/锂电池"],
        "partners": ["宁德时代"]
    },
    
    "301613": {  # 智微智能
        "industry": "计算机 - 计算机设备",
        "concepts": ["AI PC", "边缘计算"],
        "products": ["AI PC", "边缘计算设备"],
        "core_business": ["智能硬件研发和销售"],
        "industry_position": [],
        "chain": ["中游 - 智能硬件"],
        "partners": []
    }
}

def update_stocks():
    """更新今日 JSON 文件"""
    # 读取 JSON 文件
    json_file = Path(__file__).parent / 'data' / 'stocks_master_2026-05-06.json'
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data['stocks']
    
    print(f"\n{'='*80}")
    print(f"更新 {len(manual_updates)} 只股票的公司画像字段")
    print(f"{'='*80}\n")
    
    updated_count = 0
    for code, updates in manual_updates.items():
        if code in stocks:
            stock = stocks[code]
            stock_name = stock.get('name', 'N/A')
            
            # 更新字段
            for field, value in updates.items():
                old_value = stock.get(field)
                stock[field] = value
                
                if old_value != value:
                    if isinstance(value, list) and len(value) > 0:
                        print(f"✅ {code} - {stock_name}: {field} = {len(value)} 项")
                    elif isinstance(value, str) and value:
                        print(f"✅ {code} - {stock_name}: {field} = {value[:50]}")
            
            updated_count += 1
            print()
        else:
            print(f"❌ {code} 不在 stocks 中")
    
    # 保存更新后的数据
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"更新完成！")
    print(f"{'='*80}")
    print(f"已更新 {updated_count} 只股票")
    print(f"文件：{json_file}")
    print(f"\n下一步：")
    print(f"1. 同步到 Firebase: python sync_today_stocks_to_firebase.py")
    print(f"2. 推送到 GitHub 触发 Vercel 部署")
    
    return updated_count

if __name__ == '__main__':
    update_stocks()
