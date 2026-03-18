# 📊 智能投研仪表板 - JSON 数据格式标准

## 文件位置

### 主数据文件
```
/home/admin/openclaw/workspace/railway-deploy/data/master/stocks_master.json
```

### 搜索索引文件（压缩）
```
/home/admin/openclaw/workspace/railway-deploy/data/sentiment/search_index_full.json.gz
```

### 格式定义脚本
```
/home/admin/openclaw/workspace/railway-deploy/build_index.py
```

---

## 📋 stocks_master.json 格式

### 根结构
```json
{
  "stocks": [
    {
      "code": "601869",
      "name": "长飞光纤",
      "board": "SH",
      "mention_count": 44,
      "concepts": [...],
      "industries": [...],
      "products": [...],
      "core_business": "...",
      "industry_position": "...",
      "chain": "...",
      "key_metrics": "...",
      "partners": [...],
      "accident": "...",
      "insights": "...",
      "articles": [...],
      "detail_texts": [...]
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `code` | string | ✅ | 6 位股票代码 | `"601869"` |
| `name` | string | ✅ | 股票简称 | `"长飞光纤"` |
| `board` | string | ✅ | 交易所板块 | `"SH"` (上海), `"SZ"` (深圳), `"BJ"` (北交所) |
| `mention_count` | number | ❌ | 提及次数 | `44` |
| `concepts` | array | ❌ | 概念标签 | `["算力基础设施", "光通信/CPO"]` |
| `industries` | array | ❌ | 行业分类 | `["光通信/CPO", "光通信/CPO"]` |
| `products` | array | ❌ | 主要产品 | `["G.654.E 超低损耗光纤", "光纤预制棒"]` |
| `core_business` | string | ❌ | 核心业务描述 | `"光纤预制棒、光纤、光缆及综合解决方案..."` |
| `industry_position` | string | ❌ | 行业地位 | `"全球最大的光纤预制棒及光纤供应商..."` |
| `chain` | string | ❌ | 产业链位置 | `"光通信产业链中上游核心材料与传输媒介"` |
| `key_metrics` | string | ❌ | 关键指标 | `"预制棒自给率 100%，海外收入占比逐年提升"` |
| `partners` | array | ❌ | 合作伙伴/客户 | `["中国移动", "中国电信", "中兴通讯"]` |
| `accident` | string | ❌ | 催化剂/事件驱动 | `"近期受「全国一体化算力网络长途干线启动 400G 升级」催化..."` |
| `insights` | string | ❌ | 投资洞察/逻辑 | `"公司是全球唯一具备三种主流预制棒工艺..."` |
| `articles` | array | ❌ | 来源文章列表 | 见下方格式 |
| `detail_texts` | array | ❌ | 详细文本（7 个维度） | 见下方格式 |

---

## 📄 articles 数组格式

```json
"articles": [
  {
    "article_id": "300308_email://18901700722@163.com/uid/1773406505",
    "article_title": "股票 LLM 摘要处理任务",
    "article_url": "email://18901700722@163.com/uid/1773406505",
    "date": "2026-03-16",
    "source": "llm_summary",
    "context": "全球领先的光通信收发模块制造商...",
    "accident": "亚马逊、Meta 等硅谷巨头大幅上调 2026 年资本开支...",
    "industry_position": "全球光模块行业龙头...",
    "products": ["800G 光模块", "400G 光模块"],
    "partners": ["谷歌", "Meta", "英伟达"]
  }
]
```

### articles 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `article_id` | string | 唯一文章 ID（格式：`{code}_{source}`） |
| `article_title` | string | 文章标题 |
| `article_url` | string | 文章链接（email://或 http://） |
| `date` | string | 日期（YYYY-MM-DD） |
| `source` | string | 来源类型（`llm_summary`, `wechat_article`, `manual`） |
| `context` | string | 核心业务摘要 |
| `accident` | string | 催化剂 |
| `industry_position` | string | 行业地位 |
| `products` | array | 产品列表 |
| `partners` | array | 合作伙伴 |

---

## 📝 detail_texts 数组格式

```json
"detail_texts": [
  "核心业务：全球领先的光通信收发模块制造商...",
  "行业地位：全球光模块行业龙头...",
  "产业链：处于光通信产业链核心节点...",
  "关键指标：25 年预期净利超 60 亿...",
  "催化剂：亚马逊、Meta 等硅谷巨头大幅上调 2026 年资本开支...",
  "投资洞察：公司在 800G 光模块领域占据全球 50% 以上市场份额...",
  "合作伙伴：谷歌 (Google), Meta, 英伟达, 微软"
]
```

### detail_texts 顺序（固定 7 个维度）

1. **核心业务** - 公司主营业务描述
2. **行业地位** - 市场地位和竞争优势
3. **产业链** - 在产业链中的位置
4. **关键指标** - 财务/经营关键数据
5. **催化剂** - 近期事件驱动
6. **投资洞察** - 投资逻辑和亮点
7. **合作伙伴** - 主要客户/合作伙伴

---

## 🔀 支持两种数据格式

### 格式 A: llm_summary 嵌套格式（批量 LLM 处理）

```json
{
  "code": "300308",
  "name": "中际旭创",
  "llm_summary": {
    "core_business": "...",
    "insights": "...",
    "accident": "...",
    "products": [...],
    "partners": [...],
    "chain": "...",
    "key_metrics": "...",
    "industry_position": "..."
  }
}
```

### 格式 B: 直接字段格式（邮件直传）

```json
{
  "code": "300308",
  "name": "中际旭创",
  "core_business": "...",
  "insights": "...",
  "accident": "...",
  "products": [...],
  "partners": [...],
  "chain": "...",
  "key_metrics": "...",
  "industry_position": "..."
}
```

**自动识别逻辑：** `build_index.py` 中的 `extract_stock_fields()` 函数会自动检测并兼容两种格式。

---

## 🗂️ search_index_full.json.gz 格式

这是前端搜索使用的索引文件，结构与 `stocks_master.json` 类似，但增加了搜索优化字段：

```json
{
  "601869": {
    "name": "长飞光纤",
    "board": "SH",
    "mention_count": 44,
    "concepts": ["算力基础设施", "光通信/CPO"],
    "industries": ["光通信/CPO"],
    "products": ["G.654.E 超低损耗光纤"],
    "core_business": "...",
    "industry_position": "...",
    "chain": "...",
    "key_metrics": "...",
    "partners": ["中国移动"],
    "accident": "...",
    "insights": "...",
    "articles": []
  }
}
```

**区别：**
- 以股票代码为键（非数组）
- 经过 gzip 压缩（减小传输体积）
- 文本字段已清理（移除 Markdown/HTML 格式）

---

## 🛠️ 数据处理流程

```
1. 原始数据 (emails_raw.json / wechat_articles)
        ↓
2. LLM 处理 (生成 llm_summary 字段)
        ↓
3. 合并到 stocks_master.json (JVSCLAW_merge_all_sources.py)
        ↓
4. 清理文本 (JVSCLAW_clean_texts.py)
   - 繁体→简体转换
   - 多来源格式化为 [1][2][3] + --- 分隔线
        ↓
5. 生成搜索索引 (build_index.py)
   - 提取核心字段
   - 清理 Markdown/HTML
   - gzip 压缩
        ↓
6. 推送到 Railway (git push)
```

---

## 📌 多来源内容格式

当同一股票在多个来源中出现时，使用以下格式：

### 内部存储（||| 分隔）
```
催化剂内容 1 ||| 催化剂内容 2 ||| 催化剂内容 3
```

### 前端显示（编号 + 分隔线）
```
[1] 催化剂内容 1

---

[2] 催化剂内容 2

---

[3] 催化剂内容 3
```

**实现方式：**
- `JVSCLAW_clean_texts.py` 中的 `format_multi_source()` 函数
- 前端 `renderMultiSource()` JavaScript 函数解析并渲染

---

## 🎯 前端 API 接口

### 获取股票详情
```
GET /api/stock/{code}
```

**响应示例：**
```json
{
  "code": "300308",
  "name": "中际旭创",
  "board": "SZ",
  "concepts": ["算力基础设施", "光通信/CPO"],
  "core_business": "...",
  "accident": "[1] 催化剂内容 1\n\n---\n\n[2] 催化剂内容 2",
  "insights": "...",
  "products": ["800G 光模块"],
  "partners": ["英伟达", "谷歌"],
  "articles": [...]
}
```

### 搜索接口
```
GET /api/search?q=关键词
```

**搜索范围：**
- 股票代码（权重 1000）
- 股票名称（权重 500）
- 概念标签（权重 300）
- 内容字段（权重 200）
- 行业/产业链（权重 150）

---

## 📁 关键文件路径汇总

| 文件 | 路径 | 用途 |
|------|------|------|
| 主数据 | `railway-deploy/data/master/stocks_master.json` | 完整股票数据 |
| 搜索索引 | `railway-deploy/data/sentiment/search_index_full.json.gz` | 前端搜索 |
| 构建脚本 | `railway-deploy/build_index.py` | 生成索引 |
| 合并脚本 | `JVSCLAW_merge_all_sources.py` | 合并多来源数据 |
| 清理脚本 | `JVSCLAW_clean_texts.py` | 文本清理和格式化 |
| 主应用 | `railway-deploy/main.py` | Flask 后端 API |

---

**最后更新：** 2026-03-18  
**维护者：** Teeext · 严谨专业版
