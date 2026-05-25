#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 Firebase 重建完整的 stocks_master.json"""
import os, json
os.environ["NO_PROXY"] = "*"

MASTER_FILE = "data/stocks/stocks_master.json"

def convert_firestore_types(obj):
    if hasattr(obj, '__class__') and obj.__class__.__name__ == 'DatetimeWithNanoseconds':
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_firestore_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_firestore_types(item) for item in obj]
    return obj

def get_all_firebase_stocks():
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
            break
    if not key_file:
        print("❌ 未找到 Firebase 密钥文件")
        return None

    cred = credentials.Certificate(key_file)
    app = firebase_admin.initialize_app(cred, {'projectId': 'webstock-724'})
    db = firestore.client()
    stocks_ref = db.collection('stocks')
    docs = stocks_ref.get()
    
    result = {}
    for doc in docs:
        result[doc.id] = convert_firestore_types(doc.to_dict())
    return result

def main():
    print("=" * 70)
    print("🔄 从 Firebase 重建 stocks_master.json")
    print(f"⏱  {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    print("\n📥 从 Firebase 下载所有股票数据...")
    fb_stocks = get_all_firebase_stocks()
    if not fb_stocks:
        return
    
    print(f"   成功下载: {len(fb_stocks)} 只股票")

    print("\n💾 保存到 stocks_master.json...")
    master = {
        "stocks": fb_stocks,
        "updated_at": __import__('datetime').datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "total_count": len(fb_stocks)
    }
    
    with open(MASTER_FILE, "w", encoding="utf-8") as f:
        json.dump(master, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 重建完成!")
    print(f"   stocks_master.json 包含 {len(fb_stocks)} 只股票")

if __name__ == "__main__":
    main()
