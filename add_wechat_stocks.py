#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从微信公众号文章提取的个股信息添加到投研数据库"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / ".trae" / "skills" / "wechat-fetch-research-embedded" / "scripts"))

from incremental_update import IncrementalUpdater

# 文章1: 江丰电子 vs 有研新材 - 半导体溅射靶材对比
stocks_article_1 = [
    {
        "code": "300666",
        "name": "江丰电子",
        "board": "SZ",
        "industry": "电子-半导体-半导体材料",
        "concepts": ["半导体", "溅射靶材", "国产替代", "先进制程", "3nm", "台积电"],
        "products": ["超高纯铝靶", "钛靶", "钽靶", "铜靶", "CMP抛光垫", "腔体屏蔽件", "覆铜陶瓷基板"],
        "core_business": ["超大规模集成电路制造用超高纯金属材料及溅射靶材", "半导体精密零部件", "第三代半导体材料"],
        "industry_position": ["半导体溅射靶材全球领先", "国内市占率超70%", "全球市占率约18.6%位列全球第二", "铜靶材进入台积电3nm供应链"],
        "chain": ["半导体-上游-材料", "芯片制造-核心材料"],
        "partners": ["台积电", "中芯国际", "SK海力士"],
        "mention_count": 1,
        "articles": [{
            "title": "江丰电子vs有研新材：半导体溅射靶材公司对比",
            "date": "2026-04-19",
            "source": "https://mp.weixin.qq.com/s/TZzO03Kqv_yW37Z884rd_g",
            "accidents": ["突破7N级超高纯钛靶技术", "量产满足3nm制程的6N级铜靶", "铜靶材进入台积电3nm供应链"],
            "insights": ["全球半导体市场规模预计2025年突破7000亿美元，AI、HPC、5G/6G推动芯片需求激增", "2023-2027年全球溅射靶材市场规模年复合增长率达8.5%，预计2027年突破251亿元人民币", "中美科技博弈加剧，国内晶圆厂将供应链本土化作为战略重点，国产替代加速"],
            "key_metrics": ["国内市占率超73%", "全球市占率约18.6%位列全球第二", "纯度达99.9999%以上支持5nm以下先进制程"],
            "target_valuation": []
        }]
    },
    {
        "code": "600206",
        "name": "有研新材",
        "board": "SH",
        "industry": "有色金属-金属新材料-稀土磁性材料",
        "concepts": ["半导体", "溅射靶材", "稀土材料", "光电材料", "高纯金属", "红外光学"],
        "products": ["12英寸高纯铜铝靶材", "高纯钴靶", "稀土材料", "CVDZnS/ZnSe红外光学材料"],
        "core_business": ["半导体靶材", "稀土材料", "光电材料", "高纯金属材料"],
        "industry_position": ["国内率先实现12英寸高纯钽靶的批量应用", "高纯钴靶通过先进存储客户验证", "红外光学材料国内唯一量产企业"],
        "chain": ["半导体-上游-材料", "军工-上游-光学材料"],
        "partners": ["台积电", "中芯国际"],
        "mention_count": 1,
        "articles": [{
            "title": "江丰电子vs有研新材：半导体溅射靶材公司对比",
            "date": "2026-04-19",
            "source": "https://mp.weixin.qq.com/s/TZzO03Kqv_yW37Z884rd_g",
            "accidents": ["国内率先实现12英寸高纯钽靶的批量应用", "高纯钴靶通过先进存储客户验证"],
            "insights": ["以'电磁光医'四大板块为核心，产品应用于半导体、新能源、生物医疗等产业", "晶界渗透技术降低重稀土用量30%，硫化物/卤化物电解质适配固态电池", "CVDZnS/ZnSe材料用于导弹制导系统，国内唯一量产企业"],
            "key_metrics": ["12英寸高纯铜铝靶材纯度99.9999%", "全球市场份额超20%"],
            "target_valuation": []
        }]
    }
]

# 文章2: 钽铌材料应用与东方钽业
stocks_article_2 = [
    {
        "code": "000962",
        "name": "东方钽业",
        "board": "SZ",
        "industry": "有色金属-稀有金属-钽铌",
        "concepts": ["钽", "铌", "可控核聚变", "商业航天", "超导", "高温合金", "国产替代"],
        "products": ["钽粉", "钽丝", "铌合金", "超导铌材", "钽靶材", "铌超导腔"],
        "core_business": ["钽铌材料生产", "超导材料", "高温合金材料"],
        "industry_position": ["国内钽铌龙头企业", "超导铌材全球市占率达70%", "铌超导腔国内独家供应", "钽粉钽丝全球市占率超55%"],
        "chain": ["有色金属-上游-稀有金属", "核聚变-上游-超导材料", "商业航天-上游-高温合金"],
        "partners": ["蓝箭航天"],
        "mention_count": 1,
        "articles": [{
            "title": "钽铌材料应用与相关投资标的",
            "date": "2026-04-19",
            "source": "https://mp.weixin.qq.com/s/-6KfIcFfrbvUFyJlNKYNsg",
            "accidents": ["米级铌钨合金推力室已交付蓝箭航天", "与巴西Taboca矿业签订5.4亿元采购合同锁定3000吨铁钽铌合金", "募投项目新增湿法冶金3000吨、火法冶金1000吨、高端制品145吨产能"],
            "insights": ["铌钛合金、铌三锡用于约束高温等离子体，是磁约束聚变装置核心组件", "铌合金用于火箭发动机喷管延伸段、燃烧室，单箭推力室价值量约3500-4500万元", "预计2026年商业航天相关营收超2亿元", "原料自给率从10%提升至40%", "钽靶材、铌超导腔打破欧美垄断，列入央企科技创新成果目录"],
            "key_metrics": ["超导铌材全球市占率达70%", "钽粉钽丝全球市占率超55%", "单箭推力室价值量约3500-4500万元", "预计2026年商业航天营收超2亿元", "原料自给率从10%提升至40%", "全球钽消费量年均增速14%，预计2030年达到3546吨"],
            "target_valuation": ["募投项目预计新增年收入35.27亿元"]
        }]
    }
]

def main():
    """主函数：批量添加个股"""
    print("🚀 从微信公众号文章提取个股信息到投研数据库...\n")
    
    updater = IncrementalUpdater(base_dir=str(Path(__file__).parent / "data" / "master"))
    
    all_stocks = stocks_article_1 + stocks_article_2
    added_count = 0
    updated_count = 0
    
    for stock in all_stocks:
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
    print(f"\n📊 涉及文章:")
    print(f"   1. 江丰电子vs有研新材：半导体溅射靶材对比")
    print(f"   2. 钽铌材料应用与东方钽业")

if __name__ == "__main__":
    main()
