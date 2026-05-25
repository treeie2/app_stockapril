#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""热点数据同步脚本"""
import json
from pathlib import Path

# 添加父目录到路径
import sys
sys.path.insert(0, str(Path(__file__).parent))

from firebase_hot_topics import sync_to_firebase

def main():
    # 读取热点数据
    hot_topics_path = Path(__file__).parent / "data" / "hot_topics" / "hot_topics.json"
    
    if not hot_topics_path.exists():
        print(f"❌ 热点文件不存在: {hot_topics_path}")
        return
    
    with open(hot_topics_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    topics = data.get("topics", [])
    print(f"📖 读取到 {len(topics)} 个热点")
    
    # 同步到 Firebase
    print("\n🔄 同步到 Firebase...")
    sync_to_firebase(topics)
    
    print("\n✅ 同步完成")

if __name__ == "__main__":
    main()
