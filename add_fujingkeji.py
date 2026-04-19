#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""添加福晶科技个股信息"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / ".trae" / "skills" / "wechat-fetch-research-embedded" / "scripts"))

from incremental_update import IncrementalUpdater

stock_data = {
    "name": "福晶科技",
    "board": "SZ",
    "industry": "电子-光学光电子-光学元件",
    "concepts": ["CPO", "光通信", "法拉第旋片", "SGGG", "国产替代", "光刻机"],
    "products": ["法拉第旋转片", "光学晶体", "精密光学元件"],
    "core_business": ["光学晶体制造", "法拉第旋转片生产", "精密光学元件加工"],
    "industry_position": ["极少数实现SGGG自产的法拉第旋转片厂商", "扩产不受任何限制"],
    "chain": ["电子-中游-光学元件", "光通信-上游-光学器件"],
    "partners": [],
    "mention_count": 1,
    "articles": [{
        "title": "CPO拉动法拉第旋片用量激增，SGGG紧缺推动公司国产替代加速",
        "date": "2026-04-19",
        "source": "manual_input",
        "accidents": ["CPO拉动法拉第旋片用量激增", "SGGG供应商严重供不应求", "日本住友自稀土禁运后大幅减产", "法国luxium严重供不应求"],
        "insights": ["福晶科技为极少数实现SGGG自产的法拉第旋转片厂商，扩产不受任何限制", "上游SGGG供给缺口为福晶科技带来国产替代加速机遇"],
        "key_metrics": [],
        "target_valuation": []
    }]
}

updater = IncrementalUpdater(base_dir=str(Path(__file__).parent / "data" / "master"))
result = updater.update_single_stock("002222", stock_data)

print(f"✅ 福晶科技(002222) 已{result['action']}到投研数据库")
