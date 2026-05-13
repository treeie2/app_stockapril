"""Add a new stock group by directly writing to groups.json."""
import sys
import json
from _common import load_groups, save_groups, next_id, today_str

def main():
    if len(sys.argv) < 2:
        print("用法: python add_group.py <分组名称> [描述] [个股(逗号分隔)] [--color 颜色代码] [--icon 图标]")
        print("示例: python add_group.py \"锂资源\" \"锂矿资源相关股票\" \"盐湖股份,藏格矿业\" --color \"#10b981\" --icon \"⚡\"")
        sys.exit(1)

    name = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else ""
    stocks = []
    color = "#3b82f6"
    icon = "📁"

    # Parse optional args
    i = 2
    if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
        i = 3  # description consumed
    if len(sys.argv) > 3 and not sys.argv[3].startswith("--"):
        stocks = [s.strip() for s in sys.argv[3].split(",") if s.strip()]
        i = 4
    elif len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
        stocks = [s.strip() for s in sys.argv[2].split(",") if s.strip()]

    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--color" and i + 1 < len(sys.argv):
            color = sys.argv[i + 1]; i += 2
        elif arg == "--icon" and i + 1 < len(sys.argv):
            icon = sys.argv[i + 1]; i += 2
        else:
            # Try parsing as stocks if not a flag
            if not arg.startswith("--") and not stocks:
                stocks = [s.strip() for s in arg.split(",") if s.strip()]
            i += 1

    data = load_groups()

    if any(g["name"] == name for g in data["groups"]):
        print(f"[SKIP] 分组 '{name}' 已存在，跳过")
        sys.exit(0)

    today = today_str()
    group = {
        "id": next_id(),
        "name": name,
        "description": description,
        "color": color,
        "icon": icon,
        "stocks": stocks,
        "created_at": today,
        "updated_at": today,
    }
    data["groups"].append(group)
    save_groups(data)

    print(f"[OK] 分组已添加: {name}")
    print(f"  ID:       {group['id']}")
    print(f"  描述:     {description[:60]}{'...' if len(description) > 60 else ''}")
    print(f"  图标:     {icon}")
    print(f"  颜色:     {color}")
    print(f"  个股 ({len(stocks)} 只): {', '.join(stocks) if stocks else '无'}")
    print(f"  (已同步到 agent_store)")

if __name__ == "__main__":
    main()
