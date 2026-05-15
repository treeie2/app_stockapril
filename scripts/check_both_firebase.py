"""检查 appstockapril Firebase 项目中的泰和新材数据"""
import requests, json

# 尝试 appstockapril 项目
url = "https://firestore.googleapis.com/v1/projects/appstockapril/databases/(default)/documents/stocks/002254"
resp = requests.get(url, timeout=10)
print(f'appstockapril Status: {resp.status_code}')
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

print()

# 也检查 webstock-724 项目
url2 = "https://firestore.googleapis.com/v1/projects/webstock-724/databases/(default)/documents/stocks/002254"
resp2 = requests.get(url2, timeout=10)
print(f'webstock-724 Status: {resp2.status_code}')
if resp2.status_code == 200:
    data2 = resp2.json()
    fields2 = data2.get('fields', {})
    articles2 = fields2.get('articles', {}).get('arrayValue', {}).get('values', [])
    print(f'Articles: {len(articles2)}')
    for a in articles2:
        af = a.get('mapValue', {}).get('fields', {})
        title = af.get('title', {}).get('stringValue', '')
        tv = af.get('target_valuation', {}).get('arrayValue', {}).get('values', [])
        tv_text = [t.get('stringValue', '') for t in tv]
        print(f'  - {title}: tv={tv_text}')
else:
    print(f'Error: {resp2.text[:500]}')