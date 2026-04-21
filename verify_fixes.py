#!/usr/bin/env python3
"""
验证所有修复
"""
import json
from pathlib import Path

def verify_hot_topics():
    """验证 hot_topics.json 修复"""
    print("=" * 60)
    print("验证 hot_topics.json")
    print("=" * 60)
    
    hot_topics_file = Path("data/hot_topics.json")
    with open(hot_topics_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for topic in data.get('topics', []):
        if topic.get('name') == '荣耀机器人 IPO':
            stocks = topic.get('stocks', [])
            print(f"✅ 热点名称：{topic['name']}")
            print(f"   驱动因素：{topic['drivers']}")
            print(f"   影子股数量：{len(stocks)}")
            print(f"   影子股列表：{', '.join(stocks)}")
            
            # 验证格式
            if isinstance(stocks, list) and len(stocks) == 9:
                print(f"   ✅ 格式正确（9 只股票，数组格式）")
            else:
                print(f"   ❌ 格式错误")
            
            return True
    
    print("❌ 未找到荣耀机器人 IPO 热点")
    return False

def verify_2026_04_21():
    """验证 2026-04-21.json"""
    print("\n" + "=" * 60)
    print("验证 2026-04-21.json")
    print("=" * 60)
    
    today_file = Path("data/master/stocks/2026-04-21.json")
    if not today_file.exists():
        print("❌ 2026-04-21.json 不存在")
        return False
    
    with open(today_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', {})
    print(f"✅ 文件已创建")
    print(f"   日期：{data.get('date')}")
    print(f"   更新数量：{data.get('update_count')}")
    print(f"   股票数量：{len(stocks)}")
    
    # 验证股票代码
    expected_codes = ['002475', '002138', '300433', '002600', '688322', '300602', '300136', '300115', '002440']
    actual_codes = list(stocks.keys())
    
    print(f"\n   股票代码列表：{', '.join(actual_codes)}")
    
    if len(stocks) == 9:
        print(f"   ✅ 股票数量正确（9 只）")
    else:
        print(f"   ❌ 股票数量错误（应为 9 只）")
    
    # 验证股票名称
    print("\n   股票详情：")
    for code, stock in stocks.items():
        print(f"   - {code}: {stock.get('name')}")
        print(f"     概念：{stock.get('concepts', [])}")
        print(f"     文章数：{len(stock.get('articles', []))}")
    
    return True

def verify_002201():
    """验证 002201 修复"""
    print("\n" + "=" * 60)
    print("验证 002201 股票名称修复")
    print("=" * 60)
    
    stocks_dir = Path("data/master/stocks")
    
    for json_file in stocks_dir.glob("*.json"):
        if json_file.name == "stocks_index.json":
            continue
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            stocks = data.get('stocks', {})
            
            if '002201' in stocks:
                stock = stocks['002201']
                name = stock.get('name', '')
                concepts = stock.get('concepts', [])
                
                print(f"📄 {json_file.name}:")
                print(f"   代码：002201")
                print(f"   名称：{name}")
                print(f"   概念：{concepts}")
                
                if name == '正威新材':
                    print(f"   ✅ 名称正确")
                else:
                    print(f"   ❌ 名称错误（应为：正威新材）")
                
        except Exception as e:
            print(f"读取 {json_file} 失败：{e}")
    
    return True

def verify_index():
    """验证索引文件"""
    print("\n" + "=" * 60)
    print("验证 stocks_index.json")
    print("=" * 60)
    
    index_file = Path("data/master/stocks_index.json")
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    print(f"✅ 索引文件版本：{index_data.get('version')}")
    print(f"   最后更新：{index_data.get('last_updated')}")
    print(f"   总股票数：{index_data.get('total_stocks')}")
    
    # 检查是否包含 2026-04-21 的股票
    today_stocks = ['002475', '002138', '300433', '002600', '688322', '300602', '300136', '300115', '002440']
    found_count = 0
    
    for code in today_stocks:
        if code in index_data.get('stocks', {}):
            stock = index_data['stocks'][code]
            if stock.get('last_updated') == '2026-04-21':
                found_count += 1
    
    print(f"   ✅ 2026-04-21 新增股票：{found_count}/{len(today_stocks)}")
    
    return True

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 20 + "数据验证报告" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    verify_hot_topics()
    verify_2026_04_21()
    verify_002201()
    verify_index()
    
    print("\n")
    print("=" * 60)
    print("验证完成！")
    print("=" * 60)
