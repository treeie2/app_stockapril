---
name: "add-hot-topic"
description: "Adds a new hot topic to the dashboard with name, drivers, and related stocks. Invoke when user wants to add a market hot topic/trend with related stocks."
---

# Add Hot Topic Skill

This skill helps you add a new "热点" (hot topic) to the stock research dashboard.

## What It Does

Adds a hot topic entry to `data/hot_topics.json` with:
- **热点名称**: Topic name (e.g., "光互联", "PCB/CCL", "锂电")
- **驱动因素**: Description of driving factors
- **相关个股**: Related stock codes/names (comma-separated)

## Usage

### Method 1: Direct Input (Manual)
When user wants to add a hot topic directly, ask for:
1. 热点名称 (Hot topic name)
2. 驱动因素描述 (Driving factors description)
3. 相关个股 (Related stocks, comma-separated)

Then execute:
```bash
cd e:/github/stock-research-backup
python add_hot_topic.py "热点名称" "驱动因素描述" "相关个股1,相关个股2,相关个股3"
```

### Method 2: Extract from Text (with API)
When user provides a text description with multiple hot topics, use the API extraction method:

1. **Extract and process with Doubao API**:
```bash
cd e:/github/stock-research-backup
$env:DOUBAO_API_TOKEN="your-token-here"
python call_api_add_hot_topic.py
```

This will:
- Extract hot topic info from text
- Call Doubao API to structure the data
- Output JSON format with name, drivers, and stocks

2. **Add each topic to dashboard**:
```bash
cd e:/github/stock-research-backup
python add_hot_topic.py "稀土" "Q2精矿交易价上调至3.88万元/吨..." "中稀有色,北方稀土"
python add_hot_topic.py "钨" "历经1个半月回调去库接近尾声..." ""
```

## Example Workflow

### Direct Input Example:
```
User: 添加一个热点：光互联
Agent: 请提供驱动因素描述和相关个股
User: 驱动因素：AI算力需求爆发... 相关个股：中际旭创, 新易盛, 天孚通信
Agent: python add_hot_topic.py "光互联" "AI算力需求爆发..." "中际旭创,新易盛,天孚通信"
```

### Text Extraction Example:
```
User: 稀土方面：Q2精矿交易价上调至3.88万元/吨... 钨方面：历经1个半月回调...
Agent: python call_api_add_hot_topic.py
[API returns structured data]
Agent: python add_hot_topic.py "稀土" "Q2精矿交易价上调..." "中稀有色,北方稀土"
Agent: python add_hot_topic.py "钨" "历经1个半月回调..." ""
```

## Data Format

The hot topic will be added to `data/hot_topics.json`:
```json
{
  "topics": [
    {
      "id": "unique-id",
      "name": "热点名称",
      "drivers": "驱动因素描述",
      "stocks": ["股票1", "股票2", "股票3"],
      "created_at": "2026-04-16",
      "updated_at": "2026-04-16"
    }
  ]
}
```

## API Configuration

The API extraction uses Doubao (豆包) model:
- Model: `doubao-seed-2-0-lite-260215`
- API Endpoint: `https://ark.cn-beijing.volces.com/api/v3/responses`
- Auth: Bearer token (pre-configured in script)

### Environment Setup

Set the API token as environment variable:
```bash
export DOUBAO_API_TOKEN="your-api-token-here"
```

Or in Windows PowerShell:
```powershell
$env:DOUBAO_API_TOKEN="your-api-token-here"
```

### File Paths

All operations are based from:
- **Working Directory**: `e:/github/stock-research-backup`
- **Hot Topics File**: `e:/github/stock-research-backup/data/hot_topics.json`
- **Scripts Location**: `e:/github/stock-research-backup/`
- **GitHub Target**: `e:/github/agent_store`

## Implementation Steps

### For Direct Input:
1. Read existing `data/hot_topics.json`
2. Create new topic entry with unique ID
3. Add to topics array
4. Save updated JSON
5. Push to GitHub

### For Text Extraction:
1. Extract hot topics from text locally
2. Call Doubao API to structure data
3. Parse API response
4. For each topic, call `add_hot_topic.py`
5. Push all changes to GitHub

## Push to GitHub

After adding topics, push changes:
```bash
python push_hot_topics.py
```

Or manually:
```bash
cd e:/github/agent_store
git add data/hot_topics.json
git commit -m "Add hot topic: [topic name]"
git push github HEAD:main -f
```

## Files

- `add_hot_topic.py` - Add single hot topic
- `call_api_add_hot_topic.py` - Extract from text using API
- `extract_hot_topic_info.py` - Local text extraction (fallback)
