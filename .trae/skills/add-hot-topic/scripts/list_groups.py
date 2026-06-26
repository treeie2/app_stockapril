"""List all stock groups from groups.json."""
import json
from _common import load_groups

def main():
    data = load_groups()
    groups = data.get("groups", [])

    if not groups:
        print("暂无分组数据")
        return

    print(f"共 {len(groups)} 个分组:\n")
    for i, g in enumerate(groups, 1):
        stocks = g.get("stocks", [])
        stock_str = ", ".join(stocks) if stocks else "无"
        desc = g.get("description", "")
        print(f"{i}. {g.get('icon', '📁')} {g['name']}")
        print(f"   ID:         {g.get('id', '(无ID)')}")
        print(f"   描述:       {desc[:60]}{'...' if len(desc) > 60 else ''}")
        print(f"   颜色:       {g.get('color', '#3b82f6')}")
        print(f"   个股 ({len(stocks)} 只): {stock_str}")
        print(f"   创建:       {g.get('created_at', '')}")
        print()

if __name__ == "__main__":
    main()
