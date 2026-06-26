"""Firebase 同步 - 单条写入全量"""
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
print(f"总个股: {total}")

synced = 0
errors = 0
start = time.time()
batch_size = 50

codes_list = list(stocks.keys())
for i in range(0, len(codes_list), batch_size):
    batch_codes = codes_list[i:i+batch_size]
    batch = db.batch()
    for code in batch_codes:
        stock = stocks[code]
        if not isinstance(stock, dict):
            continue
        data = {k: v for k, v in stock.items() if k != 'code'}
        data = {k: v for k, v in data.items() if not (isinstance(v, list) and len(v) == 0)}
        batch.set(db.collection('stocks').document(code), data)
    
    retries = 2
    while retries > 0:
        try:
            batch.commit()
            synced += len(batch_codes)
            break
        except Exception as e:
            retries -= 1
            err = str(e)[:60]
            if "Quota" in err or "RESOURCE" in err:
                print(f"\n  ⚠️ 配额限制，暂停 30s...")
                time.sleep(30)
            else:
                print(f"\n  ⚠️ {err}")
                time.sleep(5)
    
    if (i // batch_size) % 5 == 0:
        print(f"  进度: {synced}/{total}", end="\r")

elapsed = time.time() - start
print(f"\n同步完成! {synced}/{total}, 失败 {errors}, 耗时 {elapsed:.0f}秒")