"""
从行业映射文件补充股票数据
"""
import json
from pathlib import Path

def load_json_file(filename):
    """加载JSON文件"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def supplement_from_mappings():
    """从映射文件补充数据"""
    print("📊 加载股票数据...")
    master_file = Path('data/master/stocks_master.json')
    with open(master_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', [])
    stocks_dict = {s['code']: s for s in stocks}
    
    print(f"📈 共 {len(stocks)} 只股票\n")
    
    # 加载映射文件
    print("📂 加载映射文件...")
    
    # 尝试加载各种映射文件
    industry_map = load_json_file('data/master/industry_map.json')
    ths_map = load_json_file('data/master/ths_industry_map.json')
    things_map = load_json_file('data/master/thingsindustry_map.json')
    
    print(f"  - 行业映射: {len(industry_map)} 条")
    print(f"  - 同花顺映射: {len(ths_map)} 条")
    print(f"  - Things映射: {len(things_map)} 条\n")
    
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
    
    # 补充板块信息（根据代码规则）
    print("🔧 补充板块信息...")
    for stock in missing_board:
        code = stock.get('code', '')
        if code.startswith('6'):
            stock['board'] = 'SH'
        elif code.startswith('0') or code.startswith('3'):
            stock['board'] = 'SZ'
        elif code.startswith('8') or code.startswith('4'):
            stock['board'] = 'BJ'
        else:
            stock['board'] = 'SZ'
    print(f"  ✅ 已补充 {len(missing_board)} 只股票的板块信息\n")
    
    # 从映射文件补充行业
    print("🔧 从映射文件补充行业...")
    industry_supplemented = 0
    
    for stock in missing_industry:
        code = stock.get('code', '')
        
        # 尝试从不同映射获取行业
        industry = None
        
        if code in industry_map:
            industry = industry_map[code]
        elif code in ths_map:
            industry = ths_map[code]
        elif code in things_map:
            industry = things_map[code]
        
        if industry:
            stock['industry'] = industry
            industry_supplemented += 1
    
    print(f"  ✅ 从映射补充 {industry_supplemented}/{len(missing_industry)} 只股票的行业\n")
    
    # 为缺失概念的股票添加默认概念
    print("🔧 补充概念信息...")
    concepts_supplemented = 0
    
    for stock in missing_concepts:
        code = stock.get('code', '')
        industry = stock.get('industry', '')
        
        # 根据行业生成概念
        concepts = []
        if industry:
            # 从行业提取概念
            if ' - ' in industry:
                parts = industry.split(' - ')
                concepts = [p.strip() for p in parts if p.strip()]
            else:
                concepts = [industry]
        
        # 根据代码添加市场概念
        if code.startswith('60'):
            concepts.append('上证主板')
        elif code.startswith('00'):
            concepts.append('深证主板')
        elif code.startswith('30'):
            concepts.append('创业板')
        elif code.startswith('68'):
            concepts.append('科创板')
        elif code.startswith('8') or code.startswith('4'):
            concepts.append('北交所')
        
        if concepts:
            stock['concepts'] = concepts[:5]  # 最多5个
            concepts_supplemented += 1
    
    print(f"  ✅ 已补充 {concepts_supplemented}/{len(missing_concepts)} 只股票的概念\n")
    
    # 保存数据
    print("💾 保存数据...")
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 数据已保存\n")
    
    # 再次统计
    print("📊 补充后数据统计:")
    missing_industry_after = sum(1 for s in stocks if not s.get('industry'))
    missing_concepts_after = sum(1 for s in stocks if not s.get('concepts'))
    missing_board_after = sum(1 for s in stocks if not s.get('board'))
    
    print(f"  - 缺行业: {missing_industry_after} 只 (减少 {len(missing_industry) - missing_industry_after})")
    print(f"  - 缺概念: {missing_concepts_after} 只 (减少 {len(missing_concepts) - missing_concepts_after})")
    print(f"  - 缺板块: {missing_board_after} 只 (减少 {len(missing_board) - missing_board_after})")
    
    # 显示仍缺失的股票
    if missing_industry_after > 0:
        print(f"\n⚠️  仍缺失行业的股票(前10只):")
        for stock in [s for s in stocks if not s.get('industry')][:10]:
            print(f"    - {stock.get('code')} {stock.get('name', 'N/A')}")
    
    print("\n🎉 数据补充完成！")

if __name__ == "__main__":
    supplement_from_mappings()
