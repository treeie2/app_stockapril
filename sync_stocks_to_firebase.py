#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""同步更新了 last_updated 的股票数据到 Firebase"""

import json
import sys
import io
from pathlib import Path
import os

# UTF-8 输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 禁用代理
os.environ["NO_PROXY"] = "firestore.googleapis.com,googleapis.com,oauth2.googleapis.com"
os.environ["no_proxy"] = "firestore.googleapis.com,googleapis.com,oauth2.googleapis.com"

FIREBASE_PROJECT_ID = "webstock-724"
KEY_FILES = [
    Path(__file__).parent / "api" / "firebase-credentials.json",
    Path(__file__).parent / "serviceAccountKey.json",
    Path(__file__).parent / "firebase_key.json",
    Path(__file__).parent / ".trae" / "rules" / "firebase-credentials.json",
    Path(__file__).parent / ".trae" / "skills" / "add-hot-topic" / f"hottopic-7b5a7-firebase-adminsdk-fbsvc-017b2efebd.json",
]


def get_firebase_app():
    """获取或初始化 Firebase App"""
    import firebase_admin
    from firebase_admin import credentials

    if firebase_admin._apps:
        return firebase_admin.get_app()

    key_file = None
    for f in KEY_FILES:
        if f.exists():
            key_file = str(f)
            print(f"[Firebase] Found key file: {key_file}")
            break

    if not key_file:
        print("[Firebase] No service account key file found")
        return None

    try:
        cred = credentials.Certificate(key_file)
        app = firebase_admin.initialize_app(cred, {'projectId': FIREBASE_PROJECT_ID})
        print(f"[Firebase] Initialized: {FIREBASE_PROJECT_ID}")
        return app
    except Exception as e:
        print(f"[Firebase] Init failed: {e}")
        return None


def sync_stocks_to_firebase():
    """同步 stocks_master.json 中所有股票到 Firebase"""
    app = get_firebase_app()
    if not app:
        print("[Firebase] Cannot connect to Firebase")
        return

    from firebase_admin import firestore
    from google.api_core import retry as google_retry

    # 读取 stocks_master.json
    data_file = Path(__file__).parent / "data" / "stocks" / "stocks_master.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stocks_dict = data.get('stocks', {})

    # 只同步有 last_updated 的股票（减少超时风险）
    target_date = '2026-05-15'
    stocks_to_sync = [(code, stock) for code, stock in stocks_dict.items()
                      if isinstance(stock, dict) and stock.get('last_updated') == target_date]

    print(f"\n{'='*60}")
    print(f"Syncing {len(stocks_to_sync)} stocks to Firebase")
    print(f"{'='*60}\n")

    db = firestore.client(app=app)
    # 增加超时时间到 120 秒
    try:
        db._firestore_api._transport.grpc._channel._timeout = 120.0
    except:
        pass
    synced_count = 0
    failed_count = 0
    batch_size = 500
    total = len(stocks_to_sync)

    # 分批写入（Firestore 每批最多 500 条）
    for batch_start in range(0, total, batch_size):
        batch = db.batch()
        batch_end = min(batch_start + batch_size, total)
        batch_stocks = stocks_to_sync[batch_start:batch_end]

        for code, stock in batch_stocks:
            try:
                doc_ref = db.collection("stocks").document(code)
                batch.set(doc_ref, {
                    "name": stock.get("name", ""),
                    "code": code,
                    "board": stock.get("board", ""),
                    "industry": stock.get("industry", ""),
                    "concepts": stock.get("concepts", []),
                    "products": stock.get("products", []),
                    "core_business": stock.get("core_business", []),
                    "industry_position": stock.get("industry_position", []),
                    "chain": stock.get("chain", []),
                    "partners": stock.get("partners", []),
                    "mention_count": stock.get("mention_count", 0),
                    "articles": stock.get("articles", []),
                    "last_updated": stock.get("last_updated", ""),
                    "updated_at": firestore.SERVER_TIMESTAMP,
                })
                synced_count += 1
            except Exception as e:
                failed_count += 1
                print(f"[FAIL] {code} {stock.get('name', '')} - {e}")

        # 提交批次
        batch.commit()
        print(f"[BATCH] 批次 {batch_start//batch_size + 1}/{(total-1)//batch_size + 1}: {batch_end}/{total} 完成")

    print(f"\n{'='*60}")
    print(f"Sync complete: {synced_count} success, {failed_count} failed")
    print(f"{'='*60}")


if __name__ == "__main__":
    sync_stocks_to_firebase()
