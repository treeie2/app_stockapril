#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复晶科科技（601778）重复文章问题
合并相同 source 和 title 的文章，删除重复项
"""
import json
from pathlib import Path
from datetime import datetime

# 数据文件路径
DATA_FILE = Path(__file__).parent / 'data' / 'master' / 'stocks_master.json'

def fix_duplicate_articles():
    """修复重复文章"""
    
    print(f"处理文件：{DATA_FILE.name}")
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 数据结构可能是 {"stocks": {...}} 或直接是 {...}
    if 'stocks' in data:
        stocks = data['stocks']
    else:
        stocks = data
    
    # 检查 601778（晶科科技）
    if '601778' not in stocks:
        print("❌ 未找到 601778（晶科科技）")
        return 0
        
    stock = stocks['601778']
    articles = stock.get('articles', [])
    
    if not articles:
        print("❌ 晶科科技没有文章")
        return 0
        
    print(f"晶科科技文章数：{len(articles)}")
    
    # 按 (source, title) 去重
    seen = set()
    unique_articles = []
    duplicates = []
    
    for article in articles:
        source = article.get('source', '')
        title = article.get('title', '')
        key = (source, title)
        
        if key in seen:
            duplicates.append(article)
            print(f"  ❌ 重复：{title[:50]}...")
        else:
            seen.add(key)
            unique_articles.append(article)
            print(f"  ✅ 保留：{title[:50]}...")
    
    if duplicates:
        print(f"删除 {len(duplicates)} 篇重复文章，保留 {len(unique_articles)} 篇")
        
        # 更新文章列表（保持最新在前）
        stock['articles'] = unique_articles
        
        # 保存回文件
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存到 {DATA_FILE.name}")
        print(f"\n{'='*60}")
        print(f"修复完成！共删除 {len(duplicates)} 篇重复文章")
        
        return len(duplicates)
    else:
        print("✅ 没有发现重复文章")
        return 0

if __name__ == '__main__':
    fix_duplicate_articles()
