#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从电池相关微信公众号文章提取的个股信息添加到投研数据库"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / ".trae" / "skills" / "wechat-fetch-research-embedded" / "scripts"))

from incremental_update import IncrementalUpdater

# 文章相关个股
stocks_to_add = [
    {
        "code": "300750",
        "name": "宁德时代",
        "board": "SZ",
        "industry": "电力设备-电池-动力电池",
        "concepts": ["动力电池", "储能电池", "锂电池", "固态电池", "全球龙头", "特斯拉", "比亚迪"],
        "products": ["动力电池", "储能电池", "锂电池", "固态电池"],
        "core_business": ["动力电池研发制造", "储能系统", "电池材料", "电池回收"],
        "industry_position": ["全球动力电池龙头", "全球市占率第一", "储能电池全球领先"],
        "chain": ["新能源汽车-上游-动力电池", "储能-上游-储能电池"],
        "partners": ["特斯拉", "宝马", "奔驰", "大众", "蔚来", "小鹏", "理想"],
        "mention_count": 1,
        "articles": [{
            "title": "电池产业链核心企业",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/4oaY2uOZhUoPxf0aMe6NjQ",
            "accidents": [],
            "insights": ["全球动力电池龙头，技术领先，产能规模全球第一", "积极布局固态电池技术，保持技术领先优势"],
            "key_metrics": ["全球动力电池市占率第一"],
            "target_valuation": []
        }]
    },
    {
        "code": "002594",
        "name": "比亚迪",
        "board": "SZ",
        "industry": "汽车-乘用车-新能源汽车",
        "concepts": ["新能源汽车", "动力电池", "刀片电池", "整车制造", "垂直整合"],
        "products": ["新能源汽车", "动力电池", "刀片电池", "汽车电子"],
        "core_business": ["新能源汽车整车制造", "动力电池", "汽车电子", "半导体"],
        "industry_position": ["全球新能源汽车龙头", "动力电池全球领先", "垂直整合能力最强"],
        "chain": ["新能源汽车-下游-整车", "动力电池-中游-电池制造"],
        "partners": [],
        "mention_count": 1,
        "articles": [{
            "title": "电池产业链核心企业",
            "date": "2026-04-20",
            "source": "https://mp.weixin.qq.com/s/4oaY2uOZhUoPxf0aMe6NjQ",
            "accidents": [],
            "insights": ["全球新能源汽车销量冠军", "刀片电池技术领先，安全性高", "垂直整合能力强，成本控制优秀"],
            "key_metrics": ["新能源汽车销量全球第一"],
            "target_valuation": []
        }]
    }
]

def main():
    """主函数：批量添加个股"""
    print("🚀 从电池相关文章提取个股信息到投研数据库...\n")
    
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

if __name__ == "__main__":
    main()
