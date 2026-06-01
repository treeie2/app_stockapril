#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从Firebase同步完整研究数据到本地"""

import json
import os
from pathlib import Path

# 设置代理环境变量
os.environ['NO_PROXY'] = '*'
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    def init_firebase():
        if firebase_admin._apps:
            return firebase_admin.get_app()
        
        key_file = Path(__file__).parent / "api" / "firebase-credentials.json"
        if not key_file.exists():
            key_file = Path(__file__).parent / ".trae" / "rules" / "firebase-credentials.json"
        
        if not key_file.exists():
            print("[ERROR] Firebase credentials not found")
            return None
        
        cred = credentials.Certificate(str(key_file))
        return firebase_admin.initialize_app(cred, {'projectId': 'webstock-724'})
    
    app = init_firebase()
    if app:
        db = firestore.client()
        print("[Firebase] 已连接")
        
        # 获取所有有研究更新的股票
        stocks_ref = db.collection('stocks')
        query = stocks_ref.where('last_updated', '!=', '')
        results = query.get()
        
        print(f"\n[Firebase] 获取到 {len(results)} 只有研究更新的股票")
        
        all_stocks = {}
        for doc in results:
            data = doc.to_dict()
            code = doc.id
            
            cleaned = {}
            for k, v in data.items():
                if v is None:
                    continue
                if k == 'updated_at':
                    continue
                cleaned[k] = v
            
            all_stocks[code] = cleaned
        
        # 保存到本地
        output = {
            "version": "2.3",
            "updated_at": "",
            "stocks": all_stocks
        }
        
        output_file = Path(__file__).parent / "data" / "stocks" / "stocks_master.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n[SUCCESS] 同步完成!")
        print(f"  股票总数: {len(all_stocks)}")
        print(f"  文件: {output_file}")
        
    else:
        print("[ERROR] 无法连接Firebase")
        
except Exception as e:
    print(f"[ERROR] {str(e)}")
