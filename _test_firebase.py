"""快速测试 Firebase 配额"""
import os
os.environ["NO_PROXY"] = "firestore.googleapis.com,googleapis.com,oauth2.googleapis.com"
os.environ["no_proxy"] = "firestore.googleapis.com,googleapis.com,oauth2.googleapis.com"

import json
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

key_path = Path('.trae/rules/firebase-credentials.json')
cred = credentials.Certificate(str(key_path))
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {'projectId': 'webstock-724'})
db = firestore.client()

with open('data/stocks/stocks_master.json', encoding='utf-8') as f:
    stocks = json.load(f)['stocks']

synced = 0
for i, (code, stock) in enumerate(stocks.items()):
    if not isinstance(stock, dict) or not stock.get('articles'):
        continue
    data = {k: v for k, v in stock.items() if k != 'code'}
    data = {k: v for k, v in data.items() if not (isinstance(v, list) and len(v) == 0)}
    try:
        db.collection('stocks').document(code).set(data)
        synced += 1
        name = stock.get('name', '')
        print(f"OK [{code}] {name}")
    except Exception as e:
        print(f"ERR [{code}] {str(e)[:80]}")
        break
    if synced >= 5:
        break

print(f"结果: 成功 {synced} 条")