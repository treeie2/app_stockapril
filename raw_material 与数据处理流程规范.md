# Raw Material 与数据处理流程规范

**版本**: v1.0  
**更新日期**: 2026-05-11  
**适用**: 微信文章→原始素材→结构化数据全流程

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

今天收集到的一些信息，分享如下：

一、盛科通信（688250）
1. 二季度订单加速放量
2. 阿里 3 万 +scale out 订单意向
3. 字节 3 万颗框架订单

二、德福科技（300991）
1. 固态电池负极用铜箔量产
2. 2026 年固态电池装机 100GWh

---
```

### 字段说明

| 字段 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `## Article` | ✅ | 文章块标识 | 固定格式 |
| `source` | ✅ | 微信文章 URL | `https://mp.weixin.qq.com/s/...` |
| `fetched_at` | ✅ | 抓取时间（ISO 格式） | `2026-05-09T10:30:00` |
| `title` | ⭕ | 文章标题 | `今天的一些信息整理 5.7` |
| `date` | ⭕ | 文章发布日期 | `2026-05-09` |
| 正文内容 | ✅ | 文章完整文本 | 包含个股信息 |

### 生成方式

#### 方式 1: 自动抓取（推荐）

```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/fetch_wechat_to_raw_material.py \
  --url "https://mp.weixin.qq.com/s/jU3eFc1irDolyJyLd6egyg" \
  --out "raw_material/raw_material_2026-05-09.md"
```

#### 方式 2: 手动创建

1. 复制微信文章全文
2. 按照上述格式保存为 `.md` 文件
3. 确保包含 `## Article` 和元数据

---

## 🔄 数据处理流程

### 整体流程图

```
微信公众号文章
    ↓
[Step 1] 抓取文章
fetch_wechat_to_raw_material.py
    ↓
raw_material/raw_material_YYYY-MM-DD.md
    ↓
[Step 2] 提取个股信息
extract_stocks_from_raw_material.py
    ↓
data/master/stocks/2026-05-09.json
    ↓
[Step 3] 增量合并
incremental_update.py
    ↓
data/master/stocks_index.json
data/master/stocks_master.json
    ↓
[Step 4] 同步到 Firebase
sync_to_firestore.py
    ↓
Firestore 数据库
    ↓
[Step 5] Web 界面展示
```

### Step 1: 抓取文章

**脚本**: `fetch_wechat_to_raw_material.py`

**功能**:
- 从微信公众号 URL 抓取文章
- 保存为 raw_material 格式
- 自动提取标题、日期等元数据

**命令**:
```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/fetch_wechat_to_raw_material.py \
  --url "https://mp.weixin.qq.com/s/xxx" \
  --out "raw_material/raw_material_2026-05-09.md"
```

**参数**:
- `--url`: 微信文章链接（必填）
- `--out`: 输出文件路径（必填）
- `--mcp_server`: MCP 服务器名称（可选）
- `--mcp_tool`: MCP 工具名称（可选）

### Step 2: 提取个股信息

**脚本**: `extract_stocks_from_raw_material.py`

**功能**:
- 读取 raw_material markdown 文件
- 使用 LLM 识别提到的股票
- 提取结构化数据（accidents/insights/key_metrics/target_valuation）
- 映射到股票代码和名称

**命令**:
```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/extract_stocks_from_raw_material.py \
  --raw "raw_material/raw_material_2026-05-09.md" \
  --xls ".trae/skills/wechat-fetch-research-embedded/assets/全部个股.xls" \
  --out "data/stocks/2026-05-09.json"
```

**参数**:
- `--raw`: raw_material 文件路径（必填）
- `--xls`: 全部个股 Excel 文件（必填）
- `--out`: 输出 JSON 文件（必填）
- `--api_key`: OpenAI API Key（可选，从环境变量读取）

**输出示例**:
```json
{
  "date": "2026-05-09",
  "source": "https://mp.weixin.qq.com/s/jU3eFc1irDolyJyLd6egyg",
  "stocks": {
    "688250": {
      "name": "盛科通信",
      "code": "688250",
      "board": "SH",
      "industry": "电子 - 半导体 - 集成电路",
      "concepts": ["交换芯片", "Scale-out", "国产芯片"],
      "products": ["交换芯片"],
      "core_business": ["交换芯片研发与销售"],
      "industry_position": ["国产交换芯片龙头"],
      "chain": ["中游 - 芯片设计"],
      "partners": ["阿里巴巴", "字节跳动", "腾讯"],
      "mention_count": 1,
      "valuation": {
        "target_market_cap": "2700 亿",
        "target_market_cap_billion": 2700.0
      },
      "articles": [
        {
          "title": "今天的一些信息整理 5.7",
          "date": "2026-05-09",
          "source": "https://mp.weixin.qq.com/s/jU3eFc1irDolyJyLd6egyg",
          "accidents": ["二季度订单加速放量", "阿里 3 万 +scale out 订单"],
          "insights": ["MRC 协议影响有限，珍惜倒车接人机会"],
          "key_metrics": ["2026 年国产 GPU 出货量预计 400 万颗"],
          "target_valuation": ["约 2700 亿市值"]
        }
      ],
      "last_updated": "2026-05-09"
    }
  }
}
```

### Step 3: 增量合并

**脚本**: `incremental_update.py`

**功能**:
- 将每日数据合并到日期分片文件
- 更新股票索引
- 去重文章（按 source + title）
- 合并重复股票代码

**命令**:
```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/incremental_update.py \
  --json "data/stocks/2026-05-09.json" \
  --mode merge
```

**工作模式**:
- `merge`: 合并每日数据到分片
- `single`: 更新单只股票
- `rebuild-index`: 重建索引

**输出**:
1. `data/stocks/2026-05-09.json` - 日期分片
2. `data/stocks/stocks_index.json` - 股票索引
3. `data/stocks/stocks_master.json` - 完整备份（可选）

### Step 4: 同步到 Firebase

**脚本**: `sync_to_firestore.py`

**功能**:
- 将 JSON 数据同步到 Firebase Firestore
- 支持增量更新
- 自动合并现有数据

**命令**:
```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/sync_to_firestore.py \
  --credentials ".trae/rules/firebase-credentials.json" \
  --json "data/master/stocks/2026-05-09.json" \
  --on_exists merge
```

**参数**:
- `--credentials`: Firebase 凭证文件（必填）
- `--json`: 要同步的 JSON 文件（必填）
- `--on_exists`: 遇到已存在股票时的处理方式
  - `merge`: 合并数据
  - `skip`: 跳过
  - `overwrite`: 覆盖

### Step 5: Web 界面展示

数据自动在 Web 界面展示：
- 股票列表：`/stocks`
- 个股详情：`/stock/{code}`
- 分组详情：`/group/{id}`
- 热点详情：`/hot-topic/{id}`

---

## 📅 日期分片存储

### 数据架构

```
data/
├── stocks/                    # 个股数据
│   ├── stocks/               # 按日期分片存储
│   │   ├── 2026-03-25.json
│   │   ├── 2026-04-05.json
│   │   └── 2026-05-09.json
│   ├── stocks_master.json    # 完整备份（可选）
│   └── stocks_index.json     # 股票索引
├── groups/                   # 分组数据
│   └── groups.json
└── hot_topics/               # 热点数据
    └── hot_topics.json
```

### 分片文件格式

```json
{
  "date": "2026-05-09",
  "update_count": 23,
  "stocks": {
    "688250": { ... },
    "300991": { ... },
    "002416": { ... }
  }
}
```

### 索引文件格式

```json
{
  "version": "2.0",
  "last_updated": "2026-05-09",
  "total_stocks": 3157,
  "stocks": {
    "688250": {
      "name": "盛科通信",
      "code": "688250",
      "last_updated": "2026-05-09",
      "file": "2026-05-09.json"
    },
    "300991": {
      "name": "德福科技",
      "code": "300991",
      "last_updated": "2026-05-09",
      "file": "2026-05-09.json"
    }
  }
}
```

### 优势

1. **增量更新**: 只处理当日数据，不影响历史
2. **快速查找**: 通过索引快速定位股票
3. **易于备份**: 按日期归档
4. **避免冲突**: 多人协作时减少冲突

---

## 📝 完整示例

### 示例：处理一篇微信文章

#### 1. 抓取文章

```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/fetch_wechat_to_raw_material.py \
  --url "https://mp.weixin.qq.com/s/jU3eFc1irDolyJyLd6egyg" \
  --out "raw_material/raw_material_2026-05-09.md"
```

**生成的 raw_material 文件**:
```markdown
## Article
source: https://mp.weixin.qq.com/s/jU3eFc1irDolyJyLd6egyg
fetched_at: 2026-05-09T10:30:00
title: 今天的一些信息整理 5.7

今天收集到的一些信息，分享如下：

一、盛科通信（688250）
1. 二季度订单加速放量
2. 阿里 3 万 +scale out 订单意向
3. 字节 3 万颗框架订单
4. 国产交换芯片龙头，份额 30%

二、德福科技（300991）
1. 固态电池负极用铜箔已量产
2. 2026 年固态电池装机 100GWh
3. 铜箔加工费触底反弹

三、品高股份（688227）
1. 发布大模型一体机
2. 2026 年订单翻倍
```

#### 2. 提取个股信息

```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/extract_stocks_from_raw_material.py \
  --raw "raw_material/raw_material_2026-05-09.md" \
  --xls ".trae/skills/wechat-fetch-research-embedded/assets/全部个股.xls" \
  --out "data/master/stocks/2026-05-09.json"
```

**生成的 JSON 文件**:
```json
{
  "date": "2026-05-09",
  "source": "https://mp.weixin.qq.com/s/jU3eFc1irDolyJyLd6egyg",
  "stocks": {
    "688250": {
      "name": "盛科通信",
      "code": "688250",
      "board": "SH",
      "articles": [
        {
          "title": "今天的一些信息整理 5.7",
          "date": "2026-05-09",
          "source": "https://mp.weixin.qq.com/s/jU3eFc1irDolyJyLd6egyg",
          "accidents": [
            "二季度订单加速放量",
            "阿里 3 万 +scale out 订单",
            "字节 3 万颗框架订单"
          ],
          "insights": [
            "国产交换芯片龙头，份额 30%"
          ],
          "key_metrics": [],
          "target_valuation": []
        }
      ],
      "last_updated": "2026-05-09"
    },
    "300991": {
      "name": "德福科技",
      "code": "300991",
      "board": "SZ",
      "articles": [
        {
          "title": "今天的一些信息整理 5.7",
          "date": "2026-05-09",
          "source": "https://mp.weixin.qq.com/s/jU3eFc1irDolyJyLd6egyg",
          "accidents": [
            "固态电池负极用铜箔已量产"
          ],
          "insights": [
            "铜箔加工费触底反弹"
          ],
          "key_metrics": [
            "2026 年固态电池装机 100GWh"
          ],
          "target_valuation": []
        }
      ],
      "last_updated": "2026-05-09"
    }
  }
}
```

#### 3. 增量合并

```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/incremental_update.py \
  --json "data/master/stocks/2026-05-09.json" \
  --mode merge
```

**更新后的索引**:
```json
{
  "version": "2.0",
  "last_updated": "2026-05-09",
  "total_stocks": 3157,
  "stocks": {
    "688250": {
      "name": "盛科通信",
      "code": "688250",
      "last_updated": "2026-05-09",
      "file": "2026-05-09.json"
    },
    "300991": {
      "name": "德福科技",
      "code": "300991",
      "last_updated": "2026-05-09",
      "file": "2026-05-09.json"
    }
  }
}
```

#### 4. 同步到 Firebase

```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/sync_to_firestore.py \
  --credentials ".trae/rules/firebase-credentials.json" \
  --json "data/master/stocks/2026-05-09.json" \
  --on_exists merge
```

**输出**:
```
{"collection": "stocks", "article_subcollection": "articles", 
 "stocks": 2, "articles_total": 2, "articles_created": 2, 
 "articles_updated": 0, "parent_articles_upserts": 2, "on_exists": "merge"}
```

#### 5. 提交到 Git

```bash
git add raw_material/raw_material_2026-05-09.md
git add data/master/stocks/2026-05-09.json
git add data/master/stocks_index.json
git commit -m "feat: 添加 2026-05-09 数据（盛科通信、德福科技）"
git push origin main
```

---

## ❓ 常见问题

### Q1: raw_material 文件应该保存到哪里？

**A**: 保存到 `raw_material/` 目录，命名格式为 `raw_material_YYYY-MM-DD.md`。

### Q2: 同一天有多篇文章怎么办？

**A**: 使用序号区分：
- `raw_material_2026-05-09.md`
- `raw_material_2026-05-09_2.md`
- `raw_material_2026-05-09_3.md`

### Q3: 提取的股票代码不正确怎么办？

**A**: 检查 `全部个股.xls` 是否最新，或手动修正 JSON 文件中的股票代码。

### Q4: 如何合并重复的股票代码？

**A**: 使用 `incremental_update.py` 的 `merge` 模式，会自动去重文章。

### Q5: 数据同步失败怎么办？

**A**: 
1. 检查 Firebase 凭证文件是否正确
2. 检查网络连接
3. 查看错误日志
4. 重试同步命令

### Q6: 如何回滚错误的数据？

**A**: 
1. 从 Git 恢复旧的 JSON 文件
2. 重新运行 `incremental_update.py`
3. 重新同步到 Firebase

---

## 🔧 自动化脚本

### 一键处理脚本

```bash
#!/bin/bash
# process_article.sh - 一键处理微信文章

URL=$1
DATE=$(date +%Y-%m-%d)

echo "1. 抓取文章..."
python .trae/skills/wechat-fetch-research-embedded/scripts/fetch_wechat_to_raw_material.py \
  --url "$URL" \
  --out "raw_material/raw_material_${DATE}.md"

echo "2. 提取个股..."
python .trae/skills/wechat-fetch-research-embedded/scripts/extract_stocks_from_raw_material.py \
  --raw "raw_material/raw_material_${DATE}.md" \
  --xls ".trae/skills/wechat-fetch-research-embedded/assets/全部个股.xls" \
  --out "data/master/stocks/${DATE}.json"

echo "3. 增量合并..."
python .trae/skills/wechat-fetch-research-embedded/scripts/incremental_update.py \
  --json "data/master/stocks/${DATE}.json" \
  --mode merge

echo "4. 同步到 Firebase..."
python .trae/skills/wechat-fetch-research-embedded/scripts/sync_to_firestore.py \
  --credentials ".trae/rules/firebase-credentials.json" \
  --json "data/master/stocks/${DATE}.json" \
  --on_exists merge

echo "✅ 完成！"
```

**使用方式**:
```bash
./process_article.sh "https://mp.weixin.qq.com/s/xxx"
```

---

## 📊 数据质量检查

### 检查清单

- [ ] raw_material 文件格式正确
- [ ] 包含 `## Article` 标识
- [ ] source URL 正确
- [ ] fetched_at 时间格式正确
- [ ] 提取的 JSON 文件格式符合规范
- [ ] 股票代码映射正确
- [ ] 文章去重成功
- [ ] Firebase 同步成功

### 验证命令

```bash
# 验证 JSON 格式
python -c "import json; json.load(open('data/master/stocks/2026-05-09.json'))"

# 检查 Firebase 数据
python check_firebase_stocks.py

# 查看索引
cat data/master/stocks_index.json
```

---

**文档维护**: 系统自动更新  
**最后更新**: 2026-05-11
