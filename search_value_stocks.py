import json
import os

# 读取stocks_master.json
with open('data/stocks/stocks_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('数据结构:')
print(f'版本: {data.get("version")}')
print(f'更新日期: {data.get("updated_at")}')
print(f'股票数量: {len(data.get("stocks", {}))}')

# 搜索包含"深度价值展望"的股票
print('\n搜索包含"深度价值展望"的股票...')
found_stocks = []
for code, stock in data.get('stocks', {}).items():
    # 检查各个字段是否包含'深度价值展望'
    for key, value in stock.items():
        if isinstance(value, str) and '深度价值展望' in value:
            found_stocks.append((code, stock.get('name'), key))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str) and '深度价值展望' in item:
                    found_stocks.append((code, stock.get('name'), key))

print(f'\n找到 {len(found_stocks)} 只包含"深度价值展望"的股票:')
for code, name, field in found_stocks:
    print(f'  - {code}: {name} (字段: {field})')
