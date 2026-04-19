#!/usr/bin/env python3
"""
检查联赢激光(688518)的数据
"""
import json
from pathlib import Path

DATA_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")

def check_stock():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', {})
    
    print("🔍 检查联赢激光(688518)...\n")
    
    if '688518' in stocks:
        stock = stocks['688518']
        print(f"✅ 找到股票: {stock.get('name', 'N/A')}({stock.get('code', 'N/A')})")
        print(f"\n📋 基本信息:")
        print(f"   名称: {stock.get('name', 'N/A')}")
        print(f"   代码: {stock.get('code', 'N/A')}")
        print(f"   板块: {stock.get('board', 'N/A')}")
        print(f"   行业: {stock.get('industry', 'N/A')}")
        print(f"   概念: {stock.get('concepts', [])}")
        print(f"   提及次数: {stock.get('mention_count', 0)}")
        
        print(f"\n📝 文章数量: {len(stock.get('articles', []))}")
        for i, article in enumerate(stock.get('articles', []), 1):
            print(f"\n   文章 {i}:")
            print(f"      标题: {article.get('title', 'N/A')[:50]}...")
            print(f"      日期: {article.get('date', 'N/A')}")
            print(f"      来源: {article.get('source', 'N/A')}")
            print(f"      摘要: {article.get('summary', 'N/A')[:80]}...")
    else:
        print("❌ 未找到联赢激光(688518)")
        
        # 查找类似代码
        print(f"\n🔍 查找类似代码:")
        for code in list(stocks.keys())[:20]:
            if code.startswith('688'):
                print(f"   {code}: {stocks[code].get('name', 'N/A')}")

if __name__ == "__main__":
    check_stock()
