"""List all hot topics from hot_topics.json."""
import json
from _common import load_topics

def main():
    data = load_topics()
    topics = data.get("topics", [])

    if not topics:
        print("暂无热点数据")
        return

    print(f"共 {len(topics)} 个热点:\n")
    for i, t in enumerate(topics, 1):
        stocks = t.get("stocks", [])
        stock_str = ", ".join(stocks) if stocks else "无"
        drivers = t.get("drivers", "")
        print(f"{i}. {t['name']}")
        print(f"   ID:        {t.get('id', '(无ID)')}")
        print(f"   驱动因素:  {drivers[:70]}{'...' if len(drivers) > 70 else ''}")
        print(f"   个股 ({len(stocks)} 只): {stock_str}")
        print(f"   创建:      {t.get('created_at', '')}")
        print()

if __name__ == "__main__":
    main()
