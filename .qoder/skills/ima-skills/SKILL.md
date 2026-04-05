---
name: ima-skills
description: 统一的 IMA OpenAPI 技能，支持笔记管理和知识库操作。当用户提到知识库、资料库、笔记、备忘录、记事，或者想要上传文件、添加网页到知识库、搜索知识库内容、搜索/浏览/创建/编辑笔记时使用此 Skill。
---

# ima-skill

统一的 IMA OpenAPI 技能。目前支持：笔记管理、知识库操作。

## 安全说明

此 Skill 使用官方 IMA API (ima.qq.com) 进行身份验证，凭证仅作为 HTTP 头发送到 ima.qq.com，不会发送到其他域名、文件或日志。

## 配置步骤

1. 打开 https://ima.qq.com/agent-interface 获取 Client ID 和 API Key
2. 存储凭证（二选一）：

**方式 A — 配置文件（推荐）**：
```bash
mkdir -p ~/.config/ima
echo "your_client_id" > ~/.config/ima/client_id
echo "your_api_key" > ~/.config/ima/api_key
```

**方式 B — 环境变量**：
```bash
export IMA_OPENAPI_CLIENTID="your_client_id"
export IMA_OPENAPI_APIKEY="your_api_key"
```

Agent 会按优先级依次尝试：环境变量 → 配置文件。

## 凭证预检

每次调用 API 前，先确认凭证可用。如果两个值都为空，停止操作并提示用户按 Setup 步骤配置。

```bash
# Load user-provisioned IMA credentials
IMA_CLIENT_ID="${IMA_OPENAPI_CLIENTID:-$(cat ~/.config/ima/client_id 2>/dev/null)}"
IMA_API_KEY="${IMA_OPENAPI_APIKEY:-$(cat ~/.config/ima/api_key 2>/dev/null)}"
if [ -z "$IMA_CLIENT_ID" ] || [ -z "$IMA_API_KEY" ]; then
    echo "缺少 IMA 凭证，请按 Setup 步骤配置 Client ID 和 API Key"
    exit 1
fi
```

## API 调用模板

所有请求统一为 HTTP POST + JSON Body，仅发往官方 Base URL https://ima.qq.com。

```python
import requests
import os

# 获取凭证
client_id = os.getenv('IMA_OPENAPI_CLIENTID') or open(os.path.expanduser('~/.config/ima/client_id')).read().strip()
api_key = os.getenv('IMA_OPENAPI_APIKEY') or open(os.path.expanduser('~/.config/ima/api_key')).read().strip()

headers = {
    'ima-openapi-clientid': client_id,
    'ima-openapi-apikey': api_key,
    'Content-Type': 'application/json'
}

# 调用 API
response = requests.post(
    'https://ima.qq.com/api/endpoint',
    headers=headers,
    json={}
)
```

## 功能模块

### 1. 笔记模块 (notes)

**使用场景**：
- 搜索笔记
- 浏览笔记本
- 获取笔记内容
- 创建笔记
- 追加内容到笔记

**自然语言指令**：
- 「搜索笔记」
- 「看看我的笔记」
- 「创建新笔记」
- 「添加到笔记XX」

### 2. 知识库模块 (knowledge-base)

**使用场景**：
- 上传文件到知识库
- 添加网页链接到知识库
- 搜索知识库内容
- 浏览知识库
- 获取知识库信息

**自然语言指令**：
- 「上传文件到知识库」
- 「添加网页到知识库」
- 「搜索知识库」
- 「知识库里有XX吗」

## 模块决策表

| 用户意图 | 模块 | 说明 |
| --- | --- | --- |
| 搜索笔记、浏览笔记本、获取笔记内容、创建笔记、追加内容 | notes | 笔记操作 |
| 上传文件、添加网页链接、搜索知识库、浏览知识库 | knowledge-base | 知识库操作 |

## ⚠️ 易混淆场景

| 用户说的 | 实际意图 | 正确路由 |
| --- | --- | --- |
| "把这段内容添加到知识库XX里的笔记YY" | 往已有笔记追加内容 | notes |
| "把这个写到XX笔记里" | 往已有笔记追加内容 | notes |
| "把这篇笔记添加到知识库" | 将笔记关联到知识库 | knowledge-base |
| "上传文件到知识库" | 上传文件到知识库 | knowledge-base |
| "帮我记一下"（未指定已有笔记） | 意图不明确，需要确认 | 询问用户 |

## 注意事项

- 所有写入操作前必须完成 UTF-8 编码校验
- 文件上传会保持原样
- 上传文件大小有限制，大文件需要先检查
