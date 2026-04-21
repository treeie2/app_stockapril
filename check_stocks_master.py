#!/usr/bin/env python3
"""
检查并修复 stocks_master.json 中的重复条目
"""
import json
from pathlib import Path

MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")

def fix_duplicates():
    """修复重复的股票条目"""
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        stocks_master = json.load(f)
    
    print(f"📊 总股票数：{len(stocks_master)}")
    
    # 检查是否有重复
    keys = list(stocks_master.keys())
    unique_keys = set(keys)
    
    if len(keys) == len(unique_keys):
        print("✅ 没有重复条目")
    else:
        print(f"⚠️  发现重复条目：{len(keys) - len(unique_keys)} 个")
    
    # 检查 002046
    if '002046' in stocks_master:
        stock = stocks_master['002046']
        print(f"\n📄 002046 国机精工:")
        print(f"   文章数：{len(stock.get('articles', []))}")
        print(f"   提及次数：{stock.get('mention_count', 0)}")
        if stock.get('articles'):
            for i, article in enumerate(stock['articles']):
                print(f"   文章{i+1}: {article.get('title', '无标题')}")
                if article.get('target_valuation'):
                    print(f"      目标估值：{article['target_valuation']}")
    
    # 检查今天更新的其他股票
    today_stocks = ['603019', '000977', '603118', '000960', '600961', '600531', 
                    '002428', '002975', '600206', '600703', '688498', '600105',
                    '688048', '002023', '688313', '002281', '000988', '002725',
                    '300316', '002371', '603005']
    
    print("\n📚 今日更新股票检查:")
    for code in today_stocks:
        if code in stocks_master:
            stock = stocks_master[code]
            articles = stock.get('articles', [])
            today_articles = [a for a in articles if a.get('date') == '2026-04-21']
            if today_articles:
                print(f"   ✅ {code} {stock.get('name', '')}: {len(today_articles)} 篇今日文章")

if __name__ == '__main__':
    fix_duplicates()
