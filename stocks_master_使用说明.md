# stocks_master.json 使用说明

**位置**: `data/stocks/stocks_master.json`
**版本**: v3.0 | **衍生文件**: `stocks_meta.json` + `stocks_articles.json`
**数据量**: 3553 只 A 股 | **更新日期**: 2026-06-26

---

## v3.0 数据架构

```
stocks_master.json (8.5MB)  ← 唯一写入源，管线不变
    │
    │ build_derivatives.py
    ▼
┌──────────────────────────────────────┐
│ stocks_meta.json       (2.8MB)       │  ← Flask 启动加载（轻量）
│ stocks_articles.json   (2.9MB)       │  ← 个股详情按需加载
│ stocks_master.json.gz  (1.1MB)       │  ← Vercel/Docker 打包
└──────────────────────────────────────┘
```

| 场景 | 数据源 | 说明 |
|------|--------|------|
| 管线处理文章 | `stocks_master.json` | 直接读写，不变 |
| Flask 启动 | `stocks_meta.json` | 2.8MB，秒加载 |
| 个股详情页 | `stocks_articles.json` | 只读当前股票 |
| 搜索/列表 | `stocks_meta.json` | 不需要文章内容 |
| Docker 构建 | `stocks_master.json.gz` | 1.1MB 压缩包 |

## 1. 整体结构

```json
{
  "version": "2.4",
  "updated_at": "2026-06-26",
  "stocks": {
    "002962": { /* 个股对象 */ },
    "002436": { /* 个股对象 */ },
    // ... 共 3553 只股票，以 6 位股票代码为 key
  }
}
```

## 2. 个股对象（两层结构）

### 第一层：股票基本信息

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 股票名称 |
| `code` | string | 6位股票代码 |
| `industry` | string | 行业分类 `"电子-半导体-集成电路"` |
| `concepts` | string[] | 概念标签 |
| `products` | string[] | 产品列表 |
| `core_business` | string[] | 核心业务 |
| `industry_position` | string[] | 行业地位 |
| `chain` | string[] | 产业链位置 |
| `partners` | string[] | 合作伙伴 |
| `mention_count` | number | 被引用次数（= len(articles)） |
| `last_updated` | string | 最后更新日期 |
| `lyt_score` | number | 五维评分（lyt 数据） |

### 第二层：文章详情

| 字段 | 说明 | 约束 |
|------|------|------|
| `title` | 文章标题 | 必填 |
| `date` | 发布日期 | `YYYY-MM-DD` |
| `source` | 原文 URL | 去重键 |
| `accidents` | 事件/催化剂 | ≤60字 |
| `insights` | 投研观点 | 指向具体个股 |
| `key_metrics` | 关键数据 | 必须含阿拉伯数字 |
| `target_valuation` | 目标估值 | 必须含市值/PE/PB+数字 |

## 3. 快速使用

### Python

```python
import json

# 完整加载（管线用）
with open('data/stocks/stocks_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 轻量加载（Web 用）
with open('data/stocks/stocks_meta.json', 'r', encoding='utf-8') as f:
    meta = json.load(f)

# 按需获取文章
with open('data/stocks/stocks_articles.json', 'r', encoding='utf-8') as f:
    articles = json.load(f)
stock_arts = articles.get("002436", [])

# 衍生文件重建
# python build_derivatives.py
```

## 4. 常见问题

**Q: 管线处理后数据没生效？**
运行 `python build_derivatives.py` 重新生成 meta + articles + gz

**Q: Flask 启动慢？**
自动优先加载 `stocks_meta.json`（2.8MB），无需等待全部文章

**Q: `mention_count` 的含义？**
等于 `len(articles)`，新增文章后自动同步
