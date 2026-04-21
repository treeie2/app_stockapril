---
name: wechat-fetch-research-embedded
description: 把微信公众号文章链接转成可结构化投研素材并沉淀到 JSON 数据库的工作流技能（v2.0 - 按日期分片存储）。内置《全部个股.xls》和《数据结构规范_v2》，支持 Docker 部署和 Celery 队列。适用场景：你给出一个或多个 mp.weixin.qq.com 链接，需要（1）可靠读取公众号正文并落盘 raw_material；（2）从 raw_material 识别提到的个股（自动映射内置 stock list）；（3）按内置《数据结构规范_v2》抽取 accidents/insights/key_metrics/target_valuation；（4）**增量合并到按日期分片的 JSON 文件**（解决大文件问题）；（5）可选同步到 Firestore/GitHub 分片。
---

# wechat-fetch-research-embedded (v2.0)

## 快速开始（推荐工作流）

**输入**：微信公众号文章 URL（单篇或多篇）

**输出**：
- `raw_material/raw_material_YYYY-MM-DD.md`（原始正文沉淀）
- `data/stocks_master_YYYY-MM-DD.json`（当日抽取结果，中间产物）
- **`data/master/stocks/YYYY-MM-DD.json`**（按日期分片存储，新增！）
- **`data/master/stocks_index.json`**（全局索引，新增！）
- （可选）同步到 Firebase Firestore
- （可选）同步到 GitHub（分片模式或单文件模式）
- （可选）同步到 **Cloudflare R2**（raw_material 云端存储）

> 数据结构以 `references/数据结构规范_v2.md` 为准。

## Complete Workflow: 生成 → 保存 → 推送 → 上线

### 步骤 1: 生成数据

#### 方式 A: 统一 Pipeline（推荐）

单条命令完成全流程：

```powershell
cd e:/github/stock-research-backup
python scripts/pipeline.py `
  --url "https://mp.weixin.qq.com/s/..." `
  --sync-firestore `
  --sync-github
```

这会自动执行：
1. 抓取公众号文章正文
2. 保存到 `raw_material/raw_material_YYYY-MM-DD.md`
3. 抽取个股结构化信息
4. 增量合并到日期分片
5. （可选）同步到 Firestore
6. （可选）同步到 GitHub

#### 方式 B: 分步执行

**Step 1.1: 抓取正文**
```powershell
python scripts/fetch_wechat_via_browser_dom.py `
  --url "https://mp.weixin.qq.com/s/..." `
  --out_text "tmp_article.txt" `
  --user_data_dir ".browser_profile"
```

**Step 1.2: 转换为 raw_material 格式**
```powershell
python scripts/fetch_wechat_to_raw_material.py `
  --url "https://mp.weixin.qq.com/s/..." `
  --out "raw_material/raw_material_2026-04-21.md" `
  --manual_text_file "tmp_article.txt"
```

**Step 2: 抽取个股信息**
```powershell
python scripts/extract_stocks_from_raw_material.py `
  --raw "raw_material/raw_material_2026-04-21.md" `
  --stock_xls "./assets/全部个股.xls" `
  --out_json "data/stocks_master_2026-04-21.json" `
  --mode merge
```

**Step 2.5: 增量合并到分片**
```powershell
python scripts/incremental_update.py `
  --mode merge `
  --json "data/stocks_master_2026-04-21.json"
```

### 步骤 2: 保存到本地

数据会自动保存到以下位置：

```
e:/github/stock-research-backup/
├── raw_material/
│   └── raw_material_2026-04-21.md
└── data/
    ├── stocks_master_2026-04-21.json (中间产物)
    └── master/
        ├── stocks_index.json
        └── stocks/
            └── 2026-04-21.json (分片文件)
```

**分片文件格式：**
```json
{
  "date": "2026-04-21",
  "update_count": 15,
  "stocks": {
    "688227": { "name": "品高股份", "articles": [...], ... },
    "300593": { "name": "新雷能", ... }
  }
}
```

### 步骤 3: 推送到 GitHub

#### 方式 A: 自动推送（推荐）

在运行 pipeline 时添加 `--sync-github` 参数：

```powershell
python scripts/pipeline.py `
  --url "https://mp.weixin.qq.com/s/..." `
  --sync-github
```

这会自动：
1. 复制分片文件到 `agent_store`
2. 执行 git add
3. 执行 git commit
4. 执行 git push github HEAD:main -f

#### 方式 B: 手动推送

```powershell
# 1. 复制文件到 agent_store
cd e:/github/stock-research-backup
python scripts/sync_to_github.py --mode shard --base-dir "data/master"

# 2. 或者手动 git 操作
cd e:/github/agent_store
git status
git add data/master/stocks/2026-04-21.json data/master/stocks_index.json
git commit -m "Update stock data: 2026-04-21 (+15 stocks)"
git push github HEAD:main -f
```

### 步骤 4: 上线（Vercel 自动部署）

推送后，Vercel 会自动：
1. 检测到 GitHub 仓库更新
2. 触发自动构建和部署
3. 更新线上数据

**验证部署：**
- 访问 https://vercel.com/dashboard
- 查看部署状态
- 访问线上网站验证数据已更新

**检查线上数据：**
```powershell
# 检查 GitHub 仓库
# 访问 https://github.com/treeie2/stock-research/blob/main/data/master/stocks_index.json

# 检查 Vercel 部署日志
# 访问 https://vercel.com/dashboard

# 验证线上 API
# 访问 https://your-vercel-domain.vercel.app/api/stocks
```

## 完整流程示例

### 示例 1: 单篇文章处理

```powershell
# 一条命令完成全流程
python scripts/pipeline.py `
  --url "https://mp.weixin.qq.com/s/abc123" `
  --sync-github

# 输出：
# [Pipeline] Step 1: Fetching article...
# [Pipeline] ✅ Article fetched
# [Pipeline] Step 2: Extracting stocks...
# [Pipeline] ✅ Found 15 stocks
# [Pipeline] Step 2.5: Incremental merge to shards...
# [Pipeline] ✅ +15 new stocks
# [Pipeline] Step 3: Syncing to GitHub...
# [Pipeline] ✅ Pushed to GitHub
#
# ✅ 全部完成!
# Vercel 会自动重新部署
```

### 示例 2: 多篇文章批量处理

```powershell
# 创建批处理脚本
$urls = @(
  "https://mp.weixin.qq.com/s/abc123",
  "https://mp.weixin.qq.com/s/def456",
  "https://mp.weixin.qq.com/s/ghi789"
)

foreach ($url in $urls) {
  python scripts/pipeline.py --url $url --sync-github
}

# 最后统一推送（可选）
python scripts/sync_to_github.py --mode shard --base-dir "data/master" --days 1
```

## v2.0 核心变更：按日期分片存储

### 为什么需要分片？

旧版将所有股票存储在单一 `stocks_master.json` 中，随着数据积累：
- 文件越来越大（3000+ 股票时可达数 MB）
- 每次同步需要传输整个文件
- 重复运行可能导致文章重复添加

### 新架构

```
data/master/
├── stocks_index.json           # 索引文件（股票代码 → 最后更新日期）
├── stocks_master.json          # 主文件（可选完整备份）
└── stocks/
    ├── 2026-04-17.json        # 当日更新
    ├── 2026-04-16.json        # 昨日更新
    └── ...                     # 历史分片
```

### 分片文件格式

```json
{
  "date": "2026-04-17",
  "update_count": 15,
  "stocks": {
    "688227": { "name": "品高股份", "articles": [...], ... },
    "300593": { "name": "新雷能", ... }
  }
}
```

## 部署方式

### 方式一：Docker Compose（推荐，适合服务器部署）

```bash
cp .env.example .env
docker-compose up -d
docker-compose run --rm wechat-fetch \
  python scripts/pipeline.py \
  --url "https://mp.weixin.qq.com/s/..." \
  --sync-github
```

详见 [DEPLOY.md](DEPLOY.md)

### 方式二：统一 Pipeline（推荐，单条命令完成全流程）

```bash
# 默认使用分片存储 (v2.0)
python scripts/pipeline.py \
  --url "https://mp.weixin.qq.com/s/..." \
  --sync-firestore \
  --sync-github
```

### 方式三：分步执行（传统方式）

见下方详细步骤。

## Step 1：抓取公众号正文 → 写入 raw_material

公众号经常出现"环境异常/去验证/反爬"，导致 **直接 HTTP 抓取失败或拿不到全文**。本技能提供两种方式：

### 方式 A：外部 Reader（可选）
如果你有可用的 link reader / 代理 / 可访问环境（例如 MCP reader），可直接把正文喂给落盘脚本：

- `python scripts/fetch_wechat_to_raw_material.py --url "<mp_url>" --out "raw_material/raw_material_2026-04-03.md" --mcp_server <server_name> --mcp_tool <tool_name>`

### 方式 B：浏览器登录态抓取（推荐，最稳）
本技能内置 **Playwright 浏览器 DOM 抽取**，不尝试绕过微信安全机制；如遇"去验证/登录"，你需要在弹出的真实浏览器里手动完成一次验证。

1) 先用浏览器抓取正文到临时文件：
- `python scripts/fetch_wechat_via_browser_dom.py --url "<mp_url>" --out_text "tmp_article.txt" --user_data_dir ".browser_profile" --timeout 300`

2) 再把临时正文落盘为 raw_material：
- `python scripts/fetch_wechat_to_raw_material.py --url "<mp_url>" --out "raw_material/raw_material_2026-04-03.md" --manual_text_file "tmp_article.txt"`

> 说明：`--manual_text_file` 模式等价于"外部 reader 已经拿到正文"，脚本负责 **统一 raw_material 结构**（source/fetched_at/title/date + content）。

## Step 2：从 raw_material 抽取个股结构化信息 → 写入 JSON

- `python scripts/extract_stocks_from_raw_material.py \
  --raw "raw_material/raw_material_2026-04-03.md" \
  --stock_xls "./assets/全部个股.xls" \
  --out_json "data/stocks_master_2026-04-03.json" \
  --mode merge`

> 本 skill **已内置** `assets/全部个股.xls` 与 `references/数据结构规范_v2.md`。

## Step 2.5（NEW）：增量合并到按日期分片 ✨

将 Step 2 的抽取结果 **增量合并** 到按日期分片的存储中：

```bash
python scripts/incremental_update.py \
  --mode merge \
  --json "data/stocks_master_2026-04-17.json"
```

**自动完成：**
1. 将当天更新的股票写入 `data/master/stocks/2026-04-17.json`
2. 更新索引文件 `data/master/stocks_index.json`
3. **智能去重**：
   - 文章按 `(source, title)` 去重
   - `core_business`, `industry_position`, `chain`, `partners` 等 set 字段自动合并
   - 同一股票同一天只保留最新版本
4. 累加 `mention_count`

**其他增量操作：**
```bash
# 更新单只股票
python scripts/incremental_update.py \
  --mode single \
  --stock-code "688227" \
  --stock-data '{"name":"品高股份","core_business":["..."],"articles":[]}'

# 重建索引（从现有分片）
python scripts/incremental_update.py --mode rebuild-index

# 从分片构建主文件备份
python scripts/incremental_update.py --mode build-master
```

## Step 3（可选）：同步 JSON 到 Firebase Firestore

本增强版的 `sync_to_firestore.py` 会同时维护：
- 子集合：`stocks/{code}/articles/{article_id}`（完整文章）
- 父文档数组：`stocks/{code}.articles[]`（文章摘要，用于快速列表）

## Step 4（可选）：同步到 GitHub ✨ 已升级

### 推荐模式：分片同步（v2.0 默认）

```bash
python scripts/sync_to_github.py \
  --mode shard \
  --base-dir "data/master" \
  --github-token "$GITHUB_TOKEN"
```

**同步内容：**
- `data/master/stocks/YYYY-MM-DD.json`（当天分片）
- `data/master/stocks_index.json`（索引文件）

**优势：**
- 只上传当天变更，大幅减少传输量
- 避免大文件 API 限制问题
- 支持多天批量同步：`--days 3`

### 兼容模式：单文件同步（旧版）

```bash
python scripts/sync_to_github.py \
  --mode single \
  --json "data/stocks_master_2026-04-17.json" \
  --github-token "$GITHUB_TOKEN"
```

### 全量模式

```bash
python scripts/sync_to_github.py \
  --mode full \
  --github-token "$GITHUB_TOKEN"
```

> 安全建议：不要把 token 写进 skill 或仓库，推荐用环境变量 `GITHUB_TOKEN`。

## 目录约定

建议在项目根目录使用如下结构：

```
├── raw_material/                    # 原始文章正文沉淀（Markdown）
│   └── raw_material_YYYY-MM-DD.md
├── data/
│   ├── stocks_master_YYYY-MM-DD.json # 当日抽取结果（中间产物）
│   └── master/                      # 分片存储（核心输出）
│       ├── stocks_index.json        # 全局索引
│       ├── stocks_master.json       # 完整备份（可选）
│       └── stocks/                  # 按日期分片
│           ├── 2026-04-17.json
│           └── ...
├── assets/
│   └── 全部个股.xls                 # 内置股票列表
└── references/
    └── 数据结构规范_v2.md            # 数据结构定义
```

## 关键资源

### 数据结构规范
- `references/数据结构规范_v2.md`

### 脚本清单

| 脚本 | 功能 | 版本 |
|------|------|------|
| `scripts/pipeline.py` | **统一 Pipeline**（集成全流程 + 自动分片） | v2.0 |
| `scripts/incremental_update.py` | **增量合并到分片**（核心新功能） | NEW |
| `scripts/sync_to_github.py` | **GitHub 同步**（支持分片+单文件） | v2.0 |
| `scripts/fetch_wechat_to_raw_material.py` | 正文落盘为 raw_material | v1.x |
| `scripts/fetch_wechat_via_browser_dom.py` | 浏览器 DOM 抽取全文 | v1.x |
| `scripts/extract_stocks_from_raw_material.py` | LLM 抽取个股信息 | v1.x |
| `scripts/sync_to_firestore.py` | 同步到 Firestore | v1.x |

## Pipeline 完整流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    pipeline.py (v2.0)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  URL ──→ [Step 1] 浏览器抓取 ──→ raw_material/*.md         │
│                    │                                       │
│                    ▼                                       │
│             [Step 2] LLM 抽取 ──→ stocks_master_*.json      │
│                    │                                       │
│                    ▼                                       │
│        [Step 2.5] ⭐ 增量合并到分片                         │
│              │         │                                   │
│              ▼         ▼                                   │
│     stocks/2026-04-17.json   stocks_index.json             │
│              │                                             │
│              ├─→ [Step 3] Firestore (可选)                │
│              │                                             │
│              └─→ [Step 4] GitHub 分片同步 (可选)           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 常见坑（务必看）

1. **公众号"去验证"**：遇到验证页时，需要在浏览器里人工点一下，验证通过后再抽正文。
2. **公众号反爬**：直接抓 HTML 常失败或内容不全；优先用"浏览器 DOM 提取正文"兜底。
3. **股票简称歧义**：抽取到的简称可能是同名词/简称重叠；脚本会尽量映射到《全部个股.xls》，无法映射则不入库。
4. **文章去重**：v2.0 的增量合并已实现按 `(source, title)` 双键去重，重复运行不会产生重复文章。
5. **set 字段合并**：`core_business`, `industry_position`, `chain`, `partners` 使用 set 合并，不会重复。
6. **mention_count 累加**：每次更新会累加 mention_count，如需重置请手动编辑。
7. **旧版兼容**：使用 `--no-shards` 参数可回退到单文件模式。

## Firestore 同步详情

### 前置条件
- 需要 **Firebase Admin Service Account** JSON（私钥文件），不要用前端 `apiKey`。
- 出于安全原因，**不建议把私钥嵌进 skill**。推荐放在安全路径。

### 数据模型
- 股票文档：`stocks/{stock_code}`（只写入股票基础字段 + 计数）
- 文章子集合：`stocks/{stock_code}/articles/{article_id}`
  - `article_id = sha1(source)`（天然去重）

### 同步命令
```bash
python scripts/sync_to_firestore.py \
  --credentials "/path/to/firebase-credentials.json" \
  --json "data/stocks_master_2026-04-17.json" \
  --collection "stocks" \
  --article_subcollection "articles" \
  --on_exists skip
```

### 同步规则
- **不再把 articles 数组写回 stocks 文档**（避免整文档写回）
- 每篇文章单独写入子集合 doc（按 source 哈希去重）
- 仅当新文章写入成功时，使用事务对 `stocks/{code}` 的 `article_count`/`mention_count` 做 `Increment(1)`
- 已存在文章默认 `skip`（你也可以用 `--on_exists update` 更新内容）

## Step 5（可选）：同步 raw_material 到 Cloudflare R2 ✨

### 为什么用 R2？

- **10GB 免费存储**（比 S3 大方）
- **无出口流量费**（下载免费）
- **S3 兼容 API**（boto3 直接用）
- **国内访问速度快**

### 配置步骤

1. **创建 R2 Bucket**
   - 访问 https://dash.cloudflare.com/ → R2
   - 创建 bucket: `stock-research`

2. **创建 API Token**
   - R2 → Manage R2 API Tokens → Create API Token
   - 权限: `Object Read & Write`
   - 复制 `Access Key ID` 和 `Secret Access Key`

3. **配置环境变量**（添加到 `.env`）
   ```bash
   R2_ACCOUNT_ID=your_account_id
   R2_ACCESS_KEY_ID=your_access_key
   R2_SECRET_ACCESS_KEY=your_secret_key
   R2_BUCKET_NAME=stock-research
   ```

### 使用方式

```bash
# 上传单个文件
python scripts/sync_to_r2.py \
  --mode upload \
  --file "raw_material/raw_material_2026-04-17.md"

# 增量同步本地 raw_material 到 R2 (推荐日常使用)
python scripts/sync_to_r2.py \
  --mode sync-up \
  --dir "raw_material"

# 从 R2 同步到本地 (龙虾端使用)
python scripts/sync_to_r2.py \
  --mode sync-down \
  --dir "raw_material"

# 列出所有文件
python scripts/sync_to_r2.py --mode list

# 获取文件公开 URL (7天有效)
python scripts/sync_to_r2.py \
  --mode url \
  --key "raw_material/raw_material_2026-04-17.md"
```

### 在 Pipeline 中自动同步

可以在 `pipeline.py` 抓取完成后自动上传 raw_material 到 R2：

```python
# 在 Step 1 完成后添加
from scripts.sync_to_r2 import R2Syncer

syncer = R2Syncer()
syncer.upload_file(str(raw_material_file))
```

### Docker 方式运行（解决 Windows Python 3.14 SSL 问题）

如果在 Windows 上遇到 `SSLV3_ALERT_HANDSHAKE_FAILURE` 错误，可以使用 Docker：

```bash
# 构建镜像
docker build -f Dockerfile.r2 -t stock-research-r2 .

# 列出 R2 文件
docker run --rm -v "${PWD}/raw_material:/app/raw_material" stock-research-r2 --mode list

# 同步本地到 R2
docker run --rm -v "${PWD}/raw_material:/app/raw_material" stock-research-r2 --mode sync-up --dir /app/raw_material

# 同步 R2 到本地
docker run --rm -v "${PWD}/raw_material:/app/raw_material" stock-research-r2 --mode sync-down --dir /app/raw_material
```

或使用 docker-compose：

```bash
# 列出文件
docker-compose -f docker-compose.r2.yml run --rm r2-list

# 同步本地到 R2
docker-compose -f docker-compose.r2.yml run --rm r2-sync-up

# 同步 R2 到本地
docker-compose -f docker-compose.r2.yml run --rm r2-sync-down
```

### 完整同步流程（IDE → R2 → 龙虾）

#### 场景 1：IDE 端抓取文章后同步到 R2

```bash
# 1. 抓取文章（生成 raw_material）
python scripts/pipeline.py --url "https://mp.weixin.qq.com/s/xxx"

# 2. 同步 raw_material 到 R2（Docker 方式）
docker-compose -f docker-compose.r2.yml run --rm r2-sync-up

# 或者同步单个文件
docker run --rm -v "${PWD}/raw_material:/app/raw_material" \
  stock-research-r2 --mode upload \
  --file "/app/raw_material/raw_material_2026-04-17.md"
```

#### 场景 2：龙虾端从 R2 同步到本地

```bash
# 在龙虾机器上执行
# 1. 从 R2 同步 raw_material 到本地
docker-compose -f docker-compose.r2.yml run --rm r2-sync-down

# 2. 运行后续处理流程
python scripts/extract_stocks_from_raw_material.py \
  --input "raw_material/raw_material_2026-04-17.md"
```

#### 场景 3：Pipeline 中自动同步

修改 `pipeline.py`，在抓取完成后自动上传：

```python
# 在 Step 1 完成后添加 R2 同步
print(f"[Pipeline] Step 1.5: 同步 raw_material 到 R2")
try:
    from scripts.sync_to_r2 import R2Syncer
    syncer = R2Syncer()
    syncer.upload_file(str(raw_material_file))
    result["r2_uploaded"] = True
    print(f"[Pipeline] ✅ 已同步到 R2: {raw_material_file.name}")
except Exception as e:
    print(f"[Pipeline] ⚠️ R2 同步失败: {e}")
    result["r2_uploaded"] = False
```

### 常见问题

**Q: Windows 上遇到 SSL 错误怎么办？**
A: 使用 Docker 方式运行，已配置 `verify_ssl: false` 绕过证书验证。

**Q: R2 和 GitHub 同步有什么区别？**
A: 
- R2：适合存储大文件（raw_material），有 10GB 免费额度，下载免费
- GitHub：适合存储结构化数据（stocks JSON），有版本控制，但 raw_material 太大会占用仓库空间

**Q: 如何验证 R2 连接是否正常？**
A: 运行 `docker-compose -f docker-compose.r2.yml run --rm r2-list`，如果能看到文件列表（即使没有文件），说明连接成功。

## 抽取规则（核心点）

- **先识别个股**：从 raw_material 中抽取"候选个股名/代码" → 映射到《全部个股.xls》（代码+简称）。
- **再按文章维度抽字段**：对每篇文章、每只股票，抽取：
  - `accidents`：事件/催化剂/行业新闻（短句，超 60 字需压缩）
  - `insights`：投研观点/逻辑
  - `key_metrics`：量化指标/市占率/财务/产能等
  - `target_valuation`：估值/目标市值/空间/测算
- **结构化输出**：组织成 `stocks[].articles[]`，并按 `source`（URL）去重追加。