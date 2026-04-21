#!/usr/bin/env python3
"""
修正国机精工的股票代码并添加目标市值
"""
import json
from pathlib import Path
from datetime import datetime

MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")
TODAY = datetime.now().strftime('%Y-%m-%d')

def fix_guojing_stock():
    """修正国机精工的股票代码并添加目标市值"""
    if not MASTER_FILE.exists():
        print(f"❌ 文件不存在：{MASTER_FILE}")
        return
    
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    stocks = master_data.get('stocks', {})
    
    # 检查是否有错误的 300416 苏试试验（国机精工内容）
    if '300416' in stocks:
        stock_300416 = stocks['300416']
        articles = stock_300416.get('articles', [])
        
        # 查找国机精工相关的文章
        for article in articles:
            if '国机精工' in article.get('title', ''):
                print(f"📄 在 300416 苏试试验中找到国机精工文章：{article['title']}")
                
                # 移动到正确的 002046 国机精工
                if '002046' not in stocks:
                    stocks['002046'] = {
                        'name': '国机精工',
                        'articles': [],
                        'mention_count': 0
                    }
                
                # 复制文章到 002046
                stocks['002046']['articles'].append(article)
                stocks['002046']['mention_count'] = stocks['002046'].get('mention_count', 0) + 1
                
                # 确保有目标市值
                if 'target_valuation' not in article:
                    article['target_valuation'] = ['目标市值：600 亿（30 倍 PE，利润 20 亿）']
                    print(f"  ✅ 添加目标市值：600 亿")
                
                print(f"  ✅ 已移动到 002046 国机精工")
        
        # 保存回文件
        with open(MASTER_FILE, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 完成！已修正国机精工的股票代码为 002046")
    else:
        # 如果 300416 不存在，检查 002046
        if '002046' in stocks:
            stock = stocks['002046']
            print(f"📈 找到国机精工 (002046)")
            
            # 确保有目标市值
            for article in stock.get('articles', []):
                if 'target_valuation' not in article:
                    article['target_valuation'] = ['目标市值：600 亿（30 倍 PE，利润 20 亿）']
                    print(f"  ✅ 添加目标市值到文章：{article['title']}")
            
            # 保存回文件
            with open(MASTER_FILE, 'w', encoding='utf-8') as f:
                json.dump(master_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ 已添加目标市值")
        else:
            print("❌ 未找到国机精工")

if __name__ == '__main__':
    print("🚀 开始修正国机精工股票代码...\n")
    fix_guojing_stock()
    print("\n🎉 处理完成！")
