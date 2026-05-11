---
name: "add-hot-topic"
description: "Manage hot topics: add, update, delete, list, and view market hot topics/trends with related stocks. Scripts work directly on data files without requiring Flask."
---

# Hot Topic Management Skill

Manage market hot topics (热点) on the stock research dashboard. Supports full CRUD operations.

**Key advantage:** All scripts work directly on `data/hot_topics.json` — **no Flask server needed**.

## What You Can Do

- **Add** a new hot topic (name + drivers + related stocks)
- **Update** an existing hot topic
- **Delete** a hot topic
- **List** all hot topics
- **Batch import** hot topics from a text description (AI extraction)

## Scripts (in `scripts/` directory)

All scripts work directly on `data/hot_topics.json`, no server required.

### Add a hot topic

```powershell
cd .trae/skills/add-hot-topic/scripts
python add_hot_topic.py "磷化铟" "AI光互联需求爆发" "株冶集团,锡业股份,云南锗业"
```

### List all hot topics

```powershell
cd .trae/skills/add-hot-topic/scripts
python list_hot_topics.py
```

### Update a hot topic

```powershell
cd .trae/skills/add-hot-topic/scripts
python update_hot_topic.py "topic_20260509000000" --name "新名称" --drivers "新驱动" --stocks "个股1,个股2"
```

### Delete a hot topic

```powershell
cd .trae/skills/add-hot-topic/scripts
python delete_hot_topic.py "topic_20260509000000"
```

## What the Scripts Do

1. **Read** `data/hot_topics.json`
2. **Modify** the topics list (add / update / delete)
3. **Write** back to `data/hot_topics.json`
4. **Sync** to `e:/github/agent_store/data/hot_topics.json` (best-effort)
5. **Print** result to console

## Data Format

```json
{
  "topics": [
    {
      "id": "topic_20260509000000",
      "name": "磷化铟",
      "drivers": "AI光互联需求爆发...",
      "stocks": ["株冶集团", "锡业股份"],
      "created_at": "2026-05-09",
      "updated_at": "2026-05-09"
    }
  ]
}
```

## Batch Import from Text (AI Extraction)

When the user provides a text with multiple hot topics:

1. AI extracts structured data (topic name, drivers, stocks) from the text
2. Call `add_hot_topic.py` for each topic

**Example:**
```
User: "稀土方面：Q2精矿交易价上调。钨方面：去库接近尾声。"
AI:  [Extracts 2 topics]
AI:  python add_hot_topic.py "稀土" "Q2精矿交易价上调" "中稀有色,北方稀土"
AI:  python add_hot_topic.py "钨" "去库接近尾声" ""
```

## Also Available: Flask API (if app is running)

| Method | Endpoint | Action |
|--------|-----------|---------|
| GET | `/api/hot-topics` | List visible topics (display=true) |
| GET | `/api/all-hot-topics` | List all topics (including hidden) |
| GET | `/api/hot-topic/<id>` | Get one topic |
| POST | `/api/hot-topic` | Add new |
| PUT | `/api/hot-topic/<id>` | Update |
| PUT | `/api/hot-topic/<id>/display` | Toggle display |
| DELETE | `/api/hot-topic/<id>` | Delete |
| POST | `/api/reload-hot-topics` | Reload from file |
| PUT | `/api/hot-topics/batch-display` | Batch update display |

These are used by the web UI but are **not required** for the scripts.

## Verify

After adding topics:
1. Start the app: `python main.py`
2. Open `http://localhost:5000`
3. Hot topic cards should appear on the dashboard
