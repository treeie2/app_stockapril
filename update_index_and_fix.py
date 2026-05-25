#!/usr/bin/env python3
"""
更新 stocks_index.json 并修复股票名称问题
"""
import json
from pathlib import Path
from datetime import datetime

def update_index():
    """更新 stocks_index.json"""
    index_file = Path("data/stocks/stocks_index.json")
    stocks_dir = Path("data/stocks")
    
    # 读取现有索引
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    # 读取 2026-04-21.json
    today_file = stocks_dir / "2026-04-21.json"
    if not today_file.exists():
        print("❌ 2026-04-21.json 不存在")
        return False
    
    with open(today_file, 'r', encoding='utf-8') as f:
        today_data = json.load(f)
    
    stocks = today_data.get('stocks', {})
    
    # 更新索引
    updated_count = 0
    for code, stock in stocks.items():
        index_data['stocks'][code] = {
            'name': stock.get('name', ''),
            'last_updated': '2026-04-21',
            'file': '2026-04-21.json'
        }
        updated_count += 1
    
    # 更新元数据
    index_data['last_updated'] = '2026-04-21'
    index_data['total_stocks'] = len(index_data['stocks'])
    
    # 保存索引
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 索引已更新，新增 {updated_count} 只股票")
    print(f"   总股票数：{index_data['total_stocks']}")
    
    return True

def fix_002201():
    """修复 002201 的股票名称"""
    stocks_dir = Path("data/stocks")
    
    # 遍历所有数据文件
    for json_file in stocks_dir.glob("*.json"):
        if json_file.name == "stocks_index.json":
            continue
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            stocks = data.get('stocks', {})
            
            # 检查是否有 002201
            if '002201' in stocks:
                stock = stocks['002201']
                old_name = stock.get('name', '')
                
                # 修复名称
                if old_name in ['航空航天', '商业航天']:
                    stock['name'] = '正威新材'
                    
                    # 更新概念
                    if 'concepts' not in stock:
                        stock['concepts'] = []
                    
                    # 添加正确的概念
                    if '商业航天' not in stock['concepts']:
                        stock['concepts'].append('商业航天')
                    if '电子布' not in stock['concepts']:
                        stock['concepts'].append('电子布')
                    if '玻璃纤维' not in stock['concepts']:
                        stock['concepts'].append('玻璃纤维')
                    
                    print(f"✅ 修复 {json_file.name}: 002201")
                    print(f"   原名称：{old_name}")
                    print(f"   新名称：正威新材")
                    print(f"   概念：{stock['concepts']}")
                    
                    # 保存文件
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
        except Exception as e:
            print(f"读取 {json_file} 失败：{e}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("更新 stocks_index.json")
    print("=" * 60)
    
    update_index()
    
    print("\n" + "=" * 60)
    print("修复 002201 股票名称")
    print("=" * 60)
    
    fix_002201()
    
    print("\n" + "=" * 60)
    print("更新完成！")
    print("=" * 60)
