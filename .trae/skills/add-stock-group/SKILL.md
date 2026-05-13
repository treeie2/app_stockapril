---
name: "add-stock-group"
description: "Manage stock groups: add, update, delete, list groups, and add/remove stocks from groups. Groups are custom stock collections with icons and colors. Scripts work directly on data files without requiring Flask."
---

# Stock Group Management Skill

Manage custom stock groups (分组) on the stock research dashboard. Supports full CRUD operations plus stock management within groups.

**Key advantage:** All scripts work directly on `data/groups.json` — **no Flask server needed**.

## What You Can Do

- **Add** a new group (name + optional description + stocks + icon + color)
- **Update** an existing group
- **Delete** a group
- **List** all groups
- **Add stocks** to a group
- **Remove stocks** from a group
- **Batch import** groups from a text description (AI extraction)

## Scripts (in `scripts/` directory)

All scripts work directly on `data/groups.json`, no server required.

### Add a group

```powershell
cd .trae/skills/add-stock-group/scripts
python add_group.py "锂资源" "锂矿资源相关股票" "盐湖股份,藏格矿业,永兴材料" --color "#10b981" --icon "⚡"
```

### List all groups

```powershell
cd .trae/skills/add-stock-group/scripts
python list_groups.py
```

### Update a group

```powershell
cd .trae/skills/add-stock-group/scripts
python update_group.py "group_20260511000000" --name "新名称" --description "新描述" --stocks "个股1,个股2" --color "#f59e0b" --icon "🏭"
```

### Delete a group

```powershell
cd .trae/skills/add-stock-group/scripts
python delete_group.py "group_20260511000000"
```

### Add stocks to a group

```powershell
cd .trae/skills/add-stock-group/scripts
python add_stock_to_group.py "group_20260511000000" "天齐锂业,赣锋锂业"
```

### Remove stocks from a group

```powershell
cd .trae/skills/add-stock-group/scripts
python remove_stock_from_group.py "group_20260511000000" "盐湖股份,藏格矿业"
```

## What the Scripts Do

1. **Read** `data/groups.json`
2. **Modify** the groups list (add / update / delete / manage stocks)
3. **Write** back to `data/groups.json`
4. **Sync** to `e:/github/agent_store/data/groups.json` (best-effort)
5. **Print** result to console

## Data Format

```json
{
  "groups": [
    {
      "id": "group_20260511000000",
      "name": "锂资源",
      "description": "锂矿资源相关股票",
      "color": "#10b981",
      "icon": "⚡",
      "stocks": ["盐湖股份", "藏格矿业", "永兴材料", "金圆股份"],
      "created_at": "2026-05-11",
      "updated_at": "2026-05-11"
    }
  ]
}
```

## Batch Import from Text (AI Extraction)

When the user provides a text with multiple groups:

1. AI extracts structured data (group name, description, stocks, icon, color) from the text
2. Call `add_group.py` for each group

**Example:**
```
User: "锂资源：藏格矿业，盐湖股份。铝业：中国铝业，云铝股份。"
AI: [Extracts 2 groups]
AI: python add_group.py "锂资源" "" "藏格矿业,盐湖股份" --icon "⚡" --color "#10b981"
AI: python add_group.py "铝业" "" "中国铝业,云铝股份" --icon "🏭" --color "#f59e0b"
```

## Also Available: Flask API (if app is running)

| Method | Endpoint | Action |
|--------|----------|--------|
| GET | `/api/groups` | List all groups |
| GET | `/api/group/<id>` | Get one group |
| POST | `/api/group` | Add new group |
| PUT | `/api/group/<id>` | Update group |
| DELETE | `/api/group/<id>` | Delete group |
| POST | `/api/group/<id>/add-stock` | Add stock to group |
| POST | `/api/group/<id>/remove-stock` | Remove stock from group |
| GET | `/api/stock/<code>/groups` | Get groups for a stock |

These are used by the web UI but are **not required** for the scripts.

## Verify

After adding/modifying groups:
1. Start the app: `python main.py`
2. Open `http://localhost:5000`
3. Group cards should appear on the dashboard
4. Click a stock detail page to see its group associations
