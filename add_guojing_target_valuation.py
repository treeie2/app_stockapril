#!/usr/bin/env python3
"""
给国机精工添加目标市值
"""
import json
from pathlib import Path
from datetime import datetime

MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")

def add_target_valuation():
    """给国机精工添加目标市值"""
    if not MASTER_FILE.exists():
        print(f"❌ 文件不存在：{MASTER_FILE}")
        return
    
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    stocks = master_data.get('stocks', {})
    
    # 查找国机精工（300416）
    if '300416' in stocks:
        stock = stocks['300416']
        print(f"📈 找到股票：{stock.get('name', '苏试试验')} (300416)")
        
        # 查找相关文章
        articles = stock.get('articles', [])
        updated_count = 0
        
        for article in articles:
            if '国机精工' in article.get('title', '') or '航天轴承' in article.get('title', ''):
                print(f"  📄 文章：{article['title'][:50]}...")
                
                # 添加目标市值
                if 'target_valuation' not in article:
                    article['target_valuation'] = ['目标市值：600 亿（30 倍 PE，利润 20 亿）']
                    print(f"    ✅ 添加目标市值：600 亿")
                    updated_count += 1
                else:
                    print(f"    ⏭️  已有目标市值：{article['target_valuation']}")
        
        # 保存回文件
        with open(MASTER_FILE, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 完成！更新了 {updated_count} 篇文章")
    else:
        print("❌ 未找到国机精工 (300416)")

if __name__ == '__main__':
    print("🚀 开始给国机精工添加目标市值...\n")
    add_target_valuation()
    print("\n🎉 处理完成！")
