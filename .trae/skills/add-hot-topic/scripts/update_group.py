"""Update an existing stock group by directly editing groups.json."""
import sys
import json
from _common import load_groups, save_groups, today_str

def main():
    if len(sys.argv) < 2:
        print("用法: python update_group.py <分组ID> [选项]")
        print("选项:")
        print("  --name <新名称>")
        print("  --description <新描述>")
        print("  --stocks <个股列表(逗号分隔)>")
        print("  --color <颜色代码>")
        print("  --icon <图标>")
        print()
        print("示例: python update_group.py group_20260511203601 --name \"新名称\" --color \"#ff0000\"")
        print()
        print("可用分组ID:")
        data = load_groups()
        for g in data.get("groups", []):
            print(f"  {g['id']}: {g['name']}")
        sys.exit(1)

    group_id = sys.argv[1]
    data = load_groups()

    # Find the group
    group = None
    idx = None
    for i, g in enumerate(data["groups"]):
        if g["id"] == group_id:
            group = g
            idx = i
            break

    if group is None:
        print(f"[ERROR] 未找到分组: {group_id}")
        print("可用分组:")
        for g in data.get("groups", []):
            print(f"  {g['id']}: {g['name']}")
        sys.exit(1)

    # Parse optional args
    i = 2
    new_name = None
    new_description = None
    new_stocks = None
    new_color = None
    new_icon = None

    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--name" and i + 1 < len(sys.argv):
            new_name = sys.argv[i + 1]; i += 2
        elif arg == "--description" and i + 1 < len(sys.argv):
            new_description = sys.argv[i + 1]; i += 2
        elif arg == "--stocks" and i + 1 < len(sys.argv):
            new_stocks = [s.strip() for s in sys.argv[i + 1].split(",") if s.strip()]; i += 2
        elif arg == "--color" and i + 1 < len(sys.argv):
            new_color = sys.argv[i + 1]; i += 2
        elif arg == "--icon" and i + 1 < len(sys.argv):
            new_icon = sys.argv[i + 1]; i += 2
        else:
            print(f"[WARN] 未知参数: {arg}")
            i += 1

    # Check if anything to update
    if all(v is None for v in [new_name, new_description, new_stocks, new_color, new_icon]):
        print(f"[INFO] 未指定任何更新内容，当前分组信息:")
        print(f"  ID:          {group['id']}")
        print(f"  名称:        {group['name']}")
        print(f"  描述:        {group['description']}")
        print(f"  图标:        {group['icon']}")
        print(f"  颜色:        {group['color']}")
        print(f"  个股 ({len(group['stocks'])} 只): {', '.join(group['stocks']) if group['stocks'] else '无'}")
        print(f"  创建时间:    {group['created_at']}")
        print(f"  更新时间:    {group['updated_at']}")
        sys.exit(0)

    # Apply updates
    if new_name is not None:
        group["name"] = new_name
        print(f"[UPDATE] 名称: {new_name}")
    if new_description is not None:
        group["description"] = new_description
        print(f"[UPDATE] 描述: {new_description}")
    if new_stocks is not None:
        old_count = len(group["stocks"])
        group["stocks"] = new_stocks
        print(f"[UPDATE] 个股: {old_count} -> {len(new_stocks)} 只")
    if new_color is not None:
        group["color"] = new_color
        print(f"[UPDATE] 颜色: {new_color}")
    if new_icon is not None:
        group["icon"] = new_icon
        print(f"[UPDATE] 图标: {new_icon}")

    group["updated_at"] = today_str()

    # Save
    data["groups"][idx] = group
    save_groups(data)

    print(f"\n[OK] 分组已更新: {group['name']}")
    print(f"  (已同步到 agent_store)")

if __name__ == "__main__":
    main()
