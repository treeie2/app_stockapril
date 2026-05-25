#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从Firebase重建完整的主数据文件"""

import json
import os
from pathlib import Path

# 禁用代理
os.environ['NO_PROXY'] = 'firestore.googleapis.com,googleapis.com,oauth2.googleapis.com'

import firebase_admin
from firebase_admin import credentials, firestore


def get_firebase_app():
    """获取或初始化Firebase App"""
    if firebase_admin._apps:
        return firebase_admin.get_app()
    
    key_files = [
        Path(__file__).parent / "api" / "firebase-credentials.json",
        Path(__file__).parent / ".trae" / "rules" / "firebase-credentials.json",
    ]
    
    key_file = None
    for f in key_files:
        if f.exists():
            key_file = str(f)
            print(f"[Firebase] Found key file: {key_file}")
            break
    
    if not key_file:
        print("[Firebase] No service account key file found")
        return None
    
    cred = credentials.Certificate(key_file)
    app = firebase_admin.initialize_app(cred, {'projectId': 'webstock-724'})
    print(f"[Firebase] Initialized: webstock-724")
    return app


def rebuild_master():
    """重建主数据文件"""
    app = get_firebase_app()
    if not app:
        return
    
    db = firestore.client()
    
    # 查询所有有last_updated字段的股票
    stocks_ref = db.collection('stocks')
    query = stocks_ref.where('last_updated', '!=', '')
    results = query.get()
    
    print(f"\n{'='*60}")
    print(f"从Firebase获取到 {len(results)} 只有研究更新的股票")
    print(f"{'='*60}\n")
    
    # 构建股票字典
    all_stocks = {}
    for doc in results:
        data = doc.to_dict()
        code = doc.id
        
        # 清理数据 - 移除Firebase特殊类型
        cleaned_data = {}
        for key, value in data.items():
            if value is None:
                continue
            if key == 'updated_at':
                continue
            cleaned_data[key] = value
        
        all_stocks[code] = cleaned_data
        print(f"  {code} - {cleaned_data.get('name', '')} ({cleaned_data.get('last_updated', '')})")
    
    # 创建完整的输出数据
    output_data = {
        "version": "2.3",
        "updated_at": "",
        "stocks": all_stocks
    }
    
    # 保存到主数据文件
    output_file = Path(__file__).parent / "data" / "stocks" / "stocks_master.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"重建完成!")
    print(f"  总股票数: {len(all_stocks)} 只")
    print(f"  文件已保存: {output_file}")
    print(f"{'='*60}")
    
    return all_stocks


if __name__ == "__main__":
    rebuild_master()
