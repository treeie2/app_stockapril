#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 同步分组和利扬芯片到Firebase

import json
from pathlib import Path
import os

os.environ["NO_PROXY"] = "firestore.googleapis.com,googleapis.com,oauth2.googleapis.com"
os.environ["no_proxy"] = "firestore.googleapis.com,googleapis.com,oauth2.googleapis.com"

FIREBASE_PROJECT_ID = "webstock-724"
KEY_FILES = [
    Path(__file__).parent / "serviceAccountKey.json",
    Path(__file__).parent / "firebase_key.json",
    Path(__file__).parent / "api" / "firebase-credentials.json",
    Path(__file__).parent / ".trae" / "rules" / "firebase-credentials.json",
]


def _get_app():
    import firebase_admin
    from firebase_admin import credentials
    
    if firebase_admin._apps:
        return firebase_admin.get_app()

    key_file = None
    for f in KEY_FILES:
        if f.exists():
            key_file = str(f)
            break

    if not key_file:
        return None

    cred = credentials.Certificate(key_file)
    app = firebase_admin.initialize_app(cred, {
        'projectId': FIREBASE_PROJECT_ID,
    })
    return app


def _get_db():
    app = _get_app()
    if not app:
        return None
    from firebase_admin import firestore
    return firestore.client(app=app)


def sync_groups_to_firebase():
    """同步分组数据到Firebase"""
    db = _get_db()
    if not db:
        return
    from firebase_admin import firestore
    
    groups_file = Path("data/groups/groups.json")
    with open(groups_file, 'r', encoding='utf-8') as f:
        groups = json.load(f)
    
    doc_ref = db.collection("config").document("groups")
    doc_ref.set({
        "groups": groups['groups'],
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    print(f"✅ 分组同步成功 ({len(groups['groups'])} 个分组)")


def sync_liyang_chip():
    """同步利扬芯片完整数据到Firebase"""
    db = _get_db()
    if not db:
        return
    from firebase_admin import firestore
    
    stock_code = "688135"
    master_file = Path("data/stocks/stocks_master.json")
    with open(master_file, 'r', encoding='utf-8') as f:
        master = json.load(f)
    
    if stock_code not in master['stocks']:
        print(f"❌ 本地没有利扬芯片数据")
        return
    
    stock_data = master['stocks'][stock_code]
    
    # 更新stocks文档
    doc_ref = db.collection("stocks").document(stock_code)
    base_data = {
        'name': stock_data.get('name', ''),
        'code': stock_data.get('code', ''),
        'board': stock_data.get('board', ''),
        'industry': stock_data.get('industry', ''),
        'concepts': stock_data.get('concepts', []),
        'core_business': stock_data.get('core_business', []),
        'industry_position': stock_data.get('industry_position', []),
        'chain': stock_data.get('chain', []),
        'partners': stock_data.get('partners', []),
        'last_updated': stock_data.get('last_updated', ''),
        'mention_count': stock_data.get('mention_count', 0),
        'updated_at': firestore.SERVER_TIMESTAMP
    }
    
    doc_ref.set(base_data, merge=True)
    print(f"✅ 已更新利扬芯片基础数据")
    
    # 更新articles子集合
    articles = stock_data.get('articles', [])
    for article in articles:
        article_id = str(abs(hash(article.get('source', '') + article.get('title', ''))))[:10]
        article_ref = doc_ref.collection("articles").document(article_id)
        article_ref.set(article)
        print(f"  - 已添加文章: {article.get('title', '无标题')}")
    
    print(f"✅ 利扬芯片数据已完整同步到Firebase！\n  - articles数量: {len(articles)}")


if __name__ == "__main__":
    print("正在同步分组...")
    sync_groups_to_firebase()
    
    print("\n正在同步利扬芯片...")
    sync_liyang_chip()
    
    print("\n🎉 同步完成！")
