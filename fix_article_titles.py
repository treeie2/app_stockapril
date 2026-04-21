#!/usr/bin/env python3
"""
修复今日更新股票的文章标题和来源字段
"""
import json
from pathlib import Path

MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")

# 股票对应的文章标题映射
STOCK_ARTICLE_TITLES = {
    # 航天轴承 + 金刚石散热
    '002046': '航天轴承 + 金刚石散热 + AI 服务器核心标的梳理',
    '603019': '航天轴承 + 金刚石散热 + AI 服务器核心标的梳理',
    '000977': '航天轴承 + 金刚石散热 + AI 服务器核心标的梳理',
    '603118': '航天轴承 + 金刚石散热 + AI 服务器核心标的梳理',
    
    # 磷化铟产业链
    '000960': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    '600961': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    '600531': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    '002428': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    '002975': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    '600206': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    '600703': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    '688498': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    '600105': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    '688048': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    '002023': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    '688313': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    '002281': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    '000988': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    '002725': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    '300316': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    '002371': '磷化铟（InP）：AI 算力卡脖子核心，全产业链标的全梳理',
    
    # TGV 技术
    '603005': 'TGV（玻璃通孔）技术全解析 + 核心企业梳理',
}

def fix_articles():
    """修复文章标题和来源"""
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        stocks_master = json.load(f)
    
    fixed_count = 0
    
    for code, title in STOCK_ARTICLE_TITLES.items():
        if code in stocks_master:
            stock = stocks_master[code]
            for article in stock.get('articles', []):
                if article.get('date') == '2026-04-21' and not article.get('title'):
                    article['title'] = title
                    article['source'] = '微信公众号' if '磷化铟' in title or 'TGV' in title else '手动整理'
                    fixed_count += 1
                    print(f"✅ 修复 {code} {stock.get('name', '')}: {title[:30]}...")
    
    # 保存修复后的数据
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(stocks_master, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 修复完成！共修复 {fixed_count} 篇文章")

if __name__ == '__main__':
    fix_articles()
