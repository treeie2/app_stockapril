#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 同步热点和分组到 Firebase

import json
from pathlib import Path
from firebase_hot_topics import sync_to_firebase, sync_groups_to_firebase

# 1. 同步热点数据
hot_topics_file = Path("data/hot_topics/hot_topics.json")
with open(hot_topics_file, 'r', encoding='utf-8') as f:
    hot_topics = json.load(f)

print("正在同步热点数据到 Firebase...")
sync_to_firebase(hot_topics['topics'])

# 2. 同步分组数据
groups_file = Path("data/groups/groups.json")
with open(groups_file, 'r', encoding='utf-8') as f:
    groups = json.load(f)

print("\n正在同步分组数据到 Firebase...")
sync_groups_to_firebase(groups['groups'])

print("\n✅ Firebase 同步完成！")
