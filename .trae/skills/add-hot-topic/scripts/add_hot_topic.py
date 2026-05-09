"""Add a new hot topic by directly writing to hot_topics.json."""
import sys
import json
from _common import load_topics, save_topics, next_id, today_str

def main():
    if len(sys.argv) < 2:
        print("用法: python add_hot_topic.py <热点名称> [驱动因素] [个股(逗号分隔)]")
        print("示例: python add_hot_topic.py \"磷化铟\" \"AI光互联需求\" \"株冶集团,锡业股份\"")
        sys.exit(1)

    name = sys.argv[1]
    drivers = sys.argv[2] if len(sys.argv) > 2 else ""
    stocks = [s.strip() for s in sys.argv[3].split(",") if s.strip()] if len(sys.argv) > 3 else []

    data = load_topics()

    if any(t["name"] == name for t in data["topics"]):
        print(f"[SKIP] 热点 '{name}' 已存在，跳过")
        sys.exit(0)

    today = today_str()
    topic = {
        "id": next_id(),
        "name": name,
        "drivers": drivers,
        "stocks": stocks,
        "created_at": today,
        "updated_at": today,
    }
    data["topics"].append(topic)
    save_topics(data)

    print(f"[OK] 热点已添加: {name}")
    print(f"  ID:       {topic['id']}")
    print(f"  驱动因素: {drivers[:60]}{'...' if len(drivers) > 60 else ''}")
    print(f"  个股 ({len(stocks)} 只): {', '.join(stocks)}")
    print(f"  (已同步到 agent_store)")

if __name__ == "__main__":
    main()
