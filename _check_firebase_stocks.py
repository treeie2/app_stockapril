#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 Firebase 上实际的股票数量"""
import os
os.environ["NO_PROXY"] = "*"

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from pathlib import Path
    
    key_files = [
        Path(__file__).parent / "api" / "firebase-credentials.json",
        Path(__file__).parent / ".trae" / "rules" / "firebase-credentials.json",
    ]
    
    key_file = None
    for f in key_files:
        if f.exists():
            key_file = str(f)
            print(f"🔑 使用密钥文件: {f.name}")
            break
    
    if not key_file:
        print("❌ 未找到 Firebase 密钥文件")
        exit(1)
    
    cred = credentials.Certificate(key_file)
    app = firebase_admin.initialize_app(cred, {'projectId': 'webstock-724'})
    db = firestore.client()
    
    print("\n📊 开始统计 Firebase stocks 集合...")
    
    # 统计所有文档
    stocks_ref = db.collection('stocks')
    docs = stocks_ref.get()
    total_count = len(docs)
    
    # 统计有 last_updated 的文档
    query_with_update = stocks_ref.where('last_updated', '!=', '')
    docs_with_update = query_with_update.get()
    with_update_count = len(docs_with_update)
    
    print(f"🔥 Firebase stocks 集合总计: {total_count} 只股票")
    print(f"📝 其中有 last_updated 的: {with_update_count} 只")
    
    # 查看前几个文档的结构
    print("\n📋 前 5 个文档示例:")
    for doc in docs[:5]:
        data = doc.to_dict()
        print(f"  {doc.id}: {data.get('name', '未知')}")
        if 'last_updated' in data:
            print(f"      last_updated: {data.get('last_updated')}")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()