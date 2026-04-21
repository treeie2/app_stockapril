#!/usr/bin/env python3
"""
修复股票名称，确保以代码为准
"""
import json
from pathlib import Path

def fix_stock_names():
    """检查并修复所有股票名称"""
    print("🔧 检查并修复股票名称...\n")
    
    # 读取索引文件（权威数据源）
    index_file = Path("e:/github/stock-research-backup/data/master/stocks_index.json")
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    index_stocks = index_data.get('stocks', {})
    print(f"📊 索引文件中有 {len(index_stocks)} 只股票\n")
    
    # 检查所有分片文件
    stocks_dir = Path("e:/github/stock-research-backup/data/master/stocks")
    all_files = sorted(stocks_dir.glob("*.json"), reverse=True)
    
    fixed_count = 0
    checked_count = 0
    
    for file_path in all_files:
        print(f"📂 处理 {file_path.name}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stocks = data.get('stocks', {})
        file_fixed = 0
        
        for code, stock in stocks.items():
            checked_count += 1
            current_name = stock.get('name', '')
            
            # 从索引获取正确名称
            if code in index_stocks:
                correct_name = index_stocks[code].get('name', '')
                
                if current_name != correct_name:
                    print(f"  ❌ {code}: '{current_name}' → '{correct_name}'")
                    stock['name'] = correct_name
                    file_fixed += 1
                    fixed_count += 1
        
        # 保存修改
        if file_fixed > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  ✅ 修复了 {file_fixed} 只股票\n")
        else:
            print(f"  ✅ 无需修复\n")
    
    print(f"\n📊 总结:")
    print(f"  检查了 {checked_count} 只股票")
    print(f"  修复了 {fixed_count} 只股票")

if __name__ == "__main__":
    fix_stock_names()
