#!/usr/bin/env python3
"""
快速同步今日更新的 22 只股票到 Firebase
"""
import json
import os
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

# 今日更新的股票代码
TODAY_STOCKS = [
    '002046', '603019', '000977', '603118',
    '000960', '600961', '600531', '002428', '002975', '600206', '600703',
    '688498', '600105', '688048', '002023', '688313', '002281', '000988',
    '002725', '300316', '002371', '603005'
]

MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")

def sync_today_stocks():
    """同步今日更新的股票到 Firebase"""
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        stocks_master = json.load(f)
    
    print(f"📊 今日更新的股票数：{len(TODAY_STOCKS)}")
    
    success_count = 0
    fail_count = 0
    
    for i, code in enumerate(TODAY_STOCKS, 1):
        if code not in stocks_master:
            print(f"❌ [{i}] 股票不存在：{code}")
            fail_count += 1
            continue
        
        stock_data = stocks_master[code]
        
        try:
            # 准备同步的数据
            doc_data = {
                'name': stock_data.get('name', ''),
                'code': code,
                'board': stock_data.get('board', ''),
                'industry': stock_data.get('industry', ''),
                'concepts': stock_data.get('concepts', []),
                'products': stock_data.get('products', []),
                'core_business': stock_data.get('core_business', []),
                'industry_position': stock_data.get('industry_position', []),
                'chain': stock_data.get('chain', []),
                'partners': stock_data.get('partners', []),
                'mention_count': stock_data.get('mention_count', 0),
                'articles': stock_data.get('articles', []),
                'last_updated': stock_data.get('last_updated', ''),
                'synced_at': datetime.now().isoformat()
            }
            
            # 同步到 Firebase
            doc_ref = db.collection('stocks').document(code)
            doc_ref.set(doc_data)
            
            print(f"✅ [{i}] 同步成功：{code} {stock_data.get('name', '')}")
            success_count += 1
            
            # 避免频率限制
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ [{i}] 同步失败：{code} {stock_data.get('name', '')} - {str(e)}")
            fail_count += 1
    
    print(f"\n✅ 同步完成！成功：{success_count}, 失败：{fail_count}")

if __name__ == '__main__':
    sync_today_stocks()
