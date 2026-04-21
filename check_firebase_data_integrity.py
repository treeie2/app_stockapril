#!/usr/bin/env python3
"""
检查 Firebase 数据完整性
"""
import os
from pathlib import Path

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(Path('e:/github/stock-research-backup/.trae/rules/firebase-credentials.json'))

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
try:
    firebase_admin.initialize_app(cred)
except ValueError:
    app = firebase_admin.get_app()

db = firestore.client()

print("📊 检查 Firebase 数据完整性...\n")

stocks_col = db.collection('stocks')
docs = stocks_col.stream()

total = 0
with_articles = 0
without_articles = 0
with_core_business = 0

for doc in docs:
    data = doc.to_dict()
    total += 1
    
    articles = data.get('articles', [])
    if articles and len(articles) > 0:
        with_articles += 1
    else:
        without_articles += 1
    
    core_business = data.get('core_business', [])
    if core_business and len(core_business) > 0:
        with_core_business += 1
    
    if total % 500 == 0:
        print(f"已检查 {total} 只股票...")

print(f"\n📊 统计结果:")
print(f"  总股票数：{total}")
print(f"  有文章数据：{with_articles} ({with_articles/total*100:.1f}%)")
print(f"  无文章数据：{without_articles} ({without_articles/total*100:.1f}%)")
print(f"  有核心业务：{with_core_business} ({with_core_business/total*100:.1f}%)")
