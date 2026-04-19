#!/usr/bin/env python3
"""
检查联赢激光的所有字段
"""
import json
from pathlib import Path

DATA_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")

def check_all_fields():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', {})
    stock = stocks.get('688518', {})
    
    print("🔍 联赢激光(688518) 完整字段检查\n")
    print("="*60)
    
    fields_to_check = [
        'name', 'code', 'board', 'industry', 'concepts', 'mention_count',
        'products', 'core_business', 'industry_position', 'chain', 'partners'
    ]
    
    for field in fields_to_check:
        value = stock.get(field)
        if isinstance(value, list):
            if value:
                print(f"\n✅ {field}: ({len(value)}项)")
                for item in value[:5]:
                    print(f"   - {item}")
                if len(value) > 5:
                    print(f"   ... 等共{len(value)}项")
            else:
                print(f"\n❌ {field}: 空列表")
        elif isinstance(value, str):
            if value:
                print(f"\n✅ {field}: {value}")
            else:
                print(f"\n❌ {field}: 空字符串")
        elif isinstance(value, int):
            print(f"\n✅ {field}: {value}")
        else:
            print(f"\n❌ {field}: {value}")
    
    # 检查文章的 target_valuation
    print(f"\n{'='*60}")
    print("📝 文章字段检查:")
    articles = stock.get('articles', [])
    if articles:
        article = articles[0]
        for field in ['title', 'date', 'target_valuation', 'key_metrics']:
            value = article.get(field)
            if isinstance(value, list):
                if value:
                    print(f"\n✅ {field}: {value}")
                else:
                    print(f"\n❌ {field}: 空列表")
            else:
                print(f"\n✅ {field}: {value}")

if __name__ == "__main__":
    check_all_fields()
