#!/usr/bin/env python3
"""
检查 GitHub 仓库中的 stocks_master.json 文件内容
"""
import requests
import json

# GitHub API URL
url = "https://raw.githubusercontent.com/treeie2/app_stockapril/main/data/master/stocks_master.json"

print("📥 正在从 GitHub 获取 stocks_master.json...")

try:
    response = requests.get(url, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        
        # 检查 002046
        if '002046' in data:
            stock = data['002046']
            print("\n✅ GitHub 上的 002046 数据:")
            print(f"  Name: {stock.get('name')}")
            print(f"  Industry: {stock.get('industry')}")
            print(f"  Core Business: {stock.get('core_business', [])}")
            print(f"  Industry Position: {stock.get('industry_position', [])}")
            print(f"  Chain: {stock.get('chain', [])}")
            print(f"  Last Updated: {stock.get('last_updated', 'N/A')}")
            print(f"  Articles: {len(stock.get('articles', []))}")
            if stock.get('articles'):
                article = stock['articles'][0]
                print(f"    - Title: {article.get('title', 'N/A')}")
                print(f"    - Date: {article.get('date', 'N/A')}")
                print(f"    - Source: {article.get('source', 'N/A')}")
        else:
            print("❌ GitHub 上没有 002046 的数据")
        
        print(f"\n📊 GitHub 上总股票数：{len(data)}")
        
    else:
        print(f"❌ 获取失败：{response.status_code}")
        
except Exception as e:
    print(f"❌ 错误：{e}")
