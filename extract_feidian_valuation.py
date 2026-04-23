#!/usr/bin/env python3
"""
从沸点公众号文章数据中提取 target_market_cap_billion 字段
并整合到股票级别的 valuation 中
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
FEIDIAN_FILE = BASE_DIR / 'raw_material' / 'stocks_master_feidian_metrics.json'
MASTER_FILE = BASE_DIR / 'data' / 'master' / 'stocks_master.json'

def extract_valuation_metrics():
    print("📊 提取沸点文章中的估值指标...\n")
    
    # 1. 加载沸点数据
    print("📋 加载 stocks_master_feidian_metrics.json...")
    try:
        with open(FEIDIAN_FILE, 'r', encoding='utf-8') as f:
            feidian_data = json.load(f)
    except Exception as e:
        print(f"❌ 加载失败：{e}")
        return
    
    feidian_stocks = feidian_data.get('stocks', [])
    print(f"  找到 {len(feidian_stocks)} 只股票\n")
    
    # 2. 提取估值信息
    valuation_data = {}
    stocks_with_valuation = 0
    
    for stock in feidian_stocks:
        code = stock.get('code', '')
        name = stock.get('name', '')
        
        # 跳过没有代码的股票
        if not code:
            continue
        
        # 检查文章中的 valuation_metrics
        articles = stock.get('articles', [])
        for article in articles:
            val_metrics = article.get('valuation_metrics', {})
            if val_metrics:
                target_cap = val_metrics.get('target_market_cap', '')
                target_cap_billion = val_metrics.get('target_market_cap_billion')
                
                if target_cap_billion is not None:
                    if code not in valuation_data:
                        valuation_data[code] = {
                            'name': name,
                            'target_market_cap': target_cap,
                            'target_market_cap_billion': float(target_cap_billion)
                        }
                        stocks_with_valuation += 1
                        print(f"  ✅ {code} - {name}: {target_cap_billion} 亿 ({target_cap})")
    
    print(f"\n✅ 共找到 {stocks_with_valuation} 只股票有估值数据\n")
    
    # 3. 更新到 master 文件
    if valuation_data:
        print("📋 更新 stocks_master.json...")
        with open(MASTER_FILE, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        master_stocks = master_data.get('stocks', {})
        updated_count = 0
        
        for code, val_info in valuation_data.items():
            if code in master_stocks:
                # 更新或添加 valuation 信息
                if 'valuation' not in master_stocks[code]:
                    master_stocks[code]['valuation'] = {}
                
                # 优先使用沸点数据的数值
                master_stocks[code]['valuation']['target_market_cap'] = val_info['target_market_cap']
                master_stocks[code]['valuation']['target_market_cap_billion'] = val_info['target_market_cap_billion']
                updated_count += 1
        
        # 保存
        with open(MASTER_FILE, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 更新 {updated_count} 只股票的估值信息\n")
        
        # 4. 显示更新后的示例
        print("📊 更新后的估值信息示例：")
        print("-" * 80)
        for i, (code, val_info) in enumerate(list(valuation_data.items())[:5], 1):
            print(f"{i}. {code} - {val_info['name']}")
            print(f"   目标市值（文本）: {val_info['target_market_cap']}")
            print(f"   目标市值（数值）: {val_info['target_market_cap_billion']} 亿")
            print()
    
    print("✅ 处理完成！")

if __name__ == '__main__':
    extract_valuation_metrics()
