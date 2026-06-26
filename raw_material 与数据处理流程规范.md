# Raw Material 与数据处理流程规范

**版本**: v3.1
**更新日期**: 2026-06-26
**适用**: 微信文章→原始素材→结构化数据全流程（5 维度标准 + 轻量模式 + 数据分层）

---

## 🆕 v3.1 变更说明（2026-06-26）

### 数据架构简化 + Firebase 移除
- **移除 Firebase 同步链路**：不再维护 Firestore 数据库
- **三层部署**: GitHub（版本控制）→ Supabase（云端数据库）→ ModelScope（Web 展示）
- **主页三 Tab**: 仪表盘 + 分组（跳转 /groups）+ 突破信号（lyt 老鸭头）
- **行业/概念补齐**: 从同花顺 xls 批量补齐，行业覆盖率 99.7%
- **stocks_meta.json 重建**: 包含 industry/concepts 等全部非 articles 字段

## 🆕 v3.0 变更说明（2026-06-26）

### 数据分层架构 + lyt 突破信号
- **stocks_master.json 保持不变**：唯一写入源，管线不受影响
- **新增 stocks_meta.json**（2.8MB）：不含 articles，Flask 启动快 3x
- **新增 stocks_articles.json**：articles 分离，详情页按需加载
- **build_derivatives.py**：从 master 生成 meta + articles + gz
- **ModelScope 部署**：https://modelscope.cn/studios/TREEIE/aastock
- **三 Tab 首页**：仪表盘 + 分组 + 突破信号（lyt 老鸭头）

## 🆕 v2.9 变更说明（2026-06-21）

### json.gz 自动生成 + Supabase 同步
- **merge_new_stocks.py** 保存主文件时自动生成 `stocks_master.json.gz`
- **Supabase 替代 Firebase**：`sync_to_supabase.py` 全量/增量同步
- **日期格式强制 YYYY-MM-DD**：`normalize_dates.py` 检查和修复

## 🆕 v2.7 变更说明（2026-06-19）

### 本地股票扫描 + 上下文提取
- **`local_scan_stock_names()`**：0 API 调用识别文章中的股票
- **`_extract_context_for_stocks()`**：长文只传相关段落（6000→500字）
- **移除 BROAD_LIST 标题过滤**：不再按标题整篇拒绝
- **`__THIN__` 三道防线**：逐股判断质量

## 🆕 v2.5 变更说明（2026-06-13）

### 核心变更：5 维度抽取标准 + 轻量模式

参考 `references/数据结构规范_v2.md`（v2.4）。

**1. 新增 `industry_background` 字段（第 5 维度）**
- 行业/赛道宏观背景，与个股 4 维度并列
- 严禁出现公司名称；同赛道股票内容一致
- 存量文章自动补齐 `[]`

**2. 严格字段约束**
| 字段 | 约束 |
|------|------|
| `industry_background` | 严禁公司名 |
| `accidents` | 单条 ≤60 字，严禁"预计/有望"等主观词 |
| `key_metrics` | 每条**必须含阿拉伯数字**，纯定性丢弃 |
| `target_valuation` | 必须含亿/元/PE/PB 等估值词 + 数字 |

**3. 轻量模式：不浪费第一层信息**
- 个股未通过投研质量过滤时，不写 article
- 但 `products`/`core_business`/`industry_position`/`chain`/`partners` 静默合并
- `mention_count` 不变，避免低质量数据污染

**4. 前端同步更新**
- `stock_detail.html` 新增 🌐 行业/赛道背景显示区
- `main.py` API 支持 `industry_background` 字段编辑

---

## 🆕 v2.4 变更说明（2026-06-05）

### 新增：离线 HTML 研报批量处理流程
- **背景**: value/ 和 topdown/ 目录存有批量离线下载的 HTML 深度研报
- **工具**: `process_html_value.py` / `process_topdown.py` 用 BeautifulSoup 解析 HTML
- **优势**: 纯文本干净提取，无需 LLM API
- **流程**: HTML → raw_material_formatted/ → value_YYYY-MM-DD.json → stocks_master.json

### 新增：第一层字段自动补齐
- **工具**: `extract_first_layer.py` 从 raw_material 文章提取 products/core_business/industry_position/chain/partners
- **覆盖**: products(100%), core_business(94%), industry_position(92%), chain(88%), partners(55%)
- **工具**: `fill_stock_info.py` 从同花顺 Excel 补齐行业和概念

### 数据清理
- 删除 819 篇空文章（仅有链接无有效提取数据）
- 个股总数: 3313 只，其中有文章: 1957 只

### 修复：数据合并流程
- **问题**: `incremental_update.py` 将数据写入 skill 内部目录（`.trae/skills/.../data/master/`），前端不读取该路径，导致新数据不显示
- **修复**: 新增 `scripts/merge_new_stocks.py` 作为标准合并工具
- **流程变更**: Step 3 改为使用 `merge_new_stocks.py`，自动合并到 `data/stocks/stocks_master.json` 和分片文件
- **中间产物**: 提取结果输出到 `data/stocks_master_YYYY-MM-DD.json`（不再是 `data/stocks/YYYY-MM-DD.json`）

## 🆕 v2.2 变更说明（2026-05-13）

### 新增：个股数据提取
- **新增字段**: `core_business`、`industry_position`、`chain`、`partners`
- **要求**: AI 必须从文章内容中提取这 4 个个股基础字段
- **理由**: Web 界面展示需要完整的个股数据结构

### 行业和概念映射优化
- **新增**: 直接映射 `archived/同花顺行业.xls` 和 `archived/所属概念.xls`
- **工具**: `map_industry_concept.py` 一键更新所有股票的行业和概念
- **优势**: 无需手动填写行业和概念，自动从同花顺数据源获取

### 流程简化
- **简化**: AI 只需提取结构化数据（accidents/insights/key_metrics/target_valuation）
- **简化**: 股票代码、名称、行业、概念自动从映射文件获取
- **工具**: `process_article.py` 整合全流程

---

## 🆕 v2.0 变更说明

### 路径修正
- **日期分片路径**: `data/master/stocks/` → `data/stocks/`
- **增量合并**: 已验证路径正确性，更新命令示例
- **新增 AI 辅助提取流程**: 替代 LLM API 方式，直接由 AI 从文章内容提取结构化数据

---

## 📋 目录

1. [Raw Material 文件格式](#raw-material-文件格式)
2. [数据处理流程](#数据处理流程)
3. [日期分片存储](#日期分片存储)
4. [完整示例](#完整示例)
5. [常见问题](#常见问题)

---

## 📄 Raw Material 文件格式

### 文件命名规范

```
raw_material/
├── raw_material_2026-04-09.md
├── raw_material_2026-04-10.md
├── raw_material_2026-04-12.md
├── raw_material_2026-04-12_2.md      # 同一天的第二篇
├── raw_material_2026-04-12_3.md      # 同一天的第三篇
└── raw_material_2026-04-13.md
```

**命名规则**:
- 基础格式：`raw_material_YYYY-MM-DD.md`
- 同一天多篇：`raw_material_YYYY-MM-DD_N.md` (N=2,3,4...)
- 测试文件：`test_YYYY-MM-DD.md`

### 文件结构

```markdown
## Article
source: https://mp.weixin.qq.com/s/jU3eFc1irDolyJyLd6egyg
fetched_at: 2026-05-09T10:30:00
title: 今天的一些信息整理 5.7

（文章完整内容）

一、盛科通信（688250）
1. 二季度订单加速放量
2. 阿里 3 万 +scale out 订单意向
3. 字节 3 万颗框架订单
```

### 字段说明

| 字段 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `## Article` | ✅ | 文章块标识 | 固定格式 |
| `source` | ✅ | 微信文章 URL | `https://mp.weixin.qq.com/s/...` |
| `fetched_at` | ✅ | 抓取时间（ISO 格式） | `2026-05-09T10:30:00` |
| `title` | ⭕ | 文章标题 | `今天的一些信息整理 5.7` |
| 正文内容 | ✅ | 文章完整文本 | 包含个股信息 |

---

## 🔄 数据处理流程

### 整体流程图

```
微信公众号文章                     离线 HTML 研报
    ↓ (实时抓取)                     ↓ (BeautifulSoup 解析)
raw_material/YYYY-MM-DD.md       process_html_value.py
raw_material/value_formatted/    process_topdown.py
    ↓                               ↓
[提取结构化数据]                data/stocks/value_YYYY-MM-DD.json
  - LLM API 方式                    ↓
  - AI 辅助方式               [补齐第一层字段]
    ↓                         extract_first_layer.py
data/stocks_master_YYYY-MM-DD.json  ↓
    ↓                               ↓
[合并到主数据 ← ← ← ← ← ← ← ← ← ← ┘
  ↓
data/stocks/stocks_master.json（主数据，前端读取）
  ↓
[build_derivatives.py] → stocks_meta.json + stocks_articles.json + .gz
  ↓
[Supabase 同步]  sync_to_supabase.py
  ↓
[ModelScope 部署]  https://treeie-aastock.ms.show
  ↓
[Web 界面展示]（三 Tab：仪表盘 / 分组 / 突破信号）
```

### Step 1: 创建 Raw Material

**方式A: 自动抓取**
```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/fetch_wechat_to_raw_material.py \
  --url "https://mp.weixin.qq.com/s/xxx" \
  --out "raw_material/raw_material_2026-05-09.md"
```

**方式B: AI 辅助创建**
1. AI 读取微信文章 URL 内容
2. 提取正文并格式化，确保包含 `## Article` 头部
3. 保存到 `raw_material/` 目录

### Step 2: 提取个股结构化数据

**方式 A: LLM 管道提取**
```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/extract_stocks_from_raw_material.py \
  --raw "raw_material/raw_material_2026-05-09.md" \
  --xls ".trae/skills/wechat-fetch-research-embedded/assets/全部个股.xls" \
  --out "data/stocks_master_2026-05-09.json"
```
*注意：该方式需要配置 LLM API Key，且可能因编码问题在 Windows 下运行失败*

**方式 B: AI 辅助提取（推荐）**

#### v2.5 优化流程（5 维度 + 轻量模式）：
1. AI 读取文章内容，识别提到的个股名称/代码
2. AI 按 **5 维度标准** 提取（必须严格遵守红线约束）：
   - **industry_background**（行业/赛道背景）：宏观趋势，**严禁出现公司名称**
   - **accidents**（事件/催化剂）：客观动作，≤60 字，**严禁主观推测词**
   - **insights**（个股投研观点）：该公司凭什么受益
   - **key_metrics**（关键指标）：**每条必须包含阿拉伯数字**
   - **target_valuation**（目标估值）：**必须包含具体数值+估值单位**
3. AI 提取个股基础信息（products/core_business/industry_position/chain/partners）
4. 质量判定：
   - 通过 → 写完整 article + 更新第一层 + mention_count+1
   - 轻量 → 静默合并第一层字段，mention_count 不变
   - 丢弃 → 完全无信息

#### 提取字段详细说明（v2.5 5 维度标准）：

**5 维度字段**：
| 字段 | 类型 | 说明 | 红线 |
|------|------|------|------|
| `industry_background` | string[] | 行业/赛道宏观背景 | **严禁出现公司名称** |
| `accidents` | string[] | 客观事件/催化剂，≤60字 | 严禁主观推测词 |
| `insights` | string[] | 个股投研观点/受益逻辑 | 必须指向具体个股 |
| `key_metrics` | string[] | 关键量化数据 | **必须包含阿拉伯数字** |
| `target_valuation` | string[] | 目标估值锚点 | **必须包含具体数值+单位** |

**第一层字段（从文章上下文推断）**：
| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `core_business` | string[] | 核心业务/主要产品 | `["交换芯片研发与销售"]` |
| `industry_position` | string[] | 行业地位/竞争优势 | `["国产交换芯片龙头"]` |
| `chain` | string[] | 产业链位置 | `["中游-芯片设计"]` |
| `partners` | string[] | 合作伙伴公司名称 | `["阿里巴巴", "字节跳动"]` |

**使用示例**：
```python
# 方式 1: 直接调用 process_article.py
python process_article.py

# 方式 2: AI 构建 JSON 后调用合并脚本
# AI 创建 data/stocks/2026-05-13.json
python merge_daily.py  # 合并到主数据
```

**方式 C: 批量更新行业和概念（一次性工作）**
```bash
# 首次使用或定期更新时运行
python map_industry_concept.py
```
这会从 `archived/同花顺行业.xls` 和 `archived/所属概念.xls` 批量更新所有股票的行业和概念信息。

**日期分片 JSON 格式**:
```json
{
  "date": "2026-05-13",
  "update_count": 99,
  "last_updated": "2026-05-13T15:00:00+08:00",
  "stocks": {
    "688800": {
      "name": "瑞可达",
      "code": "688800",
      "board": "SH",
      "industry": "电子-其他电子-其他电子Ⅲ",
      "concepts": ["铜缆高速连接", "5G", "液冷服务器"],
      "products": ["高速铜缆连接器(AEC)", "芯片测试治具"],
      "core_business": ["高速连接器研发生产", "5G 基站配套"],
      "industry_position": ["高速铜缆连接器国产替代龙头"],
      "chain": ["中游-连接器制造"],
      "partners": ["华为", "中兴通讯"],
      "articles": [
        {
          "title": "今天的一些信息整理5.12",
          "date": "2026-05-13",
          "source": "https://mp.weixin.qq.com/s/...",
          "accidents": ["与旭创合资设立睿创布局高速铜缆"],
          "insights": ["AEC高速互联+芯片测试+主业三重成长"],
          "key_metrics": ["2026年AEC收入10-15亿元"],
          "target_valuation": ["370亿"]
        }
      ],
      "last_updated": "2026-05-13"
    }
  }
}
```

### Step 2.5: 批量处理离线 HTML 研报（🆕 v2.4）

适用于已下载到 `raw_material/value/` 或 `raw_material/topdown/` 的大量 HTML 深度研报。

```bash
# Step 2.5a: 解析 HTML，提取纯文本 + 结构化数据
python process_html_value.py    # 处理 raw_material/value/
python process_topdown.py       # 处理 raw_material/topdown/

# 输出:
#   raw_material/value_formatted/ 或 topdown_formatted/  （纯文本 MD）
#   data/stocks/value_YYYY-MM-DD.json                     （结构化 JSON）

# Step 2.5b: AI 审核修正 JSON（名称、行业、概念不能错）
#  - 名称：从文件名提取，需人工/LLM核对
#  - 行业：从 archived/同花顺行业.xls 映射
#  - 概念：从 archived/所属概念.xls 映射

# Step 2.5c: 补齐第一层字段
python extract_first_layer.py
# 从 raw_material 提取 products/core_business/industry_position/chain/partners

# Step 2.5d: 合并到 stocks_master.json
# 由 process 脚本自动处理，或手动合并
```

**文件结构**：
```
raw_material/value/ 或 topdown/
├── 万控智造（603070_sh)深度价值投资分析报告/
│   └── index.html              ← 原始 HTML（含 CSS）
    ↓ process_html_value.py
raw_material/topdown_formatted/
└── 万控智造（603070_sh)...md    ← 纯文本 MD
    ↓
data/stocks/value_YYYY-MM-DD.json  ← 结构化 JSON
```

**清理规则**（仅保留有效文章）：
- 文章必须至少包含一个非空字段：accidents/insights/key_metrics/target_valuation
- 仅有 source 链接但无任何提取数据的文章会被自动删除

### Step 3: 合并到主数据（关键步骤！）

将新数据合并到 `stocks_master.json`（前端读取的主文件）：

```bash
# ⭐ 推荐方式：使用 merge_new_stocks.py（自动处理去重和分片更新）
python scripts/merge_new_stocks.py
```

该脚本会自动：
1. 读取 `data/stocks_master_YYYY-MM-DD.json`（Step 2 的输出）
2. 按 `source` 去重合并到 `data/stocks/stocks_master.json`
3. 同步更新 `data/stocks/YYYY-MM-DD.json` 分片文件
4. 累加 `mention_count`

> ⚠️ **注意**：`incremental_update.py`（skill 内部脚本）将数据写入 `.trae/skills/.../data/master/` 目录，**前端不读取该路径**。必须运行 `merge_new_stocks.py` 才能让前端看到新数据。

**验证（重要！）**：
```bash
# 检查泰和新材是否有 target_valuation
python -c "import json; d=json.load(open('data/stocks/stocks_master.json','r',encoding='utf-8')); s=d['stocks'].get('002254',{}); print(s.get('name',''), len(s.get('articles',[])), 'articles'); [print('  -', a.get('title'), 'tv:', a.get('target_valuation')) for a in s.get('articles',[])]"
```

### Step 4: 重建衍生文件

```bash
# 从 stocks_master.json 生成 meta + articles + gz
python build_derivatives.py
# 输出: stocks_meta.json (2.8MB) + stocks_articles.json (2.9MB) + stocks_master.json.gz (1.1MB)
```

### Step 5: 同步 + 部署

```bash
# 1. 推 GitHub
git add data/stocks/stocks_master.json data/stocks/*.json
git add data/groups/ data/hot_topics/ breakt/
git commit -m "feat: add stocks from YYYY-MM-DD article"
git push origin main

# 2. 同步到 Supabase（可选）
python sync_to_supabase.py --date 2026-06-26

# 3. ModelScope 自动部署，或手动 Redeploy
# https://modelscope.cn/studios/TREEIE/aastock
```

---

## 📅 日期分片存储

### 数据架构

```
data/
├── stocks/                    # 个股数据
│   ├── 2026-03-25.json       # 按日期分片存储
│   ├── 2026-04-05.json
│   ├── 2026-05-09.json
│   ├── 2026-05-13.json       # 当日新增
│   ├── stocks_master.json    # 完整主数据（合并所有分片）
│   └── stocks_index.json     # 股票索引
├── groups/                   # 分组数据
│   └── groups.json
└── hot_topics/               # 热点数据
    └── hot_topics.json
```

### 行业字段规范 ⭐️

`industry` 字段必须使用**三级行业分类**，禁止使用板块名称：

| ❌ 错误 | ✅ 正确 |
|---------|---------|
| 创业板 | 电子 - 半导体 - 电子元器件 |
| 科创板 | 机械设备 - 自动化设备 - 电源设备 |
| 深市主板 | 医药生物 - 生物制品 - 疫苗 |

### 文章标题规范 ⭐️

所有文章 `title` 统一使用格式：`今天的一些信息整理MM.DD`
- 示例：`今天的一些信息整理5.12`

---

## 📝 完整示例

### 示例：处理一篇微信文章

#### 1. 创建 raw_material

```markdown
## Article
source: https://mp.weixin.qq.com/s/jU3eFc1irDolyJyLd6egyg
fetched_at: 2026-05-09T10:30:00
title: 今天的一些信息整理 5.7

一、盛科通信（688250）
1. 二季度订单加速放量
2. 阿里 3 万 +scale out 订单意向
```

#### 2. 提取个股信息

**输出路径**: `data/stocks_master_2026-05-09.json`（中间产物，需运行 `python scripts/merge_new_stocks.py` 合并到主文件）

```json
{
  "date": "2026-05-09",
  "update_count": 2,
  "last_updated": "2026-05-09T18:00:00+08:00",
  "stocks": {
    "688250": {
      "name": "盛科通信",
      "code": "688250",
      "board": "SH",
      "industry": "电子 - 半导体 - 集成电路",
      "concepts": ["交换芯片", "Scale-out", "国产芯片"],
      "products": ["交换芯片"],
      "core_business": ["交换芯片研发与销售"],
      "industry_position": ["国产交换芯片龙头", "国内份额30%"],
      "chain": ["中游-芯片设计"],
      "partners": ["阿里巴巴", "字节跳动"],
      "articles": [
        {
          "title": "今天的一些信息整理5.7",
          "date": "2026-05-09",
          "source": "https://mp.weixin.qq.com/s/jU3eFc1irDolyJyLd6egyg",
          "industry_background": ["交换芯片从配角变主角，Scale-out需求爆发驱动出货量倍增"],
          "accidents": ["二季度订单加速放量"],
          "insights": ["国产交换芯片龙头，份额30%"],
          "key_metrics": [],
          "target_valuation": []
        }
      ],
      "last_updated": "2026-05-09"
    }
  }
}
```

#### 3. 合并到主数据 + 验证

```bash
# 合并（使用 merge_new_stocks.py）
python scripts/merge_new_stocks.py

# 验证
python -c "import json; d=json.load(open('data/stocks/stocks_master.json','r',encoding='utf-8')); print('Total:', len(d['stocks']), 'stocks')"
```

#### 4. 同步到 Supabase

```bash
# 增量同步（推荐，每次合并后运行）
python .trae/skills/wechat-fetch-research-embedded/scripts/sync_to_supabase.py --date 2026-06-20

# 全量同步（首次或修复时使用）
python .trae/skills/wechat-fetch-research-embedded/scripts/sync_to_supabase.py --full
```

#### 5. 重启服务器 + Git 提交

```bash
# 重启
Stop-Process -Name "python" -Force
Start-Process -NoNewWindow python -ArgumentList "main.py"

# 提交
git add raw_material/raw_material_2026-05-09.md
git add data/stocks_master_2026-05-09.json
git add data/stocks/stocks_master.json
git add data/stocks/2026-05-09.json
git commit -m "feat: 添加 YYYY-MM-DD 数据（N只股票）"
git push origin main
```

---

## ❓ 常见问题

### Q1: raw_material 文件应该保存到哪里？
**A**: 保存到 `raw_material/` 目录，命名格式为 `raw_material_YYYY-MM-DD.md`。

### Q2: 同一天有多篇文章怎么办？
**A**: 使用序号区分：`_1.md`, `_2.md`, `_3.md`...

### Q3: 行业字段显示"创业板/科创板"怎么办？
**A**: 必须修正为三级行业分类。常见修正对照见 [行业字段规范](#行业字段规范-) 表格。

### Q4: 合并后页面没有更新？
**A**: 必须**重启 Flask 服务器**才能生效。`stocks_master.json` 在服务器启动时加载。

### Q5: Supabase 同步失败怎么办？
**A**: 
1. 检查 Supabase 连接和 API Key
2. 检查网络连接
3. 查看错误日志
4. 可以跳过 Supabase 同步，GitHub + ModelScope 即可正常展示

---

## 📊 数据质量检查

### 检查清单

- [ ] raw_material 文件格式正确（`## Article` 头部）
- [ ] source URL 正确
- [ ] fetched_at 时间格式正确
- [ ] 提取的 JSON 格式符合规范
- [ ] 股票代码映射正确
- [ ] industry 字段不是"创业板/科创板"等板块名
- [ ] 文章 title 格式统一
- [ ] 合并后 stocks_master.json 已更新
- [ ] Flask 服务器已重启（页面生效）
- [ ] Git 已提交并推送

---

**文档维护**: 系统自动更新  
**最后更新**: 2026-06-21
