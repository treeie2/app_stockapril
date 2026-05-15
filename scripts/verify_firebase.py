"""验证 Firebase 中泰和新材的数据是否包含 target_valuation"""
import json, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import firebase_admin
from firebase_admin import credentials, firestore

KEY_FILES = [
    Path(__file__).parent.parent / "api" / "firebase-credentials.json",
    Path(__file__).parent.parent / "serviceAccountKey.json",
]

key_file = None
for f in KEY_FILES:
    if f.exists():
        key_file = str(f)
        break

if not key_file:
    print("No key file found")
    exit(1)

cred = credentials.Certificate(key_file)
app = firebase_admin.initialize_app(cred, {'projectId': 'webstock-724'})
db = firestore.client(app=app)

# 查询泰和新材
doc = db.collection("stocks").document("002254").get()
if doc.exists:
    data = doc.to_dict()
    print(f"泰和新材 (002254):")
    print(f"  last_updated: {data.get('last_updated')}")
    articles = data.get('articles', [])
    print(f"  articles: {len(articles)}")
    for a in articles:
        tv = a.get('target_valuation', [])
        print(f"  - {a.get('title')}: tv={tv}")
else:
    print("Document not found")