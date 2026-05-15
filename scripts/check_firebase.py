import requests, json

url = "https://firestore.googleapis.com/v1/projects/appstockapril/databases/(default)/documents/stocks/002254"
resp = requests.get(url, timeout=10)
if resp.status_code == 200:
    data = resp.json()
    fields = data.get('fields', {})
    articles = fields.get('articles', {}).get('arrayValue', {}).get('values', [])
    print(f'Firebase 中 002254 泰和新材: {len(articles)} 篇文章')
    for a in articles:
        af = a.get('mapValue', {}).get('fields', {})
        title = af.get('title', {}).get('stringValue', '')
        tv = af.get('target_valuation', {}).get('arrayValue', {}).get('values', [])
        tv_text = [t.get('stringValue', '') for t in tv]
        print(f'  - {title}: tv={tv_text}')
else:
    print(f'Firebase 查询失败: {resp.status_code}')
    print(resp.text[:500])