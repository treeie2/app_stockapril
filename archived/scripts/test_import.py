import requests

url = 'https://mp.weixin.qq.com/s/LYz3-fNpKaO_oQsR3ao66Q'
print('Testing import...')

r = requests.post('http://localhost:5000/api/article/import', 
                  json={'url': url}, 
                  timeout=60)

d = r.json()
print('成功:', d['success'])
print('文章标题:', d.get('article_title', 'N/A'))
print('找到的股票名称总数:', d.get('total_found', 0))
print('匹配的股票数:', d.get('total_matched', 0))
print('股票列表:')
for s in d.get('stocks', []):
    print(f"  - {s['name']} ({s['code']})")

print('\n未匹配的名称:')
unmatched = d.get('unmatched_names', [])
for name in unmatched[:30]:
    print(f"  - {name}")

# 检查德科立是否在未匹配列表中
if '德科立' in unmatched:
    print('\n德科立在未匹配列表中!')
else:
    print('\n德科立不在未匹配列表中')
    # 查找包含德科的
    for name in unmatched:
        if '德' in name or '科' in name:
            print(f'  相关: {name}')
