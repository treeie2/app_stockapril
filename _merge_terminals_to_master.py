"""
合并不同终端的日期分片文件到主文件
解决多终端处理时的数据合并问题
"""
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 配置
SKILL_DATA_DIR = Path(".trae/skills/wechat-fetch-research-embedded/data/master/stocks")
MASTER_FILE = Path("data/stocks/stocks_master.json")
OUTPUT_DIR = Path("data/stocks")


def load_master():
    """加载主文件"""
    if MASTER_FILE.exists():
        with open(MASTER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"stocks": {}}


def load_all_daily_files():
    """加载所有日期分片文件（包括不同终端的）"""
    all_files = {}
    
    for file_path in SKILL_DATA_DIR.glob("*.json"):
        # 解析文件名：2026-05-19.json 或 2026-05-19_trae.json
        stem = file_path.stem
        if '_' in stem:
            date, terminal = stem.split('_', 1)
        else:
            date, terminal = stem, 'default'
        
        if date not in all_files:
            all_files[date] = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            all_files[date][terminal] = json.load(f)
    
    return all_files


def deduplicate_articles(existing_articles, new_articles):
    """文章去重（按 source + title）"""
    seen = set()
    result = []
    
    for article in existing_articles + new_articles:
        key = (article.get('source', ''), article.get('title', ''))
        if key not in seen and key != ('', ''):
            seen.add(key)
            result.append(article)
    
    return result


def merge_first_level_fields(existing_stock, new_stock):
    """合并第一层字段"""
    merged = existing_stock.copy()
    
    # 合并列表字段（去重）
    for field in ['products', 'core_business', 'industry_position', 'chain', 'partners', 'concepts']:
        existing_set = set(existing_stock.get(field, []))
        new_set = set(new_stock.get(field, []))
        merged[field] = list(existing_set | new_set)
    
    # 更新字符串字段
    for field in ['name', 'code', 'board', 'industry']:
        if new_stock.get(field):
            merged[field] = new_stock[field]
    
    return merged


def merge_stock_data(master_stocks, daily_stocks, date):
    """合并单日数据到主文件"""
    stats = {
        'total_stocks': 0,
        'new_stocks': 0,
        'updated_stocks': 0,
        'new_articles': 0,
        'terminals': []
    }
    
    for terminal, data in daily_stocks.items():
        stats['terminals'].append(terminal)
        stocks = data.get('stocks', {})
        
        for code, stock in stocks.items():
            stats['total_stocks'] += 1
            
            if code in master_stocks:
                # 合并第一层字段
                master_stocks[code] = merge_first_level_fields(master_stocks[code], stock)
                
                # 合并文章
                existing_articles = master_stocks[code].get('articles', [])
                new_articles = stock.get('articles', [])
                
                before_count = len(existing_articles)
                merged_articles = deduplicate_articles(existing_articles, new_articles)
                after_count = len(merged_articles)
                
                master_stocks[code]['articles'] = merged_articles
                master_stocks[code]['mention_count'] = len(merged_articles)
                master_stocks[code]['last_updated'] = date
                
                if after_count > before_count:
                    stats['new_articles'] += (after_count - before_count)
                    stats['updated_stocks'] += 1
            else:
                # 新股票
                master_stocks[code] = stock
                master_stocks[code]['last_updated'] = date
                stats['new_stocks'] += 1
                stats['new_articles'] += len(stock.get('articles', []))
    
    return stats


def create_date_slice(master_stocks, date):
    """创建日期分片文件（只包含当天更新的股票）"""
    slice_data = {
        "date": date,
        "update_count": 0,
        "stocks": {}
    }
    
    for code, stock in master_stocks.items():
        if stock.get('last_updated') == date:
            slice_data['stocks'][code] = stock
            slice_data['update_count'] += 1
    
    return slice_data


def main():
    print("=" * 80)
    print("🔄 合并不同终端的日期分片文件到主文件")
    print("=" * 80)
    
    # 加载主文件
    print("\n📂 加载主文件...")
    master_data = load_master()
    master_stocks = master_data.get('stocks', {})
    print(f"   现有股票：{len(master_stocks)} 只")
    
    # 加载所有日期分片文件
    print("\n📂 加载日期分片文件...")
    all_daily_files = load_all_daily_files()
    print(f"   找到 {len(all_daily_files)} 个日期")
    
    # 统计
    total_stats = {
        'dates': 0,
        'terminals': set(),
        'total_stocks': 0,
        'new_stocks': 0,
        'updated_stocks': 0,
        'new_articles': 0
    }
    
    # 按日期排序（最新的在前）
    sorted_dates = sorted(all_daily_files.keys(), reverse=True)
    
    for date in sorted_dates:
        daily_stocks = all_daily_files[date]
        print(f"\n📄 处理日期：{date}")
        print(f"   终端：{', '.join(daily_stocks.keys())}")
        
        # 合并数据
        stats = merge_stock_data(master_stocks, daily_stocks, date)
        
        # 更新统计
        total_stats['dates'] += 1
        total_stats['terminals'].update(stats['terminals'])
        total_stats['total_stocks'] += stats['total_stocks']
        total_stats['new_stocks'] += stats['new_stocks']
        total_stats['updated_stocks'] += stats['updated_stocks']
        total_stats['new_articles'] += stats['new_articles']
        
        print(f"   处理股票：{stats['total_stocks']} 只")
        print(f"   新增股票：{stats['new_stocks']} 只")
        print(f"   更新股票：{stats['updated_stocks']} 只")
        print(f"   新增文章：{stats['new_articles']} 篇")
        
        # 创建日期分片
        slice_data = create_date_slice(master_stocks, date)
        slice_file = OUTPUT_DIR / f"{date}.json"
        with open(slice_file, 'w', encoding='utf-8') as f:
            json.dump(slice_data, f, ensure_ascii=False, indent=2)
        print(f"   创建分片：{slice_file.name} ({slice_data['update_count']} 只)")
    
    # 保存主文件
    print("\n💾 保存主文件...")
    master_data['stocks'] = master_stocks
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)
    
    # 统计第一层信息完整度
    complete = sum(1 for s in master_stocks.values() if s.get('products') and s.get('core_business') and s.get('industry_position'))
    
    print("\n" + "=" * 80)
    print("📊 合并结果:")
    print(f"   处理日期数：{total_stats['dates']}")
    print(f"   涉及终端：{', '.join(sorted(total_stats['terminals']))}")
    print(f"   处理股票数：{total_stats['total_stocks']}")
    print(f"   新增股票：{total_stats['new_stocks']} 只")
    print(f"   更新股票：{total_stats['updated_stocks']} 只")
    print(f"   新增文章：{total_stats['new_articles']} 篇")
    print(f"   总股票数：{len(master_stocks)} 只")
    print(f"   完整第一层信息：{complete} 只 ({complete/len(master_stocks)*100:.1f}%)")
    print("\n✅ 完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()