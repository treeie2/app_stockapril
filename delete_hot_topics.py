#!/usr/bin/env python3
"""
直接删除指定的热点
"""
import json
from pathlib import Path

HOT_TOPICS_FILE = Path("e:/github/stock-research-backup/data/hot_topics.json")

def delete_hot_topics_except(names_to_keep):
    """只保留指定的热点，删除其他所有热点"""
    if not HOT_TOPICS_FILE.exists():
        print(f"❌ 热点文件不存在：{HOT_TOPICS_FILE}")
        return
    
    # 读取热点数据
    with open(HOT_TOPICS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    topics = data.get('topics', [])
    original_count = len(topics)
    
    # 过滤出要保留的热点
    kept_topics = []
    deleted_topics = []
    
    for topic in topics:
        if topic.get('name') in names_to_keep:
            kept_topics.append(topic)
            print(f"  ✅ 保留：{topic.get('name')}")
        else:
            deleted_topics.append(topic)
            print(f"  🗑️  删除：{topic.get('name')} (ID: {topic.get('id')})")
    
    # 更新数据
    data['topics'] = kept_topics
    
    # 保存回文件
    with open(HOT_TOPICS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 清理完成！")
    print(f"   原始数量：{original_count}")
    print(f"   删除数量：{len(deleted_topics)}")
    print(f"   保留数量：{len(kept_topics)}")
    
    # 同步到 agent_store
    sync_to_agent_store()

def sync_to_agent_store():
    """同步到 agent_store"""
    try:
        import shutil
        target_file = Path("e:/github/agent_store/data/hot_topics.json")
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HOT_TOPICS_FILE, target_file)
        print(f"✅ 已同步到 agent_store")
    except Exception as e:
        print(f"⚠️ 同步到 agent_store 失败：{e}")

if __name__ == '__main__':
    print("🚀 开始清理热点...\n")
    
    # 要保留的热点名称
    names_to_keep = [
        "稀土",
        "钨",
        "PCB/CCL",
        "晶圆代工涨价"
    ]
    
    print(f"📋 保留列表:")
    for name in names_to_keep:
        print(f"   ✓ {name}")
    print()
    
    delete_hot_topics_except(names_to_keep)
