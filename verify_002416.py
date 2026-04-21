#!/usr/bin/env python3
"""
验证 002416 数据
"""
import json
from pathlib import Path

def verify_002416():
    """验证 002416 数据"""
    # 检查索引
    index_file = Path('data/master/stocks_index.json')
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    if '002416' in index_data['stocks']:
        print(f"✅ 002416 在索引中")
        print(f"   名称：{index_data['stocks']['002416']['name']}")
        print(f"   文件：{index_data['stocks']['002416']['file']}")
        print(f"   最后更新：{index_data['stocks']['002416']['last_updated']}")
        
        # 检查分片文件
        file_name = index_data['stocks']['002416']['file']
        shard_file = Path('data/master/stocks') / file_name
        
        if shard_file.exists():
            with open(shard_file, 'r', encoding='utf-8') as f:
                shard_data = json.load(f)
            
            if '002416' in shard_data['stocks']:
                stock = shard_data['stocks']['002416']
                print(f"\n✅ 分片文件中有数据")
                print(f"   名称：{stock['name']}")
                print(f"   代码：{stock['code']}")
                print(f"   行业：{stock['industry']}")
                print(f"   概念：{stock['concepts']}")
                print(f"   文章数：{len(stock['articles'])}")
            else:
                print(f"\n❌ 分片文件中没有 002416 数据")
        else:
            print(f"\n❌ 分片文件不存在：{shard_file}")
    else:
        print(f"❌ 002416 不在索引中")
    
    # 检查主文件
    master_file = Path('data/master/stocks_master.json')
    with open(master_file, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    if '002416' in master_data['stocks']:
        print(f"\n✅ 主文件中有 002416")
        stock = master_data['stocks']['002416']
        print(f"   名称：{stock['name']}")
        print(f"   代码：{stock['code']}")
        print(f"   文章数：{len(stock['articles'])}")
    else:
        print(f"\n❌ 主文件中没有 002416")

if __name__ == '__main__':
    verify_002416()
