#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 同步分组到Firebase

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
    for group in groups['groups']:
        print(f"  - {group['name']}: {len(group['stocks'])} 只股票")


if __name__ == "__main__":
    print("正在同步分组到Firebase...")
    sync_groups_to_firebase()
    print("\n🎉 同步完成！")
