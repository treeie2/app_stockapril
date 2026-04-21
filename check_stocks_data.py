#!/usr/bin/env python3
"""
检查股票数据是否存在
"""
import json
from pathlib import Path

def check_stocks():
    """检查 002416 和 301666"""
    stocks_to_check = {
        '002416': '爱施德',
        '301666': '力诺药包'
    }
    
    # 检查索引文件
    index_file = Path('data/master/stocks_index.json')
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    print("📊 检查股票数据...\n")
    
    for code, name in stocks_to_check.items():
        print(f"{'='*60}")
        print(f"检查：{code} {name}")
        print(f"{'='*60}")
        
        # 1. 检查索引
        if code in index_data['stocks']:
            stock_info = index_data['stocks'][code]
            print(f"✅ 索引文件：存在")
            print(f"   名称：{stock_info['name']}")
            print(f"   文件：{stock_info['file']}")
            print(f"   最后更新：{stock_info['last_updated']}")
            
            # 2. 检查分片文件
            shard_file = Path('data/master/stocks') / stock_info['file']
            if shard_file.exists():
                with open(shard_file, 'r', encoding='utf-8') as f:
                    shard_data = json.load(f)
                
                if code in shard_data['stocks']:
                    stock = shard_data['stocks'][code]
                    print(f"✅ 分片文件：存在")
                    print(f"   代码：{stock['code']}")
                    print(f"   名称：{stock['name']}")
                    print(f"   行业：{stock['industry']}")
                    print(f"   概念数：{len(stock.get('concepts', []))}")
                    print(f"   文章数：{len(stock.get('articles', []))}")
                    
                    if stock.get('articles'):
                        print(f"   文章标题：")
                        for article in stock['articles']:
                            print(f"     - {article.get('title', 'N/A')}")
                else:
                    print(f"❌ 分片文件：{code} 不存在")
            else:
                print(f"❌ 分片文件：{shard_file} 不存在")
        else:
            print(f"❌ 索引文件：{code} 不存在")
        
        # 3. 检查主文件
        master_file = Path('data/master/stocks_master.json')
        with open(master_file, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        if code in master_data['stocks']:
            print(f"✅ 主文件：存在")
        else:
            print(f"❌ 主文件：{code} 不存在")
        
        print()

if __name__ == '__main__':
    check_stocks()
