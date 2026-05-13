"""Delete a stock group by directly writing to groups.json."""
import sys
import json
from _common import load_groups, save_groups

def main():
    if len(sys.argv) < 2:
        print("用法: python delete_group.py <group_id>")
        print("示例: python delete_group.py group_20260511000000")
        sys.exit(1)

    group_id = sys.argv[1]
    data = load_groups()

    before = len(data["groups"])
    data["groups"] = [g for g in data["groups"] if g["id"] != group_id]
    after = len(data["groups"])

    if after == before:
        print(f"[ERR] 未找到分组 ID: {group_id}")
        sys.exit(1)

    save_groups(data)
    print(f"[OK] 分组已删除: {group_id}")
    print(f"  (已同步到 agent_store)")

if __name__ == "__main__":
    main()
