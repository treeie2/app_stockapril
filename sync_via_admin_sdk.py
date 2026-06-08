"""尝试用 Firebase Admin SDK 直接同步"""
import os
os.environ["NO_PROXY"] = "firestore.googleapis.com,googleapis.com,oauth2.googleapis.com"
os.environ["no_proxy"] = "firestore.googleapis.com,googleapis.com,oauth2.googleapis.com"

import json, sys
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

key_path = Path(r'api/firebase-credentials.json')
if not key_path.exists():
    key_path = Path(r'serviceAccountKey.json')
if not key_path.exists():
    key_path = Path(r'firebase_key.json')
if not key_path.exists():
    key_path = Path(r'.trae/skills/add-hot-topic/hottopic-7b5a7-firebase-adminsdk-fbsvc-017b2efebd.json')

print(f'使用密钥: {key_path}')
if not key_path.exists():
    print('密钥文件不存在!')
    sys.exit(1)

cred = credentials.Certificate(str(key_path))
if firebase_admin._apps:
    app = firebase_admin.get_app()
else:
    app = firebase_admin.initialize_app(cred, {'projectId': 'webstock-724'})

db = firestore.client(app=app)
print('Firestore 连接成功')

# 读取数据
with open(r'data/stocks/stocks_master.json', encoding='utf-8') as f:
    stocks = json.load(f)['stocks']

# 只同步新增/更新的
codes = {'002380': '科远智慧', '300576': '容大感光'}
batch = db.batch()

for code, name in codes.items():
    stock = stocks.get(code)
    if not stock:
        print(f'  ⚠️ {code} {name}: 不存在')
        continue
    
    doc_ref = db.collection('stocks').document(code)
    data = {k: v for k, v in stock.items()}
    # 移除 code 字段避免重复
    data.pop('code', None)
    batch.set(doc_ref, data, merge=True)

batch.commit()

# 验证
for code, name in codes.items():
    doc = db.collection('stocks').document(code).get()
    if doc.exists:
        d = doc.to_dict()
        a = len(d.get('articles', []))
        print(f'  ✅ {code} {name} | {a}篇 Firebase 写入成功')
    else:
        print(f'  ❌ {code} {name}: 写入后未找到')

print('\n完成!')