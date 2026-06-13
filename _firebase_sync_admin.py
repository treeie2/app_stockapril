"""Firebase同步"""
import os
os.environ["NO_PROXY"] = "firestore.googleapis.com,googleapis.com,oauth2.googleapis.com"
os.environ["no_proxy"] = "firestore.googleapis.com,googleapis.com,oauth2.googleapis.com"

import json, time
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

total = len(stocks)
synced = 0
batch = db.batch()
op_count = 0
start = time.time()

for code, stock in stocks.items():
    data = {k: v for k, v in stock.items() if k != 'code'}
    data = {k: v for k, v in data.items() if not (isinstance(v, list) and len(v) == 0)}
    batch.set(db.collection('stocks').document(code), data)
    op_count += 1
    synced += 1
    if op_count >= 400:
        batch.commit()
        batch = db.batch()
        op_count = 0

if op_count > 0:
    batch.commit()

elapsed = time.time() - start
print(f'同步完成! {synced}/{total}, 耗时 {elapsed:.0f}秒')