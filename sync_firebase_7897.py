#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path
import time

# 设置正确的代理端口 7897
PROXY_PORT = '7897'
os.environ['HTTP_PROXY'] = f'http://127.0.0.1:{PROXY_PORT}'
os.environ['HTTPS_PROXY'] = f'http://127.0.0.1:{PROXY_PORT}'

# 重定向输出到文件
log_file = Path('firebase_sync_log.txt')
log_file.write_text('')

def log(msg):
    print(msg)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    log(f"[1/5] Testing Firebase connection via proxy 127.0.0.1:{PROXY_PORT}...")
    
    cred_path = Path('.trae/skills/add-hot-topic/hottopic-7b5a7-firebase-adminsdk-fbsvc-017b2efebd.json')
    cred = credentials.Certificate(str(cred_path))
    app = firebase_admin.initialize_app(cred, {'projectId': 'hottopic-7b5a7'})
    
    log("[OK] Firebase initialized!")
    
    db = firestore.client(app)
    log("[OK] Firestore client created!")
    
    # 测试写入一只股票 (使用时间戳作为测试ID)
    log("[2/5] Testing write to Firestore...")
    test_id = f"TEST_{int(time.time())}"
    test_ref = db.collection('stocks').document(test_id)
    test_ref.set({'test': True, 'timestamp': firestore.SERVER_TIMESTAMP})
    log(f"[OK] Test write successful! (ID: {test_id})")
    
    # 读取数据
    log("[3/5] Reading stocks_master.json...")
    with open('data/master/stocks_master.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks_dict = data.get('stocks', {})
    target_date = '2026-05-09'
    
    stocks_to_sync = [
        (code, stock) for code, stock in stocks_dict.items()
        if isinstance(stock, dict) and stock.get('last_updated') == target_date
    ]
    
    log(f"[INFO] Found {len(stocks_to_sync)} stocks to sync")
    
    # 同步 - 使用 set() 而不是 update()
    log("[4/5] Syncing stocks...")
    success = 0
    failed = 0
    
    for i, (code, stock) in enumerate(stocks_to_sync, 1):
        try:
            doc_ref = db.collection('stocks').document(code)
            # 使用 set() with merge=True 来创建或更新文档
            doc_ref.set({
                'last_updated': target_date,
                'name': stock.get('name', ''),
                'code': code,
                'sync_time': firestore.SERVER_TIMESTAMP
            }, merge=True)
            success += 1
            log(f"  [{i}/{len(stocks_to_sync)}] OK: {code} {stock.get('name', '')}")
        except Exception as e:
            failed += 1
            log(f"  [{i}/{len(stocks_to_sync)}] FAIL: {code} - {e}")
    
    log(f"[5/5] Sync complete!")
    log(f"[SUMMARY] Success: {success}, Failed: {failed}")
    
    # 清理测试文档
    test_ref.delete()
    
    firebase_admin.delete_app(app)
    log("[DONE] Firebase sync finished!")
    
except Exception as e:
    log(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    with open(log_file, 'a', encoding='utf-8') as f:
        traceback.print_exc(file=f)
