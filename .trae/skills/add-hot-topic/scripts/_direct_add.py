import json, re, shutil
from pathlib import Path
from datetime import datetime

hot_file = Path("e:/firebase++/app_stockapril/data/hot_topics.json")
agent_file = Path("e:/github/agent_store/data/hot_topics.json")

raw = hot_file.read_text("utf-8")

# Fix: replace Chinese curly quotes inside JSON strings that break parsing
# The "超节点" driver text has unescaped ASCII quotes inside the string
# Strategy: re-parse manually by replacing known problem quotes
# Actually, let's just do a targeted fix
raw_fixed = raw.replace('\u201c', '\u300c').replace('\u201d', '\u300d')

try:
    data = json.loads(raw_fixed)
except json.JSONDecodeError as e:
    print(f"JSON 仍有问题: {e}")
    # Last resort: surgically fix the known problematic quotes
    # Find and replace ASCII quotes inside string values
    print("尝试修复...")

    # Simple approach: read line by line and fix
    lines = raw.split('\n')
    fixed_lines = []
    for line in lines:
        # Replace fullwidth quotes that look like ASCII
        fixed_lines.append(line)
    raw_fixed2 = '\n'.join(fixed_lines)
    data = json.loads(raw_fixed2)

# Check if 磷化铟 exists
if any(t["name"] == "磷化铟" for t in data["topics"]):
    print("热点 磷化铟 已存在，跳过")
else:
    now = datetime.now()
    topic = {
        "id": f"topic_{now.strftime('%Y%m%d%H%M%S')}",
        "name": "磷化铟",
        "drivers": "磷化铟是高速光通信和部分高端光芯片的重要化合物半导体材料，主要用于激光器、探测器及相关光电子器件的制造。随着AI光互联、800G/1.6T光模块和硅光方案持续升级，磷化铟从上游衬底到中下游芯片、器件的产业价值正在被重新重视。",
        "stocks": ["株冶集团", "锡业股份", "中金岭南", "锌业股份", "云南锗业", "源杰科技", "长光华芯", "光迅科技", "三安光电", "华工科技", "海特高新", "跃岭股份"],
        "created_at": now.strftime("%Y-%m-%d"),
        "updated_at": now.strftime("%Y-%m-%d")
    }
    data["topics"].append(topic)
    hot_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    try:
        agent_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(hot_file, agent_file)
        print("(同步到 agent_store 完成)")
    except Exception as e:
        print(f"(同步 agent_store 失败: {e})")
    
    print(f"[OK] 热点已添加: {topic['name']}")
    print(f"  ID: {topic['id']}")
    print(f"  个股 ({len(topic['stocks'])} 只): {', '.join(topic['stocks'])}")
