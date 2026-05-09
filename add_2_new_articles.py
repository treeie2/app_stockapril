#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动添加 2 篇新文章到今日 JSON 文件
"""
import json
from pathlib import Path
from datetime import datetime

# 手动整理的股票数据
new_stocks = {
    "000751": {  # 锌业股份
        "name": "锌业股份",
        "code": "000751",
        "board": "",
        "industry": "有色金属 - 工业金属 - 铅锌",
        "concepts": [
            "有色金属冶炼",
            "小金属概念",
            "锌电池",
            "龙头股",
            "绿色工厂"
        ],
        "products": [
            "锌锭",
            "锌合金",
            "电解铜",
            "铅锭",
            "硫酸",
            "铟",
            "金",
            "银"
        ],
        "core_business": [
            "有色金属锌、铅、铜的冶炼及深加工",
            "稀贵金属综合回收（铟、镉、金、银）"
        ],
        "industry_position": [
            "国内大型锌、铅冶炼企业",
            "2025 年上半年锌金属产量 13.55 万吨，占国内 4.61%",
            "拥有'葫锌 (HX)'知名品牌，锌锭获国家免检",
            "锌锭、锌粉等国家标准起草单位"
        ],
        "chain": [
            "上游 - 锌精矿等原料",
            "中游 - 锌、铅冶炼",
            "下游 - 镀锌、汽车、基建、光伏"
        ],
        "partners": [],
        "valuation": {
            "target_market_cap": "",
            "target_market_cap_billion": 0
        },
        "insights": "",
        "key_metrics": [
            "2025 年上半年锌金属产量 13.55 万吨",
            "占国内锌金属产量的 4.61%",
            "30 万吨锌合金项目投产",
            "2025 年套期保值额度上调至 7 亿元"
        ],
        "accident": "",
        "target_valuation": [],
        "articles": [
            {
                "title": "【000751】：有色金属 + 锌电池 + 半导体磷化铟材料，国内大型锌、铅冶炼企业",
                "date": "2026-05-06",
                "source": "https://mp.weixin.qq.com/s/qkMNCFQv3t4j2dTcna4qXA",
                "insights": "",
                "key_metrics": [
                    "2025 年上半年锌金属产量 13.55 万吨",
                    "占国内锌金属产量的 4.61%",
                    "30 万吨锌合金项目投产"
                ],
                "accidents": [],
                "target_valuation": []
            }
        ],
        "mention_count": 1,
        "last_updated": "2026-05-06"
    },
    
    "300120": {  # 经纬辉开
        "name": "经纬辉开",
        "code": "300120",
        "board": "",
        "industry": "电子 - 光学光电子 - 面板",
        "concepts": [
            "射频滤波芯片",
            "液晶显示与触控模组",
            "PET 铜箔",
            "储能",
            "特高压",
            "海工装备",
            "柔性屏",
            "智慧灯杆"
        ],
        "products": [
            "液晶显示屏",
            "液晶显示模组",
            "电容式触摸屏",
            "触控显示模组",
            "电磁线",
            "电抗器",
            "特高压平波电抗器",
            "滤波电抗器"
        ],
        "core_business": [
            "液晶显示和触控显示模组的研发、生产和销售",
            "电磁线、电抗器的研发、生产和销售",
            "射频前端薄膜体声波滤波芯片布局"
        ],
        "industry_position": [
            "电力和电子信息双主业运营",
            "国家高新技术企业",
            "已建成天津、湖南、马来西亚四大生产基地",
            "电磁线是传统优势业务",
            "电抗器产品打开国家电网、南方电网市场"
        ],
        "chain": [
            "上游 - 电子材料、铜材",
            "中游 - 液晶显示模组、电磁线、电抗器制造",
            "下游 - 车载显示、医疗设备、工业控制、消费电子、特高压电力"
        ],
        "partners": [
            "国家电网",
            "南方电网",
            "伟创力",
            "捷普集团",
            "德赛西威",
            "伟世通",
            "霍尼韦尔",
            "美的"
        ],
        "valuation": {
            "target_market_cap": "",
            "target_market_cap_billion": 0
        },
        "insights": "",
        "key_metrics": [],
        "accident": "",
        "target_valuation": [],
        "articles": [
            {
                "title": "【300120】：射频滤波芯片 + 液晶显示器件及触控模组+PET 铜箔 + 储能 + 智能电网，电力和电子信息双主业运营",
                "date": "2026-05-06",
                "source": "https://mp.weixin.qq.com/s/ExsvrcBQUxSASppjzvMalQ",
                "insights": "",
                "key_metrics": [],
                "accidents": [],
                "target_valuation": []
            }
        ],
        "mention_count": 1,
        "last_updated": "2026-05-06"
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
    print(f"新增 2 只股票到今日 JSON 文件")
    print(f"{'='*80}\n")
    
    for code, stock in new_stocks.items():
        if code in stocks:
            # 如果已存在，合并 articles
            existing = stocks[code]
            existing_name = existing.get('name', 'N/A')
            
            # 合并 articles（去重）
            existing_articles = existing.get('articles', [])
            new_articles = stock['articles']
            
            # 按 (source, title) 去重
            existing_set = {(a.get('source', ''), a.get('title', '')) for a in existing_articles}
            for article in new_articles:
                key = (article.get('source', ''), article.get('title', ''))
                if key not in existing_set:
                    existing_articles.append(article)
                    existing_set.add(key)
            
            # 合并 concepts
            existing_concepts = set(existing.get('concepts', []))
            existing_concepts.update(stock['concepts'])
            
            # 更新字段
            existing['concepts'] = list(existing_concepts)
            existing['articles'] = existing_articles
            existing['mention_count'] = existing.get('mention_count', 0) + 1
            existing['last_updated'] = '2026-05-06'
            
            print(f"✅ {code} - {existing_name}: 合并文章 (现有 {len(existing_articles)} 篇)")
        else:
            # 新增股票
            stocks[code] = stock
            print(f"✅ {code} - {stock['name']}: 新增")
    
    # 更新 update_info
    update_info = data.get('update_info', {})
    update_info['article_count'] = update_info.get('article_count', 0) + 2
    update_info['updated_stocks'] = update_info.get('updated_stocks', 0)
    update_info['new_stocks'] = update_info.get('new_stocks', 0) + 2
    data['update_info'] = update_info
    
    # 保存更新后的数据
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"更新完成！")
    print(f"{'='*80}")
    print(f"文件：{json_file}")
    print(f"文章总数：{update_info['article_count']}")
    print(f"新增股票：{update_info['new_stocks']}")
    print(f"\n下一步：")
    print(f"1. 同步到 Firebase: python sync_today_stocks_to_firebase.py")
    print(f"2. 推送到 GitHub 触发 Vercel 部署")
    
    return len(new_stocks)

if __name__ == '__main__':
    update_stocks()
