import requests, json

# 检查 GitHub raw 数据
url = "https://raw.githubusercontent.com/treeie2/app_stockapril/main/data/stocks/stocks_master.json"
resp = requests.get(url, timeout=30)
print(f'GitHub raw status: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    stocks = data.get('stocks', data)
    s = stocks.get('002254', {})
    print(f'002254 泰和新材:')
    print(f'  last_updated: {s.get("last_updated")}')
    articles = s.get('articles', [])
    print(f'  articles: {len(articles)}')
    for a in articles:
        tv = a.get('target_valuation', [])
        print(f'  - {a.get("title")}: tv={tv}')
else:
    print(f'Failed: {resp.text[:200]}')