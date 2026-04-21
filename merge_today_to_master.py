#!/usr/bin/env python3
"""
将当天分片数据合并到 stocks_master.json
"""
import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data/master")
MASTER_FILE = DATA_DIR / "stocks_master.json"
TODAY_FILE = DATA_DIR / "stocks" / "2026-04-21.json"

def merge_to_master():
    """将当天数据合并到主文件"""
    print("🔄 合并 2026-04-21 数据到 stocks_master.json...\n")
    
    # 读取当天分片数据
    if not TODAY_FILE.exists():
        print(f"❌ 当天分片文件不存在：{TODAY_FILE}")
        return False
    
    with open(TODAY_FILE, 'r', encoding='utf-8') as f:
        today_data = json.load(f)
    
    today_stocks = today_data.get('stocks', {})
    print(f"📊 当天更新：{len(today_stocks)} 只股票")
    
    # 读取主文件
    if MASTER_FILE.exists():
        with open(MASTER_FILE, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        # 支持字典或列表格式
        if isinstance(master_data, dict):
            if 'stocks' in master_data:
                master_stocks = master_data['stocks']
            else:
                master_stocks = master_data
        elif isinstance(master_data, list):
            # 转换为字典
            master_stocks = {s.get('code'): s for s in master_data if 'code' in s}
        else:
            master_stocks = {}
    else:
        master_stocks = {}
    
    print(f"📊 主文件现有：{len(master_stocks)} 只股票")
    
    # 合并数据
    merged_count = 0
    new_count = 0
    
    for code, stock in today_stocks.items():
        if code in master_stocks:
            # 更新现有股票
            existing = master_stocks[code]
            
            # 合并文章（去重）
            existing_articles = existing.get('articles', [])
            new_articles = stock.get('articles', [])
            
            # 按 (source, title) 去重
            existing_keys = {(a.get('source'), a.get('title')) for a in existing_articles}
            for article in new_articles:
                key = (article.get('source'), article.get('title'))
                if key not in existing_keys:
                    existing_articles.append(article)
                    existing_keys.add(key)
            
            # 更新其他字段
            existing['mention_count'] = stock.get('mention_count', existing.get('mention_count', 0))
            existing['last_updated'] = stock.get('last_updated', datetime.now().strftime('%Y-%m-%d'))
            
            # 合并概念（去重）
            if 'concepts' in stock:
                existing_concepts = set(existing.get('concepts', []))
                existing_concepts.update(stock['concepts'])
                existing['concepts'] = list(existing_concepts)
            
            merged_count += 1
        else:
            # 添加新股票
            master_stocks[code] = stock
            new_count += 1
    
    print(f"\n✅ 合并完成：")
    print(f"   - 更新：{merged_count} 只股票")
    print(f"   - 新增：{new_count} 只股票")
    print(f"   - 总计：{len(master_stocks)} 只股票")
    
    # 保存主文件
    output_data = {'stocks': master_stocks}
    
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 已保存到：{MASTER_FILE}")
    
    return True

if __name__ == "__main__":
    success = merge_to_master()
    if success:
        print("\n✅ 合并成功！")
    else:
        print("\n❌ 合并失败！")
