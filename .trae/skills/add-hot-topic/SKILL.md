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

## Complete Workflow: 生成 → 保存 → 推送 → 上线

### 步骤 1: 生成热点数据

#### 方式 A: 直接输入（手动）
当用户想要直接添加热点时，询问：
1. 热点名称 (Hot topic name)
2. 驱动因素描述 (Driving factors description)
3. 相关个股 (Related stocks, comma-separated)

然后执行：
```powershell
cd e:/github/stock-research-backup
python add_hot_topic.py "热点名称" "驱动因素描述" "相关个股 1，相关个股 2，相关个股 3"
```

#### 方式 B: 从文本提取（使用 API）
当用户提供包含多个热点的文本描述时，使用 API 提取方法：

1. **使用 Doubao API 提取和结构化数据**：
```powershell
cd e:/github/stock-research-backup
$env:DOUBAO_API_TOKEN="your-token-here"
python call_api_add_hot_topic.py
```

这会：
- 从文本中提取热点信息
- 调用 Doubao API 结构化数据
- 输出 JSON 格式（包含名称、驱动因素、个股）

2. **逐个添加到 dashboard**：
```powershell
cd e:/github/stock-research-backup
python add_hot_topic.py "稀土" "Q2 精矿交易价上调至 3.88 万元/吨..." "中稀有色，北方稀土"
python add_hot_topic.py "钨" "历经 1 个半月回调去库接近尾声..." ""
```

### 步骤 2: 保存到本地

`add_hot_topic.py` 脚本会自动：
- 读取现有的 `data/hot_topics.json`
- 创建新的热点条目（包含唯一 ID 和时间戳）
- 保存到 `e:/github/stock-research-backup/data/hot_topics.json`

输出示例：
```
✅ 热点已添加：光互联
   ID: topic_20260421153045
   驱动因素：AI 算力需求爆发...
   相关个股：中际旭创，新易盛，天孚通信
```

### 步骤 3: 推送到 GitHub

脚本会自动完成推送（推荐）：
```powershell
# add_hot_topic.py 会自动执行以下步骤
# 1. 复制文件到 agent_store
# 2. git add
# 3. git commit
# 4. git push
```

或者手动推送：
```powershell
cd e:/github/agent_store
git add data/hot_topics.json
git commit -m "Add hot topic: 光互联"
git push github HEAD:main -f
```

### 步骤 4: 上线（Vercel 自动部署）

推送后，Vercel 会自动：
1. 检测到 GitHub 仓库更新
2. 触发自动构建和部署
3. 更新线上数据

验证部署：
- 访问 https://vercel.com/dashboard
- 查看部署状态
- 访问线上网站验证热点已显示

## Example Workflow

### 直接输入示例：
```
User: 添加一个热点：光互联
Agent: 请提供驱动因素描述和相关个股
User: 驱动因素：AI 算力需求爆发，政策支持... 相关个股：中际旭创，新易盛，天孚通信
Agent: python add_hot_topic.py "光互联" "AI 算力需求爆发，政策支持..." "中际旭创，新易盛，天孚通信"

[输出]
✅ 热点已添加：光互联
   ID: topic_20260421153045
   驱动因素：AI 算力需求爆发，政策支持...
   相关个股：中际旭创，新易盛，天孚通信

📤 推送到 GitHub...
   ✅ 文件已复制到 agent_store
   ✅ Git add 完成
   ✅ Git commit 完成
   ✅ Git push 完成

✅ 全部完成!
   热点已推送到 GitHub
   Vercel 会自动重新部署
```

### 文本提取示例：
```
User: 稀土方面：Q2 精矿交易价上调至 3.88 万元/吨... 钨方面：历经 1 个半月回调...
Agent: python call_api_add_hot_topic.py

[API 返回结构化数据]
热点 1: 稀土
  驱动因素：Q2 精矿交易价上调至 3.88 万元/吨...
  相关个股：中稀有色，北方稀土

热点 2: 钨
  驱动因素：历经 1 个半月回调去库接近尾声...
  相关个股：

Agent: python add_hot_topic.py "稀土" "Q2 精矿交易价上调..." "中稀有色，北方稀土"
Agent: python add_hot_topic.py "钨" "历经 1 个半月回调..." ""
```

## Data Format

热点数据保存在 `data/hot_topics.json`：
```json
{
  "topics": [
    {
      "id": "topic_20260421153045",
      "name": "光互联",
      "drivers": "AI 算力需求爆发，政策支持...",
      "stocks": ["中际旭创", "新易盛", "天孚通信"],
      "created_at": "2026-04-21",
      "updated_at": "2026-04-21"
    }
  ]
}
```

## API Configuration

API 提取使用 Doubao (豆包) 模型：
- Model: `doubao-seed-2-0-lite-260215`
- API Endpoint: `https://ark.cn-beijing.volces.com/api/v3/responses`
- Auth: Bearer token (脚本中预配置)

### 环境变量设置

设置 API token：
```bash
export DOUBAO_API_TOKEN="your-api-token-here"
```

或在 Windows PowerShell：
```powershell
$env:DOUBAO_API_TOKEN="your-api-token-here"
```

## File Paths

所有操作基于：
- **工作目录**: `e:/github/stock-research-backup`
- **热点文件**: `e:/github/stock-research-backup/data/hot_topics.json`
- **脚本位置**: `e:/github/stock-research-backup/`
- **GitHub 目标**: `e:/github/agent_store`

## Implementation Details

### add_hot_topic.py 脚本流程：
1. 解析输入参数（名称、驱动因素、个股）
2. 读取现有 `data/hot_topics.json`
3. 生成唯一 ID 和时间戳
4. 创建新热点条目
5. 保存更新后的 JSON
6. **自动推送到 GitHub**：
   - 复制文件到 `agent_store`
   - `git add`
   - `git commit`
   - `git push github HEAD:main -f`

### call_api_add_hot_topic.py 脚本流程：
1. 从输入文本中提取热点描述
2. 调用 Doubao API 进行结构化
3. 解析 API 响应
4. 输出格式化的热点信息
5. 对每个热点调用 `add_hot_topic.py`

## Files

- `add_hot_topic.py` - 添加单个热点并自动推送
- `call_api_add_hot_topic.py` - 使用 API 从文本提取
- `extract_hot_topic_info.py` - 本地文本提取（备用方案）
- `push_manual.md` - 手动推送指南

## Troubleshooting

### 推送失败
如果遇到网络问题，可以手动推送：
```powershell
cd e:/github/agent_store
git status
git add data/hot_topics.json
git commit -m "Add hot topic: [名称]"
git push github HEAD:main -f
```

### 验证线上数据
```powershell
# 检查本地文件
cat data/hot_topics.json

# 检查 GitHub 仓库
# 访问 https://github.com/treeie2/stock-research/blob/main/data/hot_topics.json

# 检查 Vercel 部署
# 访问 https://vercel.com/dashboard
```
