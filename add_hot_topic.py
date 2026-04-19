#!/usr/bin/env python3
"""
添加热点信息到 dashboard
用法: python add_hot_topic.py "热点名称" "驱动因素描述" "相关个股1,相关个股2,相关个股3"
"""
import json
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("e:/github/stock-research-backup/data/hot_topics.json")
TARGET_DIR = Path("e:/github/agent_store")


def add_hot_topic(name, drivers, stocks_str):
    """添加热点信息"""
    
    # 解析相关个股
    stocks = [s.strip() for s in stocks_str.split(',') if s.strip()]
    
    # 读取现有数据
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"topics": []}
    
    # 生成唯一ID
    topic_id = f"topic_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 创建新热点
    new_topic = {
        "id": topic_id,
        "name": name,
        "drivers": drivers,
        "stocks": stocks,
        "created_at": datetime.now().strftime('%Y-%m-%d'),
        "updated_at": datetime.now().strftime('%Y-%m-%d')
    }
    
    # 添加到列表
    data["topics"].append(new_topic)
    
    # 保存
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 热点已添加: {name}")
    print(f"   ID: {topic_id}")
    print(f"   驱动因素: {drivers[:50]}...")
    print(f"   相关个股: {', '.join(stocks)}")
    
    return True


def push_to_github(name):
    """推送到 GitHub"""
    print("\n📤 推送到 GitHub...")
    
    # 复制文件到 agent_store
    src_file = DATA_FILE
    dst_file = TARGET_DIR / "data/hot_topics.json"
    
    try:
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)
        print("   ✅ 文件已复制到 agent_store")
    except Exception as e:
        print(f"   ❌ 复制失败: {e}")
        return False
    
    # Git add
    result = subprocess.run(["git", "add", "data/hot_topics.json"],
                          cwd=TARGET_DIR, capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✅ Git add 完成")
    else:
        print(f"   ⚠️ Git add: {result.stderr[:100]}")
    
    # Git commit
    result = subprocess.run(["git", "commit", "-m", f"Add hot topic: {name}"],
                          cwd=TARGET_DIR, capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✅ Git commit 完成")
    else:
        print(f"   ⚠️ Commit: {result.stderr[:100]}")
    
    # Git push
    result = subprocess.run(["git", "push", "github", "HEAD:main", "-f"],
                          cwd=TARGET_DIR, capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✅ Git push 完成")
        print("\n✅ 全部完成!")
        return True
    else:
        print(f"   ❌ Git push 失败: {result.stderr[:200]}")
        return False


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python add_hot_topic.py \"热点名称\" \"驱动因素描述\" [\"相关个股1,相关个股2\"]")
        print("示例: python add_hot_topic.py \"光互联\" \"AI算力需求爆发...\" \"中际旭创,新易盛\"")
        print("示例: python add_hot_topic.py \"钨\" \"历经1个半月回调...\" \"\"")
        sys.exit(1)
    
    name = sys.argv[1]
    drivers = sys.argv[2]
    stocks_str = sys.argv[3] if len(sys.argv) > 3 else ""
    
    print(f"🚀 添加热点: {name}\n")
    
    # 添加热点
    if add_hot_topic(name, drivers, stocks_str):
        # 推送到 GitHub
        push_to_github(name)
    else:
        print("❌ 添加热点失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
