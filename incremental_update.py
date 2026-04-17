#!/usr/bin/env python3
"""
增量更新机制 - 将 stocks_master.json 转换为按日期分片存储
"""
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DATA_DIR = Path("e:/github/stock-research-backup/data/master")
MASTER_FILE = DATA_DIR / "stocks_master.json"
INDEX_FILE = DATA_DIR / "stocks_index.json"
STOCKS_DIR = DATA_DIR / "stocks"

def build_incremental_data():
    """从主文件构建增量数据结构"""
    print("📖 读取主数据文件...")
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', {})
    if isinstance(stocks, list):
        stocks = {s.get('code'): s for s in stocks}
    
    print(f"📊 共 {len(stocks)} 只股票")
    
    # 按日期分组
    daily_stocks = defaultdict(dict)
    stock_index = {}
    
    for code, stock in stocks.items():
        # 获取最后更新时间
        last_updated = stock.get('last_updated', '')
        if not last_updated:
            # 如果没有 last_updated，使用最新文章的日期
            articles = stock.get('articles', [])
            if articles:
                last_updated = articles[-1].get('date', '2026-01-01')
            else:
                last_updated = '2026-01-01'
        
        # 只取日期部分
        date_key = last_updated[:10] if len(last_updated) >= 10 else last_updated
        
        # 添加到对应日期的分组
        daily_stocks[date_key][code] = stock
        
        # 更新索引
        stock_index[code] = {
            "name": stock.get('name', ''),
            "last_updated": last_updated,
            "file": f"{date_key}.json"
        }
    
    return daily_stocks, stock_index

def save_incremental_files(daily_stocks, stock_index):
    """保存增量文件"""
    # 创建 stocks 目录
    STOCKS_DIR.mkdir(exist_ok=True)
    
    # 保存每日分片文件
    for date, stocks in sorted(daily_stocks.items()):
        file_path = STOCKS_DIR / f"{date}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "date": date,
                "update_count": len(stocks),
                "stocks": stocks
            }, f, ensure_ascii=False, indent=2)
        print(f"   ✅ {date}.json - {len(stocks)} 只股票")
    
    # 保存索引文件
    index_data = {
        "version": "2.0",
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "total_stocks": len(stock_index),
        "stocks": stock_index
    }
    
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    print(f"   ✅ stocks_index.json - {len(stock_index)} 只股票")

def load_recent_stocks(days=7):
    """加载最近 N 天的股票数据"""
    if not INDEX_FILE.exists():
        print("❌ 索引文件不存在")
        return {}
    
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    # 获取最近 N 天的日期
    today = datetime.now()
    recent_dates = [
        (today.replace(day=today.day - i)).strftime("%Y-%m-%d")
        for i in range(days)
    ]
    
    # 加载对应日期的数据
    all_stocks = {}
    for date in recent_dates:
        file_path = STOCKS_DIR / f"{date}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_stocks.update(data.get('stocks', {}))
    
    return all_stocks

def update_stock_incremental(stock_code, stock_data):
    """增量更新单只股票"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 更新当天分片文件
    daily_file = STOCKS_DIR / f"{today}.json"
    if daily_file.exists():
        with open(daily_file, 'r', encoding='utf-8') as f:
            daily_data = json.load(f)
    else:
        daily_data = {"date": today, "update_count": 0, "stocks": {}}
    
    # 添加/更新股票
    daily_data['stocks'][stock_code] = stock_data
    daily_data['update_count'] = len(daily_data['stocks'])
    
    with open(daily_file, 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)
    
    # 更新索引
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = {"version": "2.0", "last_updated": today, "total_stocks": 0, "stocks": {}}
    
    index['stocks'][stock_code] = {
        "name": stock_data.get('name', ''),
        "last_updated": stock_data.get('last_updated', today),
        "file": f"{today}.json"
    }
    index['total_stocks'] = len(index['stocks'])
    index['last_updated'] = today
    
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已增量更新: {stock_data.get('name', stock_code)} -> {today}.json")

if __name__ == "__main__":
    print("🚀 构建增量数据结构...\n")
    
    # 构建增量数据
    daily_stocks, stock_index = build_incremental_data()
    
    print(f"\n📁 保存增量文件...")
    save_incremental_files(daily_stocks, stock_index)
    
    print(f"\n✅ 完成!")
    print(f"   - 共 {len(daily_stocks)} 个日期分片")
    print(f"   - 共 {len(stock_index)} 只股票")
    
    # 测试加载最近7天
    print(f"\n🧪 测试加载最近7天数据...")
    recent = load_recent_stocks(7)
    print(f"   - 加载了 {len(recent)} 只股票")
