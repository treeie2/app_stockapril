#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 Firebase 获取全部个股数据并保存到本地"""
import json
import os
from pathlib import Path

# 禁用代理
os.environ["NO_PROXY"] = "*"
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    def init_firebase():
        if firebase_admin._apps:
            return firebase_admin.get_app()
        
        key_files = [
            Path(__file__).parent / "api" / "firebase-credentials.json",
            Path(__file__).parent / ".trae" / "rules" / "firebase-credentials.json",
            Path(__file__).parent / "serviceAccountKey.json",
        ]
        
        key_file = None
        for f in key_files:
            if f.exists():
                key_file = str(f)
                print(f"🔑 使用密钥文件: {f}")
                break
        
        if not key_file:
            print("❌ 未找到 Firebase 密钥文件")
            return None
        
        cred = credentials.Certificate(key_file)
        return firebase_admin.initialize_app(cred, {'projectId': 'webstock-724'})
    
    app = init_firebase()
    if not app:
        exit(1)
    
    db = firestore.client()
    print("\n📊 开始从 Firebase 获取全部个股数据...")
    
    # 获取所有股票
    stocks_ref = db.collection('stocks')
    docs = stocks_ref.get()
    
    all_stocks = {}
    has_update_count = 0
    no_update_count = 0
    
    for doc in docs:
        data = doc.to_dict()
        code = doc.id
        
        # 清理数据，移除 Firestore 特殊字段
        cleaned = {}
        for k, v in data.items():
            if v is None:
                continue
            if k == 'updated_at':  # 移除服务器时间戳
                continue
            cleaned[k] = v
        
        all_stocks[code] = cleaned
        
        if cleaned.get('last_updated'):
            has_update_count += 1
        else:
            no_update_count += 1
    
    # 保存到本地文件
    output_file = Path(__file__).parent / "data" / "stocks" / "stocks_from_firebase.json"
    output_data = {
        "version": "2.4",
        "updated_at": "2026-05-20",
        "total_stocks": len(all_stocks),
        "stocks": all_stocks
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 同步完成！")
    print(f"📦 总股票数: {len(all_stocks)}")
    print(f"📝 有 last_updated (研究数据): {has_update_count}")
    print(f"📋 仅基本信息: {no_update_count}")
    print(f"💾 保存到: {output_file}")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()