#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从Firebase同步有研究更新的股票到本地主数据文件"""

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


def clean_stock_data(stock_data):
    """清理股票数据，处理Firebase特殊类型"""
    cleaned = {}
    for key, value in stock_data.items():
        if value is None:
            continue
        # 移除updated_at字段（Firebase时间戳）
        if key == 'updated_at':
            continue
        cleaned[key] = value
    return cleaned


def sync_from_firebase():
    """从Firebase同步有研究更新的股票"""
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
    firebase_stocks = {}
    for doc in results:
        data = doc.to_dict()
        code = doc.id
        # 清理数据
        cleaned_data = clean_stock_data(data)
        firebase_stocks[code] = cleaned_data
        print(f"  {code} - {cleaned_data.get('name', '')} ({cleaned_data.get('last_updated', '')})")
    
    # 读取本地主数据文件
    local_file = Path(__file__).parent / "data" / "stocks" / "stocks_master.json"
    if local_file.exists():
        with open(local_file, 'r', encoding='utf-8') as f:
            local_data = json.load(f)
        local_stocks = local_data.get('stocks', {})
        print(f"\n本地文件已有 {len(local_stocks)} 只股票")
    else:
        local_stocks = {}
        print("\n本地文件不存在，将创建新文件")
    
    # 合并数据：以Firebase数据为准
    merged_stocks = {**local_stocks}
    new_count = 0
    updated_count = 0
    
    for code, stock_data in firebase_stocks.items():
        if code not in local_stocks:
            merged_stocks[code] = stock_data
            new_count += 1
        else:
            # 检查是否需要更新
            local_update = local_stocks[code].get('last_updated', '')
            firebase_update = stock_data.get('last_updated', '')
            if firebase_update > local_update:
                merged_stocks[code] = stock_data
                updated_count += 1
    
    # 保存合并后的文件
    output_data = {
        "version": "2.3",
        "updated_at": "",
        "stocks": merged_stocks
    }
    
    with open(local_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"合并完成!")
    print(f"  新增股票: {new_count} 只")
    print(f"  更新股票: {updated_count} 只")
    print(f"  总计股票: {len(merged_stocks)} 只")
    print(f"{'='*60}")
    
    return merged_stocks


if __name__ == "__main__":
    sync_from_firebase()
