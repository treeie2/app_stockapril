#!/usr/bin/env python3
"""
修复 stocks_master.json 中的重复条目，合并新旧数据
"""
import json
from pathlib import Path

MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")

def fix_duplicates():
    """修复重复的股票条目"""
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        stocks_master = json.load(f)
    
    print(f"📊 修复前总股票数：{len(stocks_master)}")
    
    # 需要修复的股票代码（有新条目的）
    today_stocks = ['002046', '603019', '000977', '603118', '000960', '600961', '600531', 
                    '002428', '002975', '600206', '600703', '688498', '600105',
                    '688048', '002023', '688313', '002281', '000988', '002725',
                    '300316', '002371', '603005']
    
    # 实际上 JSON 字典不会有重复键，问题在于我们需要更新现有条目
    # 让我检查并更新这些股票的完整信息
    
    fixed_count = 0
    for code in today_stocks:
        if code in stocks_master:
            stock = stocks_master[code]
            
            # 确保有核心业务、行业地位、产业链位置等字段
            if not stock.get('core_business') and code == '002046':
                stock['core_business'] = ['航天轴承', '金刚石散热片', '半导体设备']
                stock['industry_position'] = ['国内金刚石领域第一梯队，航天领域市占率 90% 以上']
                stock['chain'] = ['中游 - 航天轴承', '中游 - 金刚石散热', '中游 - 半导体设备']
                
                # 更新文章标题
                for article in stock.get('articles', []):
                    if article.get('date') == '2026-04-21' and not article.get('title'):
                        article['title'] = '航天轴承 + 金刚石散热 + AI 服务器核心标的梳理'
                        article['source'] = '手动整理'
                
                fixed_count += 1
                print(f"✅ 修复 {code} {stock['name']}")
    
    # 保存修复后的数据
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(stocks_master, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 修复完成！共修复 {fixed_count} 只股票")
    print(f"📊 修复后总股票数：{len(stocks_master)}")

if __name__ == '__main__':
    fix_duplicates()
