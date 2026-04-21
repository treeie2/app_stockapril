#!/usr/bin/env python3
"""
检查 002416 股票
"""
import json
from pathlib import Path

def check_stock(code):
    """检查股票是否存在"""
    index_file = Path("data/master/stocks_index.json")
    
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    stocks = index_data.get('stocks', {})
    
    if code in stocks:
        stock_info = stocks[code]
        print(f"✅ {code} - {stock_info['name']}")
        print(f"   最后更新：{stock_info['last_updated']}")
        print(f"   所在文件：{stock_info['file']}")
        
        # 读取详细数据
        file_path = Path("data/master/stocks") / stock_info['file']
        with open(file_path, 'r', encoding='utf-8') as f:
            daily_data = json.load(f)
        
        stock_detail = daily_data['stocks'].get(code, {})
        print(f"\n详细信息:")
        print(f"   行业：{stock_detail.get('industry', 'N/A')}")
        print(f"   概念：{', '.join(stock_detail.get('concepts', []))}")
        print(f"   产品：{', '.join(stock_detail.get('products', []))}")
        print(f"   文章数：{len(stock_detail.get('articles', []))}")
    else:
        print(f"❌ {code} 不在数据库中")
        print(f"   可能需要添加这只股票的数据")

if __name__ == "__main__":
    check_stock("002416")
