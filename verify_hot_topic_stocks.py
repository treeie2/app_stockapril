#!/usr/bin/env python3
"""
验证 hot_topics.json 中的股票代码
"""
import json
from pathlib import Path

def verify_stocks():
    """验证股票代码和名称"""
    hot_topics_file = Path("data/hot_topics.json")
    
    with open(hot_topics_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 找到荣耀机器人 IPO
    for topic in data.get('topics', []):
        if topic.get('name') == '荣耀机器人 IPO':
            stocks = topic.get('stocks', [])
            print(f"热点：{topic['name']}")
            print(f"驱动因素：{topic['drivers']}")
            print(f"\n相关个股（{len(stocks)}只）：")
            print("-" * 60)
            
            # 读取索引文件获取名称
            index_file = Path("data/master/stocks_index.json")
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            index_stocks = index_data.get('stocks', {})
            
            for code in stocks:
                if code in index_stocks:
                    name = index_stocks[code].get('name', '未知')
                    print(f"  {code} - {name}")
                else:
                    print(f"  {code} - ❌ 数据库中不存在")
            
            return True
    
    return False

if __name__ == "__main__":
    verify_stocks()
