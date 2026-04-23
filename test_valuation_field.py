#!/usr/bin/env python3
"""
测试 target_market_cap_billion 字段的加载和显示
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
MASTER_FILE = BASE_DIR / 'data' / 'master' / 'stocks_master.json'

def test_valuation_field():
    print("📊 测试 valuation 字段支持...\n")
    
    # 1. 读取 master 文件
    print("📋 加载 stocks_master.json...")
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    stocks = master_data.get('stocks', {})
    print(f"  总计：{len(stocks)} 只股票\n")
    
    # 2. 查找有 valuation 信息的股票
    stocks_with_valuation = []
    for code, stock in stocks.items():
        valuation = stock.get('valuation', {})
        if valuation and (valuation.get('target_market_cap') or valuation.get('target_market_cap_billion')):
            stocks_with_valuation.append({
                'code': code,
                'name': stock.get('name', ''),
                'valuation': valuation
            })
    
    print(f"✅ 发现 {len(stocks_with_valuation)} 只股票有估值信息\n")
    
    # 3. 显示前 10 只股票的估值信息
    if stocks_with_valuation:
        print("📊 前 10 只股票的估值信息：")
        print("-" * 80)
        for i, stock in enumerate(stocks_with_valuation[:10], 1):
            valuation = stock['valuation']
            target_cap_text = valuation.get('target_market_cap', 'N/A')
            target_cap_num = valuation.get('target_market_cap_billion', 'N/A')
            
            print(f"{i}. {stock['code']} - {stock['name']}")
            print(f"   目标市值（文本）: {target_cap_text}")
            print(f"   目标市值（数值）: {target_cap_num} 亿")
            print()
    
    # 4. 检查规范文档
    print("\n📋 检查数据结构规范文档...")
    spec_file = BASE_DIR / 'data' / '数据结构规范_v2.md'
    if spec_file.exists():
        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'target_market_cap_billion' in content:
                print("  ✅ 规范文档已包含 target_market_cap_billion 字段")
            else:
                print("  ❌ 规范文档未包含 target_market_cap_billion 字段")
    else:
        print("  ⚠️ 规范文档不存在")
    
    # 5. 检查模板文件
    print("\n📋 检查个股页面模板...")
    template_file = BASE_DIR / 'templates' / 'stock_detail.html'
    if template_file.exists():
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'target_market_cap_billion' in content:
                print("  ✅ 模板文件已包含 target_market_cap_billion 显示逻辑")
            else:
                print("  ❌ 模板文件未包含 target_market_cap_billion 显示逻辑")
    else:
        print("  ⚠️ 模板文件不存在")
    
    # 6. 检查 Firebase 同步代码
    print("\n📋 检查 Firebase 同步代码...")
    sync_file = BASE_DIR / 'sync_today_to_firebase.py'
    if sync_file.exists():
        with open(sync_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'target_market_cap_billion' in content:
                print("  ✅ 同步脚本已支持 target_market_cap_billion 字段")
            else:
                print("  ❌ 同步脚本未支持 target_market_cap_billion 字段")
    else:
        print("  ⚠️ 同步脚本不存在")
    
    print("\n✅ 测试完成！")

if __name__ == '__main__':
    test_valuation_field()
