"""Common utilities for stock group scripts."""
import json
from pathlib import Path

PROJECT_ROOT = Path("e:/firebase++/app_stockapril")
GROUPS_FILE = PROJECT_ROOT / "data" / "groups" / "groups.json"
AGENT_STORE_FILE = Path("e:/github/agent_store/data/groups.json")

import shutil

def load_groups():
    """Load groups.json, return {'groups': [...]}."""
    if not GROUPS_FILE.exists():
        return {"groups": []}
    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_groups(data):
    """Save groups dict to groups.json and sync to agent_store."""
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # Best-effort sync
    try:
        AGENT_STORE_FILE.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(GROUPS_FILE, AGENT_STORE_FILE)
    except Exception:
        pass


def next_id():
    """Generate a new group ID based on current timestamp."""
    from datetime import datetime
    return f"group_{datetime.now().strftime('%Y%m%d%H%M%S')}"


def today_str():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")
