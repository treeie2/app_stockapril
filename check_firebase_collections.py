#!/usr/bin/env python3
"""
检查 Firebase 数据结构
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

# 检查集合
print("=== Firebase 集合检查 ===\n")

# 获取所有集合
collections = list(db.collections())
print(f"集合数量：{len(collections)}")
for col in collections:
    print(f"  - {col.id}")

# 检查 stocks 集合
print("\n=== stocks 集合 ===")
stocks_col = db.collection('stocks')
docs = stocks_col.limit(5).stream()
print("前 5 个文档:")
for doc in docs:
    data = doc.to_dict()
    print(f"  {doc.id}: {data.get('name', 'N/A')}")

# 检查 002046
print("\n=== 002046 详情 ===")
doc_ref = stocks_col.document('002046')
doc = doc_ref.get()
if doc.exists:
    data = doc.to_dict()
    print(f"Name: {data.get('name')}")
    print(f"Industry: {data.get('industry')}")
    print(f"Core Business: {data.get('core_business', [])}")
    print(f"Industry Position: {data.get('industry_position', [])}")
    print(f"Chain: {data.get('chain', [])}")
    print(f"Articles: {len(data.get('articles', []))}")
else:
    print("❌ 文档不存在")

# 检查是否有 stock_data 集合
print("\n=== 检查 stock_data 集合 ===")
stock_data_col = db.collection('stock_data')
docs = stock_data_col.limit(1).stream()
count = 0
for doc in docs:
    count += 1
if count == 0:
    print("stock_data 集合为空或不存在")
else:
    print(f"stock_data 集合有数据")
