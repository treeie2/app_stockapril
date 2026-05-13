"""Add stocks to an existing group by directly writing to groups.json."""
import sys
import json
from _common import load_groups, save_groups, today_str

def main():
    if len(sys.argv) < 3:
        print("用法: python add_stock_to_group.py <group_id> <个股1,个股2,...>")
        print("示例: python add_stock_to_group.py group_20260511000000 \"天齐锂业,赣锋锂业\"")
        sys.exit(1)

    group_id = sys.argv[1]
    new_stocks = [s.strip() for s in sys.argv[2].split(",") if s.strip()]

    if not new_stocks:
        print("[ERR] 请至少提供一个股票名称")
        sys.exit(1)

    data = load_groups()
    found = False
    for g in data["groups"]:
        if g["id"] == group_id:
            existing = g.setdefault("stocks", [])
            added = [s for s in new_stocks if s not in existing]
            if added:
                existing.extend(added)
                g["updated_at"] = today_str()
                save_groups(data)
                print(f"[OK] 已添加 {len(added)} 只股票到 '{g['name']}':")
                for s in added:
                    print(f"  + {s}")
            else:
                print(f"[SKIP] 所有股票已在分组 '{g['name']}' 中，无需重复添加")
            found = True
            break

    if not found:
        print(f"[ERR] 未找到分组 ID: {group_id}")
        sys.exit(1)

    print(f"  (已同步到 agent_store)")

if __name__ == "__main__":
    main()
