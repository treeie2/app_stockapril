"""将今天新增的个股同步到 Firebase (科远智慧 + 容大感光追加)"""
import json, requests, time
from pathlib import Path
from google.oauth2 import service_account
import google.auth.transport.requests

# 读取密钥
key_path = Path(r'.trae/skills/add-hot-topic/hottopic-7b5a7-firebase-adminsdk-fbsvc-017b2efebd.json')

# 用 google-auth 库生成 JWT
credentials = service_account.Credentials.from_service_account_file(
    str(key_path),
    scopes=['https://www.googleapis.com/auth/datastore']
)

auth_request = google.auth.transport.requests.Request()
credentials.refresh(auth_request)
token = credentials.token
print(f'✅ 获取 token (前20): {token[:20]}...')

# Firestore REST API 写入
project = 'webstock-724'
# 今天新增/更新的个股
codes = {
    '002380': '科远智慧',  # 新增
    '300576': '容大感光',  # 追加文章
}

master_path = Path(r'data/stocks/stocks_master.json')
with open(master_path, 'r', encoding='utf-8') as f:
    stocks = json.load(f)['stocks']

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
}

ok = 0
fail = 0
for code, name in codes.items():
    stock = stocks.get(code)
    if not stock:
        print(f'  ⚠️ {code} {name}: 主数据中不存在')
        continue
    
    fields = {}
    for k, v in stock.items():
        if isinstance(v, int):
            fields[k] = {'integerValue': str(v)}
        elif isinstance(v, list):
            if k == 'articles':
                avs = []
                for a in v:
                    af = {}
                    for ak, av in a.items():
                        if isinstance(av, list):
                            af[ak] = {'arrayValue': {'values': [{'stringValue': str(x)} for x in av]}}
                        else:
                            af[ak] = {'stringValue': str(av)}
                    avs.append({'mapValue': {'fields': af}})
                fields[k] = {'arrayValue': {'values': avs}}
            else:
                fields[k] = {'arrayValue': {'values': [{'stringValue': str(x)} for x in v]}}
        else:
            fields[k] = {'stringValue': str(v)}
    
    url = f'https://firestore.googleapis.com/v1/projects/{project}/databases/(default)/documents/stocks/{code}'
    r = requests.patch(url, headers=headers, json={'fields': fields}, timeout=30)
    if r.status_code in (200, 201):
        a = len(stock.get('articles', []))
        print(f'  ✅ {code} {name} | {a}篇/{stock.get("mention_count",0)}')
        ok += 1
    else:
        print(f'  ❌ {code} {name} | HTTP {r.status_code}: {r.text[:200]}')
        fail += 1

print(f'\n结果: {ok}成功, {fail}失败')