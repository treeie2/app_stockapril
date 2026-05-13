import json

# 验证中国长城数据
with open('data/stocks/stocks_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

stock = data['stocks']['000066']
print('中国长城 (000066) 最新数据:')
print(f'  提及次数：{stock["mention_count"]}')
print(f'  文章数量：{len(stock["articles"])}')
print(f'  行业：{stock["industry"]}')
print(f'  概念数量：{len(stock["concepts"])}')
print(f'  最后更新：{stock["last_updated"]}')

print('\n最新文章:')
article = stock['articles'][-1]
print(f'  标题：{article["title"]}')
print(f'  日期：{article["date"]}')
print(f'  催化剂：{len(article["accidents"])} 条')
print(f'  观点：{len(article["insights"])} 条')
print(f'  指标：{len(article["key_metrics"])} 条')
print(f'  估值：{len(article["target_valuation"])} 条')

# 显示部分数据
print('\n催化剂示例:')
for acc in article['accidents'][:2]:
    print(f'  - {acc}')

print('\n观点示例:')
for ins in article['insights'][:2]:
    print(f'  - {ins}')

print('\n关键指标示例:')
for metric in article['key_metrics'][:2]:
    print(f'  - {metric}')

print('\n目标估值示例:')
for val in article['target_valuation'][:2]:
    print(f'  - {val}')
