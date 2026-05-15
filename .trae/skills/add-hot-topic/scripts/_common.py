"""Common utilities for hot topic scripts."""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
HOT_TOPICS_FILE = PROJECT_ROOT / "data" / "hot_topics" / "hot_topics.json"
AGENT_STORE_FILE = Path("e:/github/agent_store/data/hot_topics.json")

import shutil

def load_topics():
    """Load hot_topics.json, return {'topics': [...]}."""
    if not HOT_TOPICS_FILE.exists():
        return {"topics": []}
    with open(HOT_TOPICS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_topics(data):
    """Save topics dict to hot_topics.json and sync to agent_store."""
    with open(HOT_TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # Best-effort sync
    try:
        AGENT_STORE_FILE.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HOT_TOPICS_FILE, AGENT_STORE_FILE)
    except Exception:
        pass


def next_id():
    """Generate a new topic ID based on current timestamp."""
    from datetime import datetime
    return f"topic_{datetime.now().strftime('%Y%m%d%H%M%S')}"


def today_str():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")
