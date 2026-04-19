#!/usr/bin/env python3
"""
检查长海股份的字段更新情况
"""
import json
from pathlib import Path

DATA_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")

def check_stock():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', {})
    stock = stocks.get('300196', {})
    
    print("🔍 长海股份(300196) 字段检查\n")
    print("="*60)
    
    print(f"名称: {stock.get('name', 'N/A')}")
    print(f"代码: {stock.get('code', 'N/A')}")
    print(f"行业: {stock.get('industry', 'N/A')}")
    
    print(f"\n📦 产品 ({len(stock.get('products', []))}项):")
    for item in stock.get('products', []):
        print(f"   - {item}")
    
    print(f"\n💼 核心业务 ({len(stock.get('core_business', []))}项):")
    for item in stock.get('core_business', []):
        print(f"   - {item}")
    
    print(f"\n🏆 行业地位 ({len(stock.get('industry_position', []))}项):")
    for item in stock.get('industry_position', []):
        print(f"   - {item}")
    
    print(f"\n🔗 产业链 ({len(stock.get('chain', []))}项):")
    for item in stock.get('chain', []):
        print(f"   - {item}")
    
    print(f"\n🤝 合作伙伴 ({len(stock.get('partners', []))}项):")
    for item in stock.get('partners', []):
        print(f"   - {item}")

if __name__ == "__main__":
    check_stock()
