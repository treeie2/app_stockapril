#!/usr/bin/env python3
"""
整合新的个股数据到 stocks_master.json 并同步到 Firebase
"""
import json
from pathlib import Path
from datetime import datetime

# 获取项目根目录
BASE_DIR = Path(__file__).parent

# 文件路径
NEW_DATA_FILE = BASE_DIR / 'raw_material' / 'stocks_from_raw_materials_complete_2026-04-23.json'
MASTER_FILE = BASE_DIR / 'data' / 'master' / 'stocks_master.json'
STOCKS_DIR = BASE_DIR / 'data' / 'master' / 'stocks'
INDEX_FILE = BASE_DIR / 'data' / 'master' / 'stocks_index.json'

def load_json(file_path):
    """加载 JSON 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载 {file_path} 失败：{e}")
        return None

def save_json(file_path, data):
    """保存 JSON 文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 保存到 {file_path}")
        return True
    except Exception as e:
        print(f"❌ 保存 {file_path} 失败：{e}")
        return False

def merge_stocks(master_stocks, new_stocks, today):
    """合并股票数据"""
    updated_count = 0
    new_count = 0
    
    for new_stock in new_stocks:
        code = new_stock.get('code')
        if not code:
            continue
        
        # 添加 last_updated 字段
        new_stock['last_updated'] = today
        
        if code in master_stocks:
            # 更新现有股票
            old_stock = master_stocks[code]
            
            # 合并数据（新数据优先）
            merged = {**old_stock, **new_stock}
            
            # 合并文章（去重）
            old_articles = old_stock.get('articles', [])
            new_articles = new_stock.get('articles', [])
            
            # 使用标题去重
            existing_titles = {a.get('title', '') for a in old_articles}
            for article in new_articles:
                if article.get('title', '') not in existing_titles:
                    old_articles.append(article)
            
            merged['articles'] = old_articles
            
            # 更新提及次数
            merged['mention_count'] = old_stock.get('mention_count', 0) + new_stock.get('mention_count', 0)
            
            master_stocks[code] = merged
            updated_count += 1
            print(f"  📝 更新：{code} - {new_stock.get('name', '')}")
        else:
            # 添加新股票
            master_stocks[code] = new_stock
            new_count += 1
            print(f"  ✨ 新增：{code} - {new_stock.get('name', '')}")
    
    return updated_count, new_count

def main():
    print("🚀 开始整合个股数据...\n")
    
    # 1. 加载新数据
    print("📋 加载新数据...")
    new_data = load_json(NEW_DATA_FILE)
    if not new_data:
        return
    
    new_stocks = new_data.get('stocks', [])
    print(f"  找到 {len(new_stocks)} 只股票\n")
    
    # 2. 加载 master 数据
    print("📋 加载 stocks_master.json...")
    master_data = load_json(MASTER_FILE)
    if not master_data:
        master_data = {'stocks': {}}
    
    master_stocks = master_data.get('stocks', {})
    print(f"  当前 master 中有 {len(master_stocks)} 只股票\n")
    
    # 3. 合并数据
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"📋 合并数据（日期：{today}）...")
    updated_count, new_count = merge_stocks(master_stocks, new_stocks, today)
    print(f"  更新：{updated_count} 只，新增：{new_count} 只\n")
    
    # 4. 保存 master 文件
    print("📋 保存 stocks_master.json...")
    master_data['stocks'] = master_stocks
    if not save_json(MASTER_FILE, master_data):
        return
    
    # 5. 保存到今天日期的增量文件
    today_file = STOCKS_DIR / f"{today}.json"
    print(f"📋 保存增量文件 {today_file.name}...")
    today_data = {
        'stocks': {code: stock for code, stock in master_stocks.items() if stock.get('last_updated') == today},
        'updated_at': today
    }
    if not save_json(today_file, today_data):
        return
    
    # 6. 更新索引
    print("📋 更新 stocks_index.json...")
    index_data = load_json(INDEX_FILE)
    if not index_data:
        index_data = {'version': '2.0', 'last_updated': today, 'total_stocks': 0, 'stocks': {}}
    
    # 更新索引中的股票信息
    for code, stock in master_stocks.items():
        if stock.get('last_updated') == today:
            index_data['stocks'][code] = {
                'name': stock.get('name', ''),
                'last_updated': today,
                'file': f"{today}.json"
            }
    
    index_data['total_stocks'] = len(master_stocks)
    index_data['last_updated'] = today
    
    if not save_json(INDEX_FILE, index_data):
        return
    
    print(f"\n✅ 整合完成！")
    print(f"   - 更新股票：{updated_count} 只")
    print(f"   - 新增股票：{new_count} 只")
    print(f"   - 总计股票：{len(master_stocks)} 只")
    print(f"   - 数据文件：{MASTER_FILE}")
    print(f"   - 增量文件：{today_file}")
    
    # 7. 提示同步到 Firebase
    print(f"\n💡 下一步：运行以下命令同步到 Firebase")
    print(f"   python -c \"from main import sync_stocks_to_firebase; sync_stocks_to_firebase()\"")

if __name__ == '__main__':
    main()
