"""Remove stocks from an existing group by directly writing to groups.json."""
import sys
import json
from _common import load_groups, save_groups, today_str

def main():
    if len(sys.argv) < 3:
        print("用法: python remove_stock_from_group.py <group_id> <个股1,个股2,...>")
        print("示例: python remove_stock_from_group.py group_20260511000000 \"盐湖股份,藏格矿业\"")
        sys.exit(1)

    group_id = sys.argv[1]
    remove_stocks = [s.strip() for s in sys.argv[2].split(",") if s.strip()]

    if not remove_stocks:
        print("[ERR] 请至少提供一个股票名称")
        sys.exit(1)

    data = load_groups()
    found = False
    for g in data["groups"]:
        if g["id"] == group_id:
            existing = g.get("stocks", [])
            removed = [s for s in remove_stocks if s in existing]
            if removed:
                g["stocks"] = [s for s in existing if s not in remove_stocks]
                g["updated_at"] = today_str()
                save_groups(data)
                print(f"[OK] 已从 '{g['name']}' 移除 {len(removed)} 只股票:")
                for s in removed:
                    print(f"  - {s}")
            else:
                print(f"[SKIP] 未找到要移除的股票 (分组: '{g['name']}')")
            found = True
            break

    if not found:
        print(f"[ERR] 未找到分组 ID: {group_id}")
        sys.exit(1)

    print(f"  (已同步到 agent_store)")

if __name__ == "__main__":
    main()
