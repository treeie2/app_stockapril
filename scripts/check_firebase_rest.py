"""通过 REST API 验证 Firebase 数据"""
import requests, json

url = "https://firestore.googleapis.com/v1/projects/webstock-724/databases/(default)/documents/stocks/002254"
resp = requests.get(url, timeout=10)
print(f'Status: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    fields = data.get('fields', {})
    articles = fields.get('articles', {}).get('arrayValue', {}).get('values', [])
    print(f'Articles: {len(articles)}')
    for a in articles:
        af = a.get('mapValue', {}).get('fields', {})
        title = af.get('title', {}).get('stringValue', '')
        tv = af.get('target_valuation', {}).get('arrayValue', {}).get('values', [])
        tv_text = [t.get('stringValue', '') for t in tv]
        print(f'  - {title}: tv={tv_text}')
else:
    print(f'Error: {resp.text[:500]}')