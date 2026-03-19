#!/usr/bin/env python3
"""
合并邮件附件中的股票数据到 master.json
"""
import json
import sys
from datetime import datetime

def merge_stock_data(master_path, email_data_path, output_path=None):
    """合并邮件中的股票数据到 master.json"""
    
    # 读取 master.json
    with open(master_path, 'r', encoding='utf-8') as f:
        master = json.load(f)
    
    stocks = master.get('stocks', [])
    stock_dict = {s['code']: s for s in stocks}
    
    print(f"当前 master.json 有 {len(stocks)} 只股票")
    
    # 读取邮件附件数据
    with open(email_data_path, 'r', encoding='utf-8') as f:
        email_data = json.load(f)
    
    # 处理邮件数据（可能是列表或字典）
    new_stocks = []
    if isinstance(email_data, list):
        new_stocks = email_data
    elif isinstance(email_data, dict):
        if 'stocks' in email_data:
            new_stocks = email_data['stocks']
        else:
            # 单只股票
            new_stocks = [email_data]
    
    print(f"邮件附件中有 {len(new_stocks)} 只股票")
    
    # 合并
    added = 0
    updated = 0
    for stock in new_stocks:
        code = stock.get('code')
        if not code:
            print(f"⚠️ 跳过无代码的记录：{stock.get('name', 'Unknown')}")
            continue
        
        if code in stock_dict:
            # 更新现有股票
            old = stock_dict[code]
            for k, v in stock.items():
                if v is not None:  # 只更新非空值
                    old[k] = v
            updated += 1
            print(f"✏️ 更新：{code} {stock.get('name', '')}")
        else:
            # 添加新股票
            stocks.append(stock)
            stock_dict[code] = stock
            added += 1
            print(f"➕ 新增：{code} {stock.get('name', '')}")
    
    print(f"\n合并完成:")
    print(f"  新增：{added}")
    print(f"  更新：{updated}")
    print(f"  总计：{len(stocks)}")
    
    # 保存
    if output_path is None:
        output_path = master_path
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(master, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已保存到：{output_path}")
    
    return added, updated

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python3 merge_email_data.py <email_data.json> [output.json]")
        sys.exit(1)
    
    email_path = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None
    
    master_path = '/home/admin/openclaw/workspace/railway-deploy/data/master/stocks_master.json'
    merge_stock_data(master_path, email_path, output)
