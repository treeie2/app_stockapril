#!/usr/bin/env python3
"""
检查 GitHub 上的 stocks_master.json
"""
import requests

url = 'https://raw.githubusercontent.com/treeie2/app_stockapril/main/data/master/stocks_master.json'

print("📥 正在从 GitHub 获取 stocks_master.json...")

try:
    response = requests.get(url, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n✅ GitHub 股票数：{len(data)}")
        print(f"✅ 002046 存在：{'002046' in data}")
        print(f"✅ 文件大小：{len(response.content)/1024/1024:.2f} MB")
        
        if '002046' in data:
            stock = data['002046']
            print(f"\n📊 002046 数据:")
            print(f"  Name: {stock.get('name')}")
            print(f"  Articles: {len(stock.get('articles', []))}")
            print(f"  Last Updated: {stock.get('last_updated', 'N/A')}")
    else:
        print(f"❌ 获取失败：{response.status_code}")
        
except Exception as e:
    print(f"❌ 错误：{e}")
