#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Firebase 与 stocks_master.json 双向同步脚本"""
import os, json, sys
os.environ["NO_PROXY"] = "*"

MASTER_FILE = "data/stocks/stocks_master.json"

def load_local_master():
    with open(MASTER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def convert_firestore_types(obj):
    if hasattr(obj, '__class__') and obj.__class__.__name__ == 'DatetimeWithNanoseconds':
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_firestore_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_firestore_types(item) for item in obj]
    return obj

def save_local_master(data):
    data = convert_firestore_types(data)
    with open(MASTER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_firebase_stocks():
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
        result[doc.id] = doc.to_dict()
    return result, db

def main():
    print("=" * 70)
    print("🔄 Firebase 与 stocks_master.json 双向同步")
    print(f"⏱  {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 加载数据
    print("\n📥 加载数据...")
    master = load_local_master()
    master_stocks = master.get("stocks", {})
    master_codes = set(master_stocks.keys())
    print(f"   本地 stocks_master.json: {len(master_codes)} 只股票")

    fb_result = get_firebase_stocks()
    if not fb_result:
        return
    fb_stocks, db = fb_result
    fb_codes = set(fb_stocks.keys())
    print(f"   Firebase stocks 集合: {len(fb_codes)} 只股票")

    # 计算差异
    print("\n🔍 分析差异...")
    only_master = master_codes - fb_codes
    only_fb = fb_codes - master_codes
    both = master_codes & fb_codes

    print(f"   两边都有:     {len(both)} 只")
    print(f"   仅本地有:     {len(only_master)} 只 (上传到 Firebase)")
    print(f"   仅 Firebase 有: {len(only_fb)} 只 (下载到本地)")

    # 上传本地独有的到 Firebase
    if only_master:
        print(f"\n⬆️ 上传 {len(only_master)} 只股票到 Firebase...")
        count = 0
        for code in sorted(only_master):
            stock = master_stocks[code]
            stock['sync_from'] = 'local_master'
            stock['sync_time'] = __import__('datetime').datetime.now().isoformat()
            try:
                db.collection('stocks').document(code).set(stock)
                count += 1
                print(f"      ✅ {code} {stock.get('name','?')}")
            except Exception as e:
                print(f"      ❌ {code} 上传失败: {e}")
        print(f"   成功上传: {count}/{len(only_master)}")

    # 下载 Firebase 独有的到本地
    if only_fb:
        print(f"\n⬇️ 下载 {len(only_fb)} 只股票到本地...")
        count = 0
        for code in sorted(only_fb):
            stock = fb_stocks[code]
            stock['sync_from'] = 'firebase'
            stock['sync_time'] = __import__('datetime').datetime.now().isoformat()
            master_stocks[code] = stock
            count += 1
            if count <= 5 or count % 200 == 0:
                print(f"      ✅ {code} {stock.get('name','?')}")
        print(f"   成功下载: {count}/{len(only_fb)}")

    # 同步两边都有的股票（以本地为准）
    print(f"\n🔄 同步两边都有的 {len(both)} 只股票...")
    update_count = 0
    for code in both:
        local = master_stocks[code]
        fb = fb_stocks.get(code, {})
        need_update = False

        if local.get('last_updated') and local.get('last_updated') != fb.get('last_updated'):
            fb['last_updated'] = local['last_updated']
            need_update = True
        if local.get('articles') and local.get('articles') != fb.get('articles'):
            fb['articles'] = local['articles']
            need_update = True

        fields = ['industry_position', 'core_business', 'products', 'chain', 'partners', 'concepts']
        for field in fields:
            if local.get(field) and local.get(field) != fb.get(field):
                fb[field] = local.get(field)
                need_update = True

        if need_update:
            try:
                db.collection('stocks').document(code).set(fb)
                update_count += 1
            except:
                pass
    
    print(f"   更新完成: {update_count} 只股票")

    # 保存本地文件
    master['stocks'] = master_stocks
    master['updated_at'] = __import__('datetime').datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    save_local_master(master)
    print(f"\n✅ 已保存到 stocks_master.json")

    # 验证
    final_count = len(master_stocks)
    print(f"\n📋 同步完成!")
    print(f"   本地 stocks_master.json: {final_count} 只股票")
    print(f"   Firebase stocks 集合:   {len(fb_codes) + len(only_master)} 只股票")

if __name__ == "__main__":
    main()