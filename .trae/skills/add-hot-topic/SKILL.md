---
name: "manage-collections"
description: |
  管理分组和热门题材。支持股票分组（groups）和热门题材（hot topics）的增删改查，
  以及分组内个股管理。所有脚本直接操作数据文件，无需 Flask。
  当用户需要创建/更新/删除分组或热门题材时触发。
---

# 分组 & 热门题材管理 Skill

统一管理两种数据结构：**股票分组**（`data/groups/groups.json`）和 **热门题材**（`data/hot_topics/hot_topics.json`）。

**核心优势**：所有脚本直接操作 JSON 文件，无需 Flask 服务器。

---

## 一、股票分组（Groups）

### 脚本清单

| 脚本 | 功能 |
|------|------|
| `add_group.py` | 创建分组 |
| `list_groups.py` | 列出全部分组 |
| `update_group.py` | 修改分组 |
| `delete_group.py` | 删除分组 |
| `add_stock_to_group.py` | 向分组添加个股 |
| `remove_stock_from_group.py` | 从分组移除个股 |

### 数据格式

```json
{
  "groups": [{
    "id": "group_20260511000000",
    "name": "液冷全产业链",
    "description": "上游冷却液→中游温控→下游IDC",
    "color": "#6366f1",
    "icon": "🧊",
    "stocks": ["英维克", "高澜股份"],
    "source": "微信文章",
    "created_at": "2026-06-25"
  }]
}
```

### CLI 示例

```powershell
# 创建分组
cd .trae/skills/add-hot-topic/scripts
python add_group.py "液冷全产业链" "上游→中游→下游" "英维克,高澜股份,申菱环境" --color "#6366f1" --icon "🧊"

# 列全部分组
python list_groups.py

# 修改分组
python update_group.py "group_20260625000000" --name "新名称" --description "新描述"

# 删除分组
python delete_group.py "group_20260625000000"

# 向分组添加个股
python add_stock_to_group.py "group_20260625000000" "曙光数创,依米康"

# 从分组移除个股
python remove_stock_from_group.py "group_20260625000000" "英维克"
```

### AI 批量导入

当用户提供文本描述多个分组时，AI 自动提取并创建：

```
用户: "锂资源：藏格矿业,盐湖股份。铝业：中国铝业,云铝股份。"
AI:  python add_group.py "锂资源" "" "藏格矿业,盐湖股份" --icon "⚡" --color "#10b981"
AI:  python add_group.py "铝业" "" "中国铝业,云铝股份" --icon "🏭" --color "#f59e0b"
```

---

## 二、热门题材（Hot Topics）

### 脚本清单

| 脚本 | 功能 |
|------|------|
| `add_hot_topic.py` | 创建热门题材 |
| `list_hot_topics.py` | 列出全部题材 |
| `update_hot_topic.py` | 修改题材 |
| `delete_hot_topic.py` | 删除题材 |

### 数据格式

```json
{
  "topics": [{
    "id": "topic_20260625000000",
    "name": "灵晟超算",
    "description": "2.19EFlops登顶全球TOP500",
    "stocks": ["拓维信息", "海光信息", "中科曙光"],
    "created_at": "2026-06-25"
  }]
}
```

### CLI 示例

```powershell
cd .trae/skills/add-hot-topic/scripts

# 创建热门题材
python add_hot_topic.py "灵晟超算" "2.19EFlops登顶TOP500" "拓维信息,海光信息,中科曙光"

# 列全部题材
python list_hot_topics.py

# 修改
python update_hot_topic.py "topic_20260625000000" --name "新名称" --description "新描述"

# 删除
python delete_hot_topic.py "topic_20260625000000"
```

### AI 批量导入

```
用户: "稀土：Q2精矿交易价上调。钨：去库接近尾声。"
AI:  python add_hot_topic.py "稀土" "Q2精矿交易价上调" "中稀有色,北方稀土"
AI:  python add_hot_topic.py "钨" "去库接近尾声" ""
```

---

## 三、快捷操作（AI 直接处理）

无需调用脚本，AI 可直接读写 JSON：

```python
import json

# === 分组操作 ===
g = json.load(open("data/groups/groups.json", "r", encoding="utf-8"))
g["groups"].append({
    "id": f"group_{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "name": "分组名",
    "description": "描述",
    "stocks": ["股票名1", "股票名2"],
    "color": "#6366f1",
    "source": "微信文章"
})
json.dump(g, open("data/groups/groups.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# === 热门题材操作 ===
t = json.load(open("data/hot_topics/hot_topics.json", "r", encoding="utf-8"))
t["topics"].append({
    "id": f"topic_{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "name": "题材名",
    "description": "描述",
    "stocks": ["股票1", "股票2"]
})
json.dump(t, open("data/hot_topics/hot_topics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
```

---

## 四、web UI API（需 Flask 运行）

### 分组 API

| 方法 | 端点 | 操作 |
|------|------|------|
| GET | `/api/groups` | 列所有分组 |
| GET | `/api/group/<id>` | 获取单个 |
| POST | `/api/group` | 创建 |
| PUT | `/api/group/<id>` | 更新 |
| DELETE | `/api/group/<id>` | 删除 |
| POST | `/api/group/<id>/add-stock` | 添加个股 |
| POST | `/api/group/<id>/remove-stock` | 移除个股 |
| GET | `/api/stock/<code>/groups` | 查个股归属 |

### 热门题材 API

| 方法 | 端点 | 操作 |
|------|------|------|
| GET | `/api/hot-topics` | 可见题材 |
| GET | `/api/all-hot-topics` | 全部（含隐藏） |
| GET | `/api/hot-topic/<id>` | 获取单个 |
| POST | `/api/hot-topic` | 创建 |
| PUT | `/api/hot-topic/<id>` | 更新 |
| PUT | `/api/hot-topic/<id>/display` | 切换显示 |
| DELETE | `/api/hot-topic/<id>` | 删除 |

---

## 五、验证

1. 启动 Flask: `python main.py`
2. 分组/题材正确显示在 Dashboard
3. `data/groups/groups.json` 和 `data/hot_topics/hot_topics.json` 内容正确
4. 推送到 GitHub 后自动部署到 ModelScope/Vercel
