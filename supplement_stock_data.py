"""
补充股票数据：获取缺失的行业、概念和板块信息
"""
import json
import akshare as ak
from pathlib import Path
from datetime import datetime
import time

def load_stocks_data():
    """加载现有股票数据"""
    master_file = Path('data/master/stocks_master.json')
    with open(master_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def save_stocks_data(data):
    """保存股票数据"""
    master_file = Path('data/master/stocks_master.json')
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 数据已保存到 {master_file}")

def get_stock_industry(code):
    """获取股票行业信息"""
    try:
        # 使用 akshare 获取行业信息
        df = ak.stock_individual_info_em(symbol=code)
        if df is not None and not df.empty:
            info = dict(zip(df['item'], df['value']))
            return {
                'industry': info.get('行业', ''),
                'name': info.get('股票简称', '')
            }
    except Exception as e:
        print(f"  ⚠️ 获取 {code} 行业信息失败: {e}")
    return None

def get_stock_concepts(code):
    """获取股票概念信息"""
    try:
        # 使用 akshare 获取概念板块
        df = ak.stock_board_concept_cons_em(symbol=code)
        if df is not None and not df.empty:
            concepts = df['板块名称'].tolist()
            return concepts[:10]  # 最多取10个概念
    except Exception as e:
        print(f"  ⚠️ 获取 {code} 概念信息失败: {e}")
    return []

def determine_board(code):
    """根据代码确定板块"""
    if code.startswith('6'):
        return 'SH'
    elif code.startswith('0') or code.startswith('3'):
        return 'SZ'
    elif code.startswith('8') or code.startswith('4'):
        return 'BJ'
    return 'SZ'

def supplement_stock_data():
    """补充股票数据"""
    print("📊 加载股票数据...")
    data = load_stocks_data()
    stocks = data.get('stocks', [])
    
    print(f"📈 共 {len(stocks)} 只股票\n")
    
    # 统计缺失
    missing_industry = []
    missing_concepts = []
    missing_board = []
    
    for stock in stocks:
        code = stock.get('code', '')
        if not stock.get('industry'):
            missing_industry.append(stock)
        if not stock.get('concepts'):
            missing_concepts.append(stock)
        if not stock.get('board'):
            missing_board.append(stock)
    
    print(f"📋 缺失数据统计:")
    print(f"  - 缺行业: {len(missing_industry)} 只")
    print(f"  - 缺概念: {len(missing_concepts)} 只")
    print(f"  - 缺板块: {len(missing_board)} 只\n")
    
    # 补充板块信息
    print("🔧 开始补充板块信息...")
    for stock in missing_board:
        code = stock.get('code', '')
        stock['board'] = determine_board(code)
    print(f"  ✅ 已补充 {len(missing_board)} 只股票的板块信息\n")
    
    # 补充行业信息
    print("🔧 开始补充行业信息...")
    success_count = 0
    for i, stock in enumerate(missing_industry):
        code = stock.get('code', '')
        name = stock.get('name', '')
        print(f"  [{i+1}/{len(missing_industry)}] {code} {name}")
        
        info = get_stock_industry(code)
        if info:
            if info.get('industry'):
                stock['industry'] = info['industry']
                success_count += 1
                print(f"    ✅ 行业: {info['industry']}")
            # 如果名称缺失也补充
            if not stock.get('name') and info.get('name'):
                stock['name'] = info['name']
        
        time.sleep(0.3)  # 避免请求过快
    
    print(f"  ✅ 成功补充 {success_count}/{len(missing_industry)} 只股票的行业信息\n")
    
    # 补充概念信息
    print("🔧 开始补充概念信息...")
    success_count = 0
    for i, stock in enumerate(missing_concepts):
        code = stock.get('code', '')
        name = stock.get('name', '')
        print(f"  [{i+1}/{len(missing_concepts)}] {code} {name}")
        
        concepts = get_stock_concepts(code)
        if concepts:
            stock['concepts'] = concepts
            success_count += 1
            print(f"    ✅ 概念: {', '.join(concepts[:5])}")
        
        time.sleep(0.3)  # 避免请求过快
    
    print(f"  ✅ 成功补充 {success_count}/{len(missing_concepts)} 只股票的概念信息\n")
    
    # 保存数据
    print("💾 保存数据...")
    save_stocks_data(data)
    
    # 再次统计
    print("\n📊 补充后数据统计:")
    missing_industry_after = sum(1 for s in stocks if not s.get('industry'))
    missing_concepts_after = sum(1 for s in stocks if not s.get('concepts'))
    missing_board_after = sum(1 for s in stocks if not s.get('board'))
    
    print(f"  - 缺行业: {missing_industry_after} 只 (减少 {len(missing_industry) - missing_industry_after})")
    print(f"  - 缺概念: {missing_concepts_after} 只 (减少 {len(missing_concepts) - missing_concepts_after})")
    print(f"  - 缺板块: {missing_board_after} 只 (减少 {len(missing_board) - missing_board_after})")
    
    print("\n🎉 数据补充完成！")

if __name__ == "__main__":
    supplement_stock_data()
