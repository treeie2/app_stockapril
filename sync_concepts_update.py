#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""同步概念更新到 GitHub 和 Firebase"""
import os, sys, json
from pathlib import Path

SKILL_DIR = Path('e:/github/stock-research-backup/.trae/skills/wechat-fetch-research-embedded')
PROJECT_ROOT = SKILL_DIR.parent.parent.parent
scripts_dir = SKILL_DIR / 'scripts'

os.environ['GITHUB_TOKEN'] = 'YOUR_GITHUB_TOKEN_HERE'
os.environ['FIREBASE_CREDENTIALS_PATH'] = str(PROJECT_ROOT / 'api' / 'firebase-credentials.json')
os.environ['PYTHONIOENCODING'] = 'utf-8'

master_path = PROJECT_ROOT / 'data' / 'stocks' / 'stocks_master.json'
intermediate_path = SKILL_DIR / 'data' / 'stocks_master_concepts.json'

# 1. GitHub 同步
print("=" * 60)
print("🚀 同步到 GitHub...")
print("=" * 60)

sys.path.insert(0, str(scripts_dir))
from sync_to_github import GitHubSyncer

syncer = GitHubSyncer(github_token=os.environ['GITHUB_TOKEN'], github_repo='treeie2/app_stockapril', branch='main')
success = syncer.sync_master_file(str(master_path))
print(syncer.get_results_summary())

# 2. Firebase 同步 - 创建包含概念更新的中间文件
print("\n" + "=" * 60)
print("🚀 同步到 Firebase...")
print("=" * 60)

with open(master_path, 'r', encoding='utf-8') as f:
    master = json.load(f)

# 取出有概念信息的股票（这次只传最近更新的概念数据量太大，分批次传）
# 先构建一个只包含 stocks_master 中已有股票概念的完整数据
all_stocks_concepts = []
for code, s in master['stocks'].items():
    all_stocks_concepts.append({
        'code': code,
        'name': s.get('name', ''),
        'board': s.get('board', ''),
        'concepts': s.get('concepts', []),
        'last_updated': s.get('last_updated', '')
    })

with open(intermediate_path, 'w', encoding='utf-8') as f:
    json.dump({'stocks': all_stocks_concepts}, f, ensure_ascii=False, indent=2)

import subprocess
result = subprocess.run(
    [sys.executable, str(scripts_dir / 'sync_to_firestore.py'),
     '--credentials', os.environ['FIREBASE_CREDENTIALS_PATH'],
     '--json', str(intermediate_path),
     '--collection', 'stocks',
     '--article_subcollection', 'articles',
     '--on_exists', 'merge'],
    capture_output=False,
    env={**os.environ}
)

print("\n" + "=" * 60)
print("🎉 同步完成！")
print("=" * 60)