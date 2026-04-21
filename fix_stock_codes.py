#!/usr/bin/env python3
"""
检查并修复股票代码和名称不匹配的问题
"""
import json
from pathlib import Path

# 需要检查的股票代码（来自截图）
STOCKS_TO_CHECK = {
    "001379": "商业航天",
    "002201": "商业航天",  # 实际应为正威新材
    "002287": "商业航天",
    "002361": "神剑股份",
    "002691": "商业航天铲子股",
    "002935": "商业航天",
    "159241": "航空航天 ETF",  # ETF
    "300099": "国防军工",  # 指数
}

# 正确的股票名称映射
CORRECT_NAMES = {
    "002201": "正威新材",  # 实际股票名称
    "002361": "神剑股份",
    "002691": "冀凯股份",
    "002935": "天奥电子",
}

def check_stock_data():
    """检查股票数据文件中的代码和名称匹配情况"""
    stocks_dir = Path("data/master/stocks")
    
    print("🔍 检查股票代码和名称匹配情况...\n")
    
    issues = []
    
    # 遍历所有数据文件
    for json_file in stocks_dir.glob("*.json"):
        if json_file.name == "stocks_index.json":
            continue
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            stocks = data.get('stocks', {})
            
            for code, stock in stocks.items():
                if code in STOCKS_TO_CHECK:
                    stock_name = stock.get('name', '')
                    expected = STOCKS_TO_CHECK[code]
                    
                    # 检查名称是否正确
                    if code in CORRECT_NAMES:
                        correct_name = CORRECT_NAMES[code]
                        if stock_name != correct_name:
                            issues.append({
                                'file': str(json_file),
                                'code': code,
                                'current_name': stock_name,
                                'correct_name': correct_name,
                                'expected_concept': expected
                            })
                            print(f"❌ {json_file.name}: {code}")
                            print(f"   当前名称：{stock_name}")
                            print(f"   正确名称：{correct_name}")
                            print(f"   概念：{stock.get('concepts', [])}\n")
                    else:
                        print(f"⚠️  {json_file.name}: {code} - {stock_name} (概念：{expected})")
                        
        except Exception as e:
            print(f"读取 {json_file} 失败：{e}")
    
    return issues

def fix_hot_topics():
    """修复 hot_topics.json 中的格式问题"""
    hot_topics_file = Path("data/hot_topics.json")
    
    if not hot_topics_file.exists():
        print("❌ hot_topics.json 不存在")
        return False
    
    with open(hot_topics_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    fixed = False
    for topic in data.get('topics', []):
        if topic.get('name') == '荣耀机器人 IPO':
            stocks = topic.get('stocks', [])
            # 检查是否是逗号分隔的字符串
            if len(stocks) == 1 and ',' in stocks[0]:
                # 分割成数组
                stock_list = [s.strip() for s in stocks[0].replace('，', ',').split(',')]
                topic['stocks'] = stock_list
                print(f"✅ 修复荣耀机器人 IPO 影子股格式：{stock_list}")
                fixed = True
    
    if fixed:
        with open(hot_topics_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("✅ hot_topics.json 已更新")
    
    return fixed

if __name__ == "__main__":
    print("=" * 60)
    print("检查股票代码和名称匹配问题")
    print("=" * 60)
    
    # 检查股票数据
    issues = check_stock_data()
    
    print("\n" + "=" * 60)
    print("修复 hot_topics.json 格式问题")
    print("=" * 60)
    
    # 修复热点数据
    fix_hot_topics()
    
    print("\n" + "=" * 60)
    print(f"检查完成！发现 {len(issues)} 个问题")
    print("=" * 60)
