#!/usr/bin/env python3
"""
验证 GitHub 仓库数据完整性
"""
import json
from pathlib import Path

def verify_github_repo():
    """验证仓库数据"""
    print("🔍 验证 GitHub 仓库数据...\n")
    
    # 检查关键文件
    files_to_check = [
        "data/master/stocks_index.json",
        "data/master/stocks_master.json",
        "data/hot_topics.json",
        "data/master/stocks/2026-04-21.json",
        "templates/dashboard.html",
    ]
    
    base_dir = Path("e:/github/stock-research-backup")
    
    for file_path in files_to_check:
        full_path = base_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {file_path} ({size:,} 字节)")
        else:
            print(f"❌ {file_path} 不存在")
    
    # 检查 002416 和 301666 是否在索引中
    print("\n" + "="*60)
    index_file = base_dir / "data/master/stocks_index.json"
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    stocks_to_verify = {
        '002416': '爱施德',
        '301666': '力诺药包'
    }
    
    for code, name in stocks_to_verify.items():
        if code in index_data['stocks']:
            stock = index_data['stocks'][code]
            print(f"✅ {code} {name} 在索引中")
            print(f"   文件：{stock['file']}")
            print(f"   最后更新：{stock['last_updated']}")
        else:
            print(f"❌ {code} {name} 不在索引中")
    
    # 检查分片数据
    print("\n" + "="*60)
    shard_file = base_dir / "data/master/stocks/2026-04-21.json"
    with open(shard_file, 'r', encoding='utf-8') as f:
        shard_data = json.load(f)
    
    print(f"2026-04-21.json:")
    print(f"  股票数：{len(shard_data.get('stocks', {}))}")
    print(f"  更新计数：{shard_data.get('update_count', 0)}")
    
    for code, name in stocks_to_verify.items():
        if code in shard_data['stocks']:
            stock = shard_data['stocks'][code]
            print(f"  ✅ {code} {stock['name']}")
            print(f"     行业：{stock['industry']}")
            print(f"     文章数：{len(stock.get('articles', []))}")
        else:
            print(f"  ❌ {code} 不在分片文件中")

if __name__ == '__main__':
    verify_github_repo()
