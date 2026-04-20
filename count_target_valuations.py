#!/usr/bin/env python3
"""
统计有 target_valuation 的个股数量
支持按更新时间筛选
"""
import json
from pathlib import Path
from datetime import datetime

MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")

def count_target_valuations(filter_date=None):
    """
    统计有 target_valuation 的个股
    
    Args:
        filter_date: 筛选日期，格式 'YYYY-MM-DD'，为 None 时统计所有
    """
    if not MASTER_FILE.exists():
        print(f"❌ 股票数据文件不存在：{MASTER_FILE}")
        return
    
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', {})
    total_count = len(stocks)
    
    stocks_with_target = []
    today = datetime.now().strftime('%Y-%m-%d')
    
    for code, stock in stocks.items():
        articles = stock.get('articles', [])
        has_target = False
        target_count = 0
        latest_article_date = None
        
        for article in articles:
            target_vals = article.get('target_valuation', [])
            article_date = article.get('date', '')
            
            # 记录最新的文章日期
            if article_date:
                if latest_article_date is None or article_date > latest_article_date:
                    latest_article_date = article_date
            
            if target_vals:
                # 如果指定了日期，只统计该日期的
                if filter_date:
                    if article_date == filter_date:
                        has_target = True
                        target_count += len(target_vals)
                else:
                    has_target = True
                    target_count += len(target_vals)
        
        if has_target:
            stocks_with_target.append({
                'code': code,
                'name': stock.get('name', ''),
                'target_count': target_count,
                'latest_article_date': latest_article_date,
                'updated_at': stock.get('updated_at', '')
            })
    
    # 显示筛选条件
    if filter_date:
        print(f"\n📊 统计结果 (筛选日期：{filter_date}):")
    else:
        print(f"\n📊 统计结果 (全部):")
    
    print(f"   总股票数：{total_count}")
    print(f"   有 target_valuation 的股票：{len(stocks_with_target)}")
    if filter_date:
        print(f"   占比：{len(stocks_with_target)/total_count*100:.2f}%")
    else:
        print(f"   占比：{len(stocks_with_target)/total_count*100:.2f}%")
    
    # 按 target_count 排序
    sorted_stocks = sorted(stocks_with_target, key=lambda x: x['target_count'], reverse=True)
    
    print(f"\n📋 前 20 只股票:")
    print("-" * 70)
    for i, stock in enumerate(sorted_stocks[:20], 1):
        date_str = stock['latest_article_date'] or '-'
        print(f"  {i:2d}. {stock['code']} {stock['name']}: {stock['target_count']} 条估值 (日期：{date_str})")
    
    if filter_date and filter_date == today:
        print(f"\n✅ 以上为今天 ({today}) 更新的 {len(stocks_with_target)} 只股票")
    
    # 统计分布
    if len(stocks_with_target) > 20:
        print(f"\n📈 估值数量分布:")
        print("-" * 60)
        
        distribution = {}
        for stock in stocks_with_target:
            count = stock['target_count']
            distribution[count] = distribution.get(count, 0) + 1
        
        for count in sorted(distribution.keys(), reverse=True):
            print(f"   {count} 条估值：{distribution[count]} 只股票")

if __name__ == '__main__':
    print("🚀 开始统计 target_valuation...\n")
    
    # 统计今天的
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"{'='*70}")
    print(f"📅 今天 ({today}) 更新的个股")
    print(f"{'='*70}")
    count_target_valuations(filter_date=today)
    
    # 统计全部的
    print(f"\n{'='*70}")
    print(f"📅 全部历史数据")
    print(f"{'='*70}")
    count_target_valuations(filter_date=None)
