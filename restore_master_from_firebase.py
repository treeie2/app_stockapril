#!/usr/bin/env python3
"""
从 Firebase 恢复完整的 stocks_master.json
"""
import os
import json
from pathlib import Path
from datetime import datetime
import time

# 设置 Firebase 凭证
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(Path('e:/github/stock-research-backup/.trae/rules/firebase-credentials.json'))

import firebase_admin
from firebase_admin import credentials, firestore

# 初始化 Firebase
cred = credentials.Certificate(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
try:
    firebase_admin.initialize_app(cred)
    print("✅ Firebase 初始化成功")
except ValueError:
    print("ℹ️ Firebase 已初始化，使用现有实例")
    app = firebase_admin.get_app()

db = firestore.client()

def restore_from_firebase():
    """从 Firebase 恢复完整的 stocks_master.json"""
    print("📥 正在从 Firebase 下载完整的股票数据...")
    
    # 获取所有股票
    stocks_col = db.collection('stocks')
    docs = stocks_col.stream()
    
    stocks_master = {}
    count = 0
    
    for doc in docs:
        data = doc.to_dict()
        code = data.get('code', doc.id)
        
        if code:
            # 转换为 stocks_master.json 的格式
            stocks_master[code] = {
                'name': data.get('name', ''),
                'code': code,
                'board': data.get('board', ''),
                'industry': data.get('industry', ''),
                'concepts': data.get('concepts', []),
                'products': data.get('products', []),
                'core_business': data.get('core_business', []),
                'industry_position': data.get('industry_position', []),
                'chain': data.get('chain', []),
                'partners': data.get('partners', []),
                'mention_count': data.get('mention_count', 0),
                'articles': data.get('articles', []),
                'last_updated': data.get('last_updated', '')
            }
            count += 1
            
            if count % 500 == 0:
                print(f"  已下载 {count} 只股票...")
    
    print(f"\n✅ 下载完成！共 {count} 只股票")
    
    # 保存到文件
    output_file = Path('data/master/stocks_master.json')
    print(f"💾 保存到 {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stocks_master, f, ensure_ascii=False, indent=2)
    
    file_size = output_file.stat().st_size / 1024 / 1024
    print(f"✅ 保存成功！文件大小：{file_size:.2f} MB")
    
    # 验证 002046
    if '002046' in stocks_master:
        stock = stocks_master['002046']
        print(f"\n✅ 验证 002046:")
        print(f"  Name: {stock.get('name')}")
        print(f"  Industry: {stock.get('industry')}")
        print(f"  Core Business: {stock.get('core_business', [])}")
        print(f"  Last Updated: {stock.get('last_updated')}")

if __name__ == '__main__':
    restore_from_firebase()
