"""Delete a hot topic by directly writing to hot_topics.json."""
import sys
import json
from _common import load_topics, save_topics

def main():
    if len(sys.argv) < 2:
        print("用法: python delete_hot_topic.py <topic_id>")
        print("示例: python delete_hot_topic.py topic_20260506000000")
        sys.exit(1)

    topic_id = sys.argv[1]
    data = load_topics()

    before = len(data["topics"])
    data["topics"] = [t for t in data["topics"] if t["id"] != topic_id]
    after = len(data["topics"])

    if after == before:
        print(f"[ERR] 未找到热点 ID: {topic_id}")
        sys.exit(1)

    save_topics(data)
    print(f"[OK] 热点已删除: {topic_id}")
    print(f"  (已同步到 agent_store)")

if __name__ == "__main__":
    main()
