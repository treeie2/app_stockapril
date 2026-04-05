import json
import os
import sqlite3

master_file = 'data/master/stocks_master.json'

if os.path.exists(master_file):
    with open(master_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict):
        stocks = data.get('stocks', [])
    elif isinstance(data, list):
        stocks = data
    else:
        stocks = []
    
    print(f'stocks_master.json 存在')
    print(f'股票数量: {len(stocks)}')
    
    # 检查是否有 description、insights、accidents
    with_desc = sum(1 for s in stocks if s.get('description'))
    with_insights = sum(1 for s in stocks if s.get('insights'))
    with_accidents = sum(1 for s in stocks if s.get('accidents'))
    
    print(f'有 description: {with_desc}')
    print(f'有 insights: {with_insights}')
    print(f'有 accidents: {with_accidents}')
    
    # 显示前3个股票
    print('\n前3个股票示例:')
    for s in stocks[:3]:
        code = s.get('code', 'N/A')
        name = s.get('name', 'N/A')
        has_desc = '有' if s.get('description') else '无'
        insights_count = len(s.get('insights', []))
        print(f'  {code} {name}: desc={has_desc}, insights={insights_count}条')
else:
    print(f'stocks_master.json 不存在: {master_file}')

print('\n' + '='*50)
print('SQLite 数据库状态:')

conn = sqlite3.connect('data/stock_research.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM stocks WHERE description IS NOT NULL AND description != ''")
count = cursor.fetchone()[0]
print(f'SQLite 中有 description 的股票: {count}')

cursor.execute("SELECT code, name, description FROM stocks WHERE description IS NOT NULL AND description != '' LIMIT 5")
print('\n前5个有 description 的股票:')
for row in cursor.fetchall():
    desc = row[2][:50] + '...' if row[2] and len(row[2]) > 50 else row[2]
    print(f'  {row[0]} {row[1]}: {desc}')

conn.close()
