#!/usr/bin/env python3
"""
验证 Firebase 中的 002046 数据
"""
import os
from pathlib import Path

# 设置 Firebase 凭证
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(Path('e:/github/stock-research-backup/.trae/rules/firebase-credentials.json'))

import firebase_admin
from firebase_admin import credentials, firestore

# 初始化 Firebase
cred = credentials.Certificate(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
try:
    firebase_admin.initialize_app(cred)
except ValueError:
    app = firebase_admin.get_app()

db = firestore.client()

# 获取 002046 的数据
doc_ref = db.collection('stocks').document('002046')
doc = doc_ref.get()

if doc.exists:
    data = doc.to_dict()
    print("=== Firebase 中的 002046 数据 ===\n")
    print(f"Name: {data.get('name')}")
    print(f"Code: {data.get('code')}")
    print(f"Industry: {data.get('industry')}")
    print(f"Core Business: {data.get('core_business', [])}")
    print(f"Industry Position: {data.get('industry_position', [])}")
    print(f"Chain: {data.get('chain', [])}")
    print(f"Concepts: {data.get('concepts', [])}")
    print(f"\nArticles ({len(data.get('articles', []))}):")
    for i, article in enumerate(data.get('articles', []), 1):
        print(f"  {i}. Title: '{article.get('title', 'EMPTY')}'")
        print(f"     Date: {article.get('date')}")
        print(f"     Source: '{article.get('source', 'EMPTY')}'")
        print(f"     Target Valuation: {article.get('target_valuation', [])}")
    print(f"\nLast Updated: {data.get('last_updated')}")
    print(f"Synced At: {data.get('synced_at')}")
else:
    print("❌ 文档不存在")
