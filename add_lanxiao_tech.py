#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""添加蓝晓科技个股信息到投研数据库"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / ".trae" / "skills" / "wechat-fetch-research-embedded" / "scripts"))

from incremental_update import IncrementalUpdater

# 蓝晓科技个股信息
stock_data = {
    "code": "300487",
    "name": "蓝晓科技",
    "board": "SZ",
    "industry": "基础化工-化学制品-其他化学制品",
    "concepts": ["吸附分离材料", "盐湖提锂", "GLP-1", "多肽固相合成", "超纯水", "金属回收", "生命科学", "国产替代"],
    "products": ["特种吸附分离材料", "GLP-1多肽固相合成载体", "电子级树脂", "盐湖提锂吸附材料", "金属回收材料"],
    "core_business": [
        "特种吸附分离材料研发制造",
        "GLP-1多肽固相合成载体",
        "盐湖提锂一体化方案",
        "电子级超纯水树脂",
        "金属资源回收"
    ],
    "industry_position": [
        "国内吸附分离材料领域领军企业",
        "全球产能最大、品系最全的吸附分离材料供应商之一",
        "GLP-1多肽固相合成载体国内80%以上临床阶段管线采用",
        "电子级树脂实现国产替代"
    ],
    "chain": [
        "吸附分离材料-上游-原材料",
        "吸附分离材料-中游-材料制造",
        "盐湖提锂-中游-提锂材料",
        "电子化学品-上游-超纯水材料"
    ],
    "partners": ["礼来", "诺和诺德"],
    "mention_count": 1,
    "articles": [{
        "title": "蓝晓科技：吸附分离材料龙头，赛道高增和涨价双受益稀缺标的",
        "date": "2026-04-20",
        "source": "https://mp.weixin.qq.com/s/QuYVV769vT8JBX6egoyEXg",
        "accidents": [
            "渭南高端材料产业园投产后产能将放大2-3倍",
            "在手订单超25亿元",
            "研发投入常年保持在营收5.7%-6.4%的高位",
            "拥有国内外授权专利近80项"
        ],
        "insights": [
            "精准卡位三大高增长赛道：生命科学、盐湖提锂、超纯水与金属资源",
            "GLP-1多肽固相合成载体绑定礼来、诺和诺德等全球龙头",
            "盐湖提锂技术覆盖'吸附+膜+电渗析'一体化方案，单吨成本显著低于传统工艺",
            "电子级树脂实现国产替代，切入头部晶圆厂供应链",
            "'材料+装置+服务'一体化解决方案深度嵌入客户生产流程，客户转换成本极高"
        ],
        "key_metrics": [
            "2024年扣非净利润7.45亿元，总股本5.08亿股，扣非EPS为1.466元/股",
            "2025年前三季度扣非净利润6.393亿元，同比增长10.56%",
            "生命科学板块毛利率长期维持60%以上",
            "金属回收业务毛利率超55%",
            "6.6万吨吸附分离材料年产能"
        ],
        "target_valuation": [
            "假设2025年全年扣非净利润8.893亿元，扣非EPS为1.75元/股，同比增长19.36%",
            "假设2026、2027年盈利增速维持20%",
            "2026年股票估值 = [8.5 + 2 X 20] X 1.75 = 84.87元",
            "2027年股票估值 = [8.5 + 2 X 20] X 1.75 X 1.20 = 101.85元"
        ],
        "expected_price": ["2026年: 84.87元", "2027年: 101.85元"],
        "expected_performance": [
            "2025年扣非净利润: 8.893亿元",
            "2025年扣非EPS: 1.75元/股",
            "2026-2027年盈利增速: 20%"
        ],
        "market_valuation": [
            "当前估值模型: 成长股估值模型",
            "估值公式: [8.5 + 2 X 增长率] X EPS"
        ]
    }]
}

def main():
    """主函数：添加蓝晓科技"""
    print("🚀 添加蓝晓科技个股信息到投研数据库...\n")
    
    updater = IncrementalUpdater(base_dir=str(Path(__file__).parent / "data" / "master"))
    
    code = stock_data["code"]
    name = stock_data["name"]
    
    stock_info = {
        "name": name,
        "board": stock_data["board"],
        "industry": stock_data["industry"],
        "concepts": stock_data["concepts"],
        "products": stock_data["products"],
        "core_business": stock_data["core_business"],
        "industry_position": stock_data["industry_position"],
        "chain": stock_data["chain"],
        "partners": stock_data["partners"],
        "mention_count": stock_data["mention_count"],
        "articles": stock_data["articles"]
    }
    
    result = updater.update_single_stock(code, stock_info)
    
    if result["action"] == "added":
        print(f"✅ 新增成功: {name} ({code})")
    else:
        print(f"✅ 更新成功: {name} ({code})")
    
    print(f"\n📊 个股信息:")
    print(f"   名称: {name}")
    print(f"   代码: {code}")
    print(f"   行业: {stock_data['industry']}")
    print(f"   概念: {', '.join(stock_data['concepts'][:5])}...")
    print(f"   文章: 蓝晓科技：吸附分离材料龙头...")

if __name__ == "__main__":
    main()
