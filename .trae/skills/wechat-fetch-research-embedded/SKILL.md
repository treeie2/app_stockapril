---
name: wechat-fetch-research-embedded
description: 把微信公众号文章链接转成可结构化投研素材并沉淀到 JSON 数据库的工作流技能（v2.3）。内置《全部个股.xls》和《数据结构规范_v2》，支持 Docker 部署和 Celery 队列。适用场景：你给出一个或多个 mp.weixin.qq.com 链接，需要（1）可靠读取公众号正文并落盘 raw_material；（2）从 raw_material 识别提到的个股（自动映射内置 stock list）；（3）按内置《数据结构规范_v2》抽取 accidents/insights/key_metrics/target_valuation；（4）**增量合并到按日期分片的 JSON 文件**（解决大文件问题）；（5）可选同步到 Firestore/GitHub 分片。
---

# wechat-fetch-research-embedded (v2.3)

> ⚠️ **重要路径说明**：本技能输出到 `data/stocks/` 目录（前端读取），**不是** `data/master/`。详见下方目录约定。

## 快速开始（推荐工作流）

**输入**：微信公众号文章 URL（单篇或多篇）

**输出**：
- `raw_material/raw_material_YYYY-MM-DD.md`（原始正文沉淀）
- `data/stocks_master_YYYY-MM-DD.json`（当日抽取结果，中间产物）
- **`data/stocks/YYYY-MM-DD.json`**（按日期分片存储）
- **`data/stocks/stocks_index.json`**（全局索引）
- **`data/stocks/stocks_master.json`**（主数据文件，前端读取）
- （可选）同步到 Firebase Firestore
- （可选）同步到 GitHub

> 数据结构以 `references/数据结构规范_v2.md` 为准。

---

## v2.3 变更说明

### 修复：数据合并流程
- **问题**: `incremental_update.py` 将数据写入 skill 内部目录（`.trae/skills/.../data/master/`），前端不读取该路径，导致新数据不显示
- **修复**: 新增 `scripts/merge_new_stocks.py` 作为标准合并工具
- **流程变更**: Step 2.5 改为使用 `merge_new_stocks.py`，自动合并到 `data/stocks/stocks_master.json` 和分片文件
- **中间产物**: 提取结果输出到 `data/stocks_master_YYYY-MM-DD.json`

### v2.2 变更说明
- **新增字段**: `core_business`、`industry_position`、`chain`、`partners`
- **新增工具**: `process_article.py` 整合全流程（自动映射行业/概念）
- **简化**: AI 只需提取结构化数据，股票代码/行业/概念自动从映射文件获取

---

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

**Step 2.5: 合并到主数据（关键步骤！）**
```powershell
python scripts/merge_new_stocks.py
```

该脚本会自动：
1. 读取 `data/stocks_master_YYYY-MM-DD.json`（Step 2 的输出）
2. 按 `source` 去重合并到 `data/stocks/stocks_master.json`
3. 同步更新 `data/stocks/YYYY-MM-DD.json` 分片文件
4. 累加 `mention_count`

> ⚠️ **注意**：`incremental_update.py`（旧版脚本）将数据写入 `.trae/skills/.../data/master/` 目录，**前端不读取该路径**。必须运行 `merge_new_stocks.py` 才能让前端看到新数据。

### 步骤 2: 保存到本地

数据会自动保存到以下位置：

```
e:/github/stock-research-backup/
├── raw_material/
│   └── raw_material_2026-04-21.md
└── data/
    ├── stocks_master_2026-04-21.json (中间产物)
    └── stocks/
        ├── stocks_index.json (全局索引)
        ├── stocks_master.json (主数据，前端读取)
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

#### 方式 B: 手动推送

```powershell
cd e:/github/stock-research-backup
git add data/stocks/stocks_master.json data/stocks/2026-04-21.json data/stocks/stocks_index.json
git commit -m "Update stock data: 2026-04-21 (+15 stocks)"
git push origin main
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

---

## v2.0 核心变更：按日期分片存储

### 为什么需要分片？

旧版将所有股票存储在单一 `stocks_master.json` 中，随着数据积累：
- 文件越来越大（3000+ 股票时可达数 MB）
- 每次同步需要传输整个文件
- 重复运行可能导致文章重复添加

### 新架构

```
data/stocks/
├── stocks_index.json           # 索引文件（股票代码 → 最后更新日期）
├── stocks_master.json          # 主文件（前端读取）
└── 2026-04-17.json            # 当日更新
    ️ ...                       # 历史分片
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

---

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
python scripts/pipeline.py \
  --url "https://mp.weixin.qq.com/s/..." \
  --sync-firestore \
  --sync-github
```

### 方式三：分步执行

见下方详细步骤。

---

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

---

## Step 2：从 raw_material 抽取个股结构化信息 → 写入 JSON

### 方式 A: LLM 管道提取

```bash
python scripts/extract_stocks_from_raw_material.py \
  --raw "raw_material/raw_material_2026-04-03.md" \
  --stock_xls "./assets/全部个股.xls" \
  --out_json "data/stocks_master_2026-04-03.json" \
  --mode merge
```

> 本 skill **已内置** `assets/全部个股.xls` 与 `references/数据结构规范_v2.md`。

### 方式 B: AI 辅助提取（推荐）

AI 从文章内容提取以下 **8 个字段**：

**结构化数据字段**：
| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `accidents` | string[] | 事件/催化剂，事实性描述 | `["二季度订单加速放量"]` |
| `insights` | string[] | 投研观点，原文或忠实改写 | `["国产交换芯片龙头"]` |
| `key_metrics` | string[] | 关键指标，数字/比率/市占率 | `["2026年AEC收入10-15亿元"]` |
| `target_valuation` | string[] | 目标估值/目标价 | `["370亿"]` |

**个股数据字段**（从文章上下文推断）：
| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `core_business` | string[] | 核心业务/主要产品 | `["交换芯片研发与销售"]` |
| `industry_position` | string[] | 行业地位/竞争优势 | `["国产交换芯片龙头"]` |
| `chain` | string[] | 产业链位置 | `["中游-芯片设计"]` |
| `partners` | string[] | 合作伙伴公司名称 | `["阿里巴巴", "字节跳动"]` |

然后调用 `process_article.py` 自动完成行业/概念映射和合并。

---

## Step 2.5（关键步骤）：合并到主数据

将 Step 2 的抽取结果 **合并** 到前端读取的主数据文件：

```bash
python scripts/merge_new_stocks.py
```

**自动完成：**
1. 读取 `data/stocks_master_YYYY-MM-DD.json`（Step 2 的输出）
2. 按 `source` 去重合并到 `data/stocks/stocks_master.json`
3. 同步更新 `data/stocks/YYYY-MM-DD.json` 分片文件
4. 累加 `mention_count`

**智能去重**：
- 文章按 `(source, title)` 去重
- `core_business`, `industry_position`, `chain`, `partners` 等 set 字段自动合并
- 同一股票同一天只保留最新版本

> ⚠️ **重要**：`incremental_update.py`（旧版）写入 `.trae/skills/.../data/master/` 目录，前端不读取。**必须使用 `merge_new_stocks.py`**。

---

## Step 3（可选）：同步 JSON 到 Firebase Firestore

```bash
python sync_to_firebase.py \
  --credentials ".trae/rules/firebase-credentials.json" \
  --json "data/stocks/stocks_master.json" \
  --on_exists merge
```

### 数据模型
- 股票文档：`stocks/{stock_code}`（只写入股票基础字段 + 计数）
- 文章子集合：`stocks/{stock_code}/articles/{article_id}`
  - `article_id = sha1(source)`（天然去重）

### 同步规则
- 不再把 articles 数组写回 stocks 文档
- 每篇文章单独写入子集合 doc（按 source 哈希去重）
- 仅当新文章写入成功时，使用事务对 `stocks/{code}` 的 `article_count`/`mention_count` 做 `Increment(1)`
- 已存在文章默认 `skip`（也可用 `--on_exists update` 更新内容）

---

## Step 4（可选）：同步到 GitHub

### 推荐方式：手动 git 操作

```bash
cd e:/github/stock-research-backup
git add data/stocks/stocks_master.json data/stocks/YYYY-MM-DD.json data/stocks/stocks_index.json
git commit -m "feat: 添加 YYYY-MM-DD 数据（N只股票）"
git push origin main
```

### 自动方式：pipeline 集成

```bash
python scripts/pipeline.py \
  --url "https://mp.weixin.qq.com/s/..." \
  --sync-github
```

---

## 目录约定

```
├── raw_material/                    # 原始文章正文沉淀（Markdown）
│   └── raw_material_YYYY-MM-DD.md
├── data/
│   ├── stocks_master_YYYY-MM-DD.json # 当日抽取结果（中间产物）
│   └── stocks/                      # 分片存储（核心输出，前端读取）
│       ├── stocks_index.json        # 全局索引
│       ├── stocks_master.json       # 主数据文件
│       ├── 2026-04-17.json          # 按日期分片
│       └── ...
├── assets/
│   └── 全部个股.xls                 # 内置股票列表
├── archived/
│   ├── 同花顺行业.xls               # 行业映射
│   └── 所属概念.xls                 # 概念映射
└── references/
    └── 数据结构规范_v2.md            # 数据结构定义
```

---

## 脚本清单

| 脚本 | 功能 | 版本 |
|------|------|------|
| `scripts/pipeline.py` | **统一 Pipeline**（集成全流程） | v2.0 |
| `scripts/merge_new_stocks.py` | **⭐ 合并到主数据**（推荐，前端可见） | v2.3 NEW |
| `scripts/incremental_update.py` | **旧版合并**（写入 skill 内部目录，前端不可见） | v2.0 |
| `scripts/process_article.py` | **AI 辅助全流程**（提取+映射+合并） | v2.2 |
| `scripts/map_industry_concept.py` | **批量更新行业/概念**（从同花顺映射） | v2.2 |
| `scripts/sync_to_github.py` | **GitHub 同步** | v2.0 |
| `scripts/fetch_wechat_to_raw_material.py` | 正文落盘为 raw_material | v1.x |
| `scripts/fetch_wechat_via_browser_dom.py` | 浏览器 DOM 抽取全文 | v1.x |
| `scripts/extract_stocks_from_raw_material.py` | LLM 抽取个股信息 | v1.x |
| `scripts/sync_to_firestore.py` | 同步到 Firestore | v1.x |
| `scripts/sync_to_r2.py` | 同步到 Cloudflare R2 | v1.x |

---

## Pipeline 完整流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    pipeline.py (v2.0)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  URL ──→ [Step 1] 浏览器抓取 ──→ raw_material/*.md         │
│                    │                                       │
│                    ▼                                       │
│             [Step 2] LLM/AI 抽取 ──→ stocks_master_*.json   │
│                    │                                       │
│                    ▼                                       │
│   [Step 2.5] ⭐ merge_new_stocks.py（关键步骤！）          │
│              │         │                                   │
│              ▼         ▼                                   │
│   data/stocks/stocks_master.json   data/stocks/YYYY-MM-DD   │
│              │                                             │
│              ├─→ [Step 3] Firestore (可选)                │
│              │                                             │
│              └─→ [Step 4] GitHub push (可选)              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 常见坑（务必看）

1. **公众号"去验证"**：遇到验证页时，需要在浏览器里人工点一下，验证通过后再抽正文。
2. **公众号反爬**：直接抓 HTML 常失败或内容不全；优先用"浏览器 DOM 提取正文"兜底。
3. **股票简称歧义**：抽取到的简称可能是同名词/简称重叠；脚本会尽量映射到《全部个股.xls》，无法映射则不入库。
4. **文章去重**：`merge_new_stocks.py` 已实现按 `(source, title)` 双键去重，重复运行不会产生重复文章。
5. **set 字段合并**：`core_business`, `industry_position`, `chain`, `partners` 使用 set 合并，不会重复。
6. **mention_count 累加**：每次更新会累加 mention_count，如需重置请手动编辑。
7. **⭐ 路径问题**：`incremental_update.py` 写入 `.trae/skills/.../data/master/`，**前端不读取**。务必使用 `merge_new_stocks.py`。
8. **行业字段**：`industry` 必须使用三级分类（如"电子-半导体-集成电路"），禁止使用"创业板/科创板"等板块名。

---

## 抽取规则（核心点）

- **先识别个股**：从 raw_material 中抽取"候选个股名/代码" → 映射到《全部个股.xls》（代码+简称）。
- **再按文章维度抽字段**：对每篇文章、每只股票，抽取：
  - `accidents`：事件/催化剂/行业新闻（短句，超 60 字需压缩）
  - `insights`：投研观点/逻辑
  - `key_metrics`：量化指标/市占率/财务/产能等
  - `target_valuation`：估值/目标市值/空间/测算
  - `core_business`：核心业务/主要产品
  - `industry_position`：行业地位/竞争优势
  - `chain`：产业链位置
  - `partners`：合作伙伴
- **结构化输出**：组织成 `stocks[].articles[]`，并按 `source`（URL）去重追加。