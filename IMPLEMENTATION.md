# `app_stockapril` 项目实施文档

> **最后更新**: 2026-06-28
> **版本**: v3.0
> **维护**: 龙虾 AI 团队

---

## 目录

1. [系统概述](#一系统概述)
2. [架构设计](#二架构设计)
3. [数据模型](#三数据模型)
4. [实体抽取与数据流](#四实体抽取与数据流)
5. [工具定义与脚本清单](#五工具定义与脚本清单)
6. [数据源配置](#六数据源配置)
7. [API 接口文档](#七api-接口文档)
8. [前端页面](#八前端页面)
9. [部署配置](#九部署配置)
10. [部署检查清单](#十部署检查清单)

---

## 一、系统概述

### 1.1 项目定位

`app_stockapril` 是一个 **A 股个股研究数据库与 Web 展示平台**。核心能力：
- 从微信公众号文章/离线研报中提取个股结构化数据
- 构建 3500+ 只 A 股的研究数据库（概念、业务、行业地位、估值）
- 通过 Web 界面展示个股详情、分组、热点、行情
- 支持多平台部署（本地/Vercel/ModelScope/Railway）

### 1.2 系统角色

| 角色 | 位置 | 职责 |
|------|------|------|
| **Flask Web 服务** | `main.py` (3700+ 行) | Web UI + REST API + 数据加载 |
| **Vercel 入口** | `api/index.py` | 无服务器部署适配 |
| **数据加载器** | `main.py` load_all_data() | 本地 → GitHub Raw → Supabase 三级回退 |
| **文章处理器** | `process_article.py` | 微信文章 → raw_material → 结构化 JSON |
| **研报处理器** | `process_html_value.py` | 批量解析价值/自上而下研报 |
| **分组处理器** | `process_groups.py` | 通达信/同花顺导出 → groups.json |
| **衍生构建器** | `build_derivatives.py` | master → meta + articles + gz |
| **同步器** | `sync_to_supabase.py` | 本地 → Supabase PostgreSQL |
| **突破信号** | `breakt/` | lyt 老鸭头形态信号 |
| **龙虾 AI Agent** | `AGENTS.md` | 飞书消息 → 抓取 → 提取 → 推送 |

---

## 二、架构设计

### 2.1 整体架构图

```
┌──────────────────────────────────────────────────┐
│                    前端展示层                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ 仪表板 / │  │ 看板     │  │ 个股详情 /stock/  │ │
│  │ /board   │  │ /groups  │  │ /concept/        │ │
│  └──────────┘  └──────────┘  └──────────────────┘ │
└──────────────────────┬───────────────────────────┘
                       │ HTTP/Flask
┌──────────────────────┴───────────────────────────┐
│                  API 层 (main.py)                  │
│  /api/market-data  /api/search/fulltext            │
│  /api/stock/{code}/edit  /api/sync/*              │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────┴───────────────────────────┐
│                 数据加载层                         │
│  stocks_meta.json (Flask 优先)                     │
│  → stocks_master.json.gz (Docker)                  │
│  → GitHub Raw (Vercel 环境)                        │
│  → Supabase HTTP API                               │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────┴───────────────────────────┐
│                 核心数据库                         │
│  data/stocks/stocks_master.json (~8.5MB, 3525只)   │
│  data/stocks/stocks_meta.json (衍生, 简化版)        │
│  data/stocks/stocks_articles.json (文章拆分)        │
│  data/groups/groups.json (130个分组)               │
│  data/hot_topics/hot_topics.json (市场热点)         │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────┴───────────────────────────┐
│                 外部数据源                         │
│  腾讯财经 API (qt.gtimg.cn) → 实时行情             │
│  Supabase PostgreSQL → 云端数据库                  │
│  GitHub Raw → 最新数据源                           │
└──────────────────────────────────────────────────┘
```

### 2.2 技术栈

| 层 | 技术 |
|----|------|
| **后端** | Python 3.12, Flask, Jinja2 |
| **前端** | 原生 HTML/CSS/JS, Jinja2 模板, Tailwind CSS (部分页面) |
| **数据库** | JSON 文件 (本地), Supabase PostgreSQL (云端) |
| **行情** | 腾讯财经 HTTP API (`qt.gtimg.cn`) |
| **部署** | Vercel, ModelScope Studio, Railway, Docker |
| **版本控制** | Git + GitHub |

---

## 三、数据模型

### 3.1 个股数据结构

```json
{
  "688250": {
    "name": "盛科通信",
    "board": "SH",
    "industry": "电子-半导体-集成电路设计",
    "concepts": ["交换芯片", "国产芯片", "数据中心", "5G"],
    "products": ["以太网交换芯片", "白盒交换机"],
    "core_business": ["交换芯片研发与销售"],
    "industry_position": ["国产交换芯片龙头", "市占率国内第一"],
    "chain": ["中游-芯片设计"],
    "partners": ["阿里巴巴", "字节跳动"],
    "mention_count": 8,
    "last_updated": "2026-06-28",
    "valuation": {
      "target_market_cap": "500亿",
      "target_price": "48.5",
      "pe": "45",
      "upside": "30%",
      "rating": "买入"
    },
    "articles": [
      {
        "title": "交换芯片深度分析",
        "source": "https://mp.weixin.qq.com/s/xxx",
        "date": "2026-06-25",
        "type": "机构调研",
        "author": "某某证券",
        "industry_background": ["全球交换芯片市场...", "国产替代加速..."],
        "accidents": ["AI算力需求爆发", "国产替代政策"],
        "insights": ["核心竞争优势...", "增长驱动..."],
        "key_metrics": ["营收增速 45%", "毛利率 60%+"],
        "target_valuation": ["目标价 48.5元，对应 45x PE"]
      }
    ],
    "lyt_score": {
      "total": 68.5,
      "trend": 72,
      "volume": 65,
      "momentum": 70,
      "quality": 67,
      "risk": 69
    }
  }
}
```

### 3.2 核心字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 股票全称 |
| `code` | string | ✅ | 6位代码（唯一主键） |
| `board` | string | - | SH/SZ/BJ |
| `industry` | string | - | 行业分类 |
| `concepts` | string[] | - | 概念标签（set去重） |
| `mention_count` | int | ✅ | 文章提及次数 |
| `last_updated` | string | - | YYYY-MM-DD |
| `articles` | object[] | ✅ | 研究文章列表 |
| `valuation` | object | - | 机构估值 |

### 3.3 分组数据结构

```json
{
  "groups": [
    {
      "id": "group_1719000000_MLCC",
      "name": "MLCC",
      "description": "多层陶瓷电容器产业链",
      "color": "#3b82f6",
      "icon": "📊",
      "stocks": ["002859", "300408", "603678"],
      "created_at": "2026-06-27",
      "updated_at": "2026-06-28",
      "category": "元器件"
    }
  ]
}
```

### 3.4 热点数据结构

```json
{
  "topics": [
    {
      "id": "topic_1719000000",
      "name": "算电协同",
      "drivers": "AI算力+绿色电力一体化...",
      "stocks": [
        {"code": "002015", "name": "协鑫能科"},
        {"code": "300442", "name": "润泽科技"}
      ],
      "display": true,
      "created_at": "2026-06-27",
      "updated_at": "2026-06-27",
      "category": "AI算力链"
    }
  ]
}
```

---

## 四、实体抽取与数据流

### 4.1 完整数据管道

```
Step 0: 接收飞书消息 → 解析微信文章 URL
    ↓
Step 1: web_fetch 抓取文章正文
    ↓
Step 2: LLM 结构化提取个股数据
    ↓
Step 3: 查码确认（stocks_master.json + archived/全部个股.xls）
    ↓
Step 4: 写入 data/stocks/stocks_master_YYYY-MM-DD.json（分片）
    ↓
Step 5: merge_new_stocks.py 合并到 stocks_master.json
    ↓
Step 6: build_derivatives.py 生成衍生文件
    ↓
Step 7: git push → GitHub → 自动触发部署
```

### 4.2 文章处理流水线

| 步骤 | 工具 | 输出 |
|------|------|------|
| 获取文章 | web_fetch / 浏览器 | raw_material/YYYY-MM-DD.md |
| 结构化提取 | LLM + process_article.py | raw_material/output/YYYY-MM-DD.json |
| 查码映射 | stocks_master.json 查找 | 6位代码 |
| 合并写入 | merge_new_stocks.py | stocks_master.json（增量更新） |
| 去重规则 | 按 (source, title) 双键去重 | 已存在则跳过 |

### 4.3 离线研报处理

| 处理器 | 输入 | 输出 | 说明 |
|--------|------|------|------|
| `process_html_value.py` | HTML研报 | value_YYYY-MM-DD.json | 价值股分析 |
| `process_topdown.py` | HTML研报 | topdown JSON | 自上而下分析 |
| `extract_first_layer.py` | raw_material | products/core_business等 | 补齐第一层字段 |

### 4.4 数据合并流程

1. **主文件**: `data/stocks/stocks_master.json` — 唯一写入源
2. **分片文件**: `data/stocks_master_YYYY-MM-DD.json` — 每次AI提取的临时输出
3. **合并脚本**: 读取分片 → 去重合并 → 写回主文件 → 更新 GZ 压缩版
4. **衍生文件**: `stocks_meta.json`（Flask加载）、`stocks_articles.json`（按需加载）

---

## 五、工具定义与脚本清单

### 5.1 核心脚本

| 脚本 | 功能 | 输入 | 输出 |
|------|------|------|------|
| `main.py` | Flask Web 服务 + 全部 API | — | HTTP Response |
| `process_article.py` | 处理单篇微信文章 | raw_material/*.md | output/*.json |
| `process_groups.py` | 处理通达信/同花顺分组文件 | /tmp/stock_groups/*.txt | groups.json |
| `process_html_value.py` | 批量解析价值研报 | HTML文件 | value_YYYY-MM-DD.json |
| `process_topdown.py` | 批量解析自上而下研报 | HTML文件 | topdown JSON |
| `build_derivatives.py` | 从master构建衍生文件 | stocks_master.json | meta + articles + gz |
| `sync_to_supabase.py` | 同步到 Supabase | stocks_master.json | PostgreSQL |
| `sync_supabase_full.py` | 全量同步 Supabase | stocks_master.json | PostgreSQL |
| `rebuild_stocks.py` | 重建 stocks 数据库 | 多数据源 | stocks_master.json |
| `stock_processor.py` | 多终端股票处理 | — | 多终端数据 |
| `batch_process_value.py` | 批量处理价值股 | — | value JSON |
| `full_sync.py` | 全量同步（GitHub + Supabase） | — | — |

### 5.2 辅助工具

| 脚本/目录 | 功能 |
|-----------|------|
| `extract_first_layer.py` | 从 raw_material 补齐 products/core_business 等字段 |
| `scripts/merge_new_stocks.py` | 合并分片数据到 master |
| `scripts/extract_valuation.py` | 从 target_valuation 文本提取数值 |
| `sector_monitor/app.py` | Streamlit 板块资金监控（独立应用） |
| `breakt/` | lyt 老鸭头突破信号数据与展示 |

### 5.3 关键配置变量

```python
# main.py 核心配置
BASE_DIR = Path(__file__).parent  # 自动检测
STOCKS_MASTER = BASE_DIR / "data" / "stocks" / "stocks_master.json"
STOCKS_META = BASE_DIR / "data" / "stocks" / "stocks_meta.json"
STOCKS_ARTICLES = BASE_DIR / "data" / "stocks" / "stocks_articles.json"
GROUPS_FILE = BASE_DIR / "data" / "groups" / "groups.json"
HOT_TOPICS_FILE = BASE_DIR / "data" / "hot_topics" / "hot_topics.json"
```

---

## 六、数据源配置

### 6.1 实时行情 — 腾讯财经 API

```
接口: https://qt.gtimg.cn/q=sh600000,sz000333
编码: gb18030
分隔: ~ (波浪号)
频率: 每60秒刷新

字段映射:
  parts[2]  → 原始代码 (sh600000)
  parts[3]  → 最新价
  parts[32] → 涨跌幅(%)
  parts[39] → 市盈率(PE)
  parts[45] → 总市值(元) → 除以1e8得亿
```

**代码前缀规则:**
- `6xxxxx` → `sh` (上海)
- `0xxxxx` / `3xxxxx` → `sz` (深圳)
- `8xxxxx` / `4xxxxx` → `bj` (北京)

### 6.2 数据加载优先级

| 环境 | 优先级 | 说明 |
|------|--------|------|
| **本地 Flask** | stocks_meta.json → stocks_master.json.gz → stocks_master.json | 最快，Docker已打包 |
| **Vercel** | GitHub Raw → Supabase HTTP → 本地 | 需要外部数据源 |
| **回退** | GitHub Raw → Supabase → 本地文件 | 三级降级 |

### 6.3 Supabase 配置

```
环境变量:
  SUPABASE_URL       - Supabase 项目 URL
  SUPABASE_KEY       - Supabase anon/public key
  SUPABASE_SERVICE_ROLE_KEY - 服务角色密钥（写入操作）

表:
  stocks_data - 个股数据（JSONB格式）
```

### 6.4 GitHub 同步

```bash
# 自动提交模式
git add data/stocks/ data/groups/ data/hot_topics/
git commit -m "feat: update data - YYYY-MM-DD"
git push origin main

# GitHub Token（环境变量）
GITHUB_TOKEN - Personal Access Token（repo 权限）
```

---

## 七、API 接口文档

### 7.1 行情 API

| 端点 | 方法 | 参数 | 说明 |
|------|------|------|------|
| `/api/market-data` | GET | `codes=000333,603175` | 获取实时行情（腾讯API） |
| `/api/market-all` | GET | — | 获取全部A股行情 |

**响应示例:**
```json
{
  "000333": {
    "price": 78.55,
    "change": 2.68,
    "peRatio": 13.53,
    "marketCap": 5390.29
  },
  "totalCap": 5430.76
}
```

### 7.2 搜索 API

| 端点 | 方法 | 参数 | 说明 |
|------|------|------|------|
| `/api/search/suggest` | GET | `q=美的` | 股票名称搜索建议 |
| `/api/search/fulltext` | GET | `q=AI芯片&limit=20` | 全文搜索（名称/概念/文章） |

**全文搜索覆盖范围:**
- 股票级别: `name`, `industry`, `concepts`, `products`, `core_business`, `chain`, `partners`
- 文章级别: `title`, `accidents`, `insights`, `key_metrics`, `target_valuation`

### 7.3 股票管理 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/stock/{code}/edit` | POST | 编辑股票基本信息 |
| `/api/stock/{code}/article/edit` | POST | 编辑单篇文章 |
| `/api/stock/{code}/article/delete` | POST | 删除单篇文章 |
| `/api/stock/{code}/similar` | GET | 获取相似股票推荐 |

### 7.4 同步 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/sync/github` | POST | 同步数据到 GitHub |
| `/api/sync/all` | POST | 同步到 GitHub + Supabase |
| `/api/sync/firebase` | POST | 同步到 Firebase（已废弃） |
| `/api/sync/groups/firebase` | POST | 分组同步到 Firebase（已废弃） |
| `/api/sync/hot-topics/all` | POST | 同步热点数据 |

### 7.5 热点/分组 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/hot-topics` | GET | 获取热点列表 |
| `/api/hot-topics` | POST | 创建新热点 |
| `/api/hot-topic/{id}` | PUT | 编辑热点 |
| `/api/hot-topic/{id}` | DELETE | 删除热点 |
| `/api/hot-topic/{id}/display` | PUT | 切换热点显示状态 |
| `/api/groups` | GET | 获取分组列表 |
| `/api/group/{id}/sync` | POST | 同步单个分组 |

### 7.6 lyt 突破信号 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/lyt-signals` | GET | 获取每日突破信号 |
| `/api/lyt-scores` | GET | 获取五维评分 |
| `/api/lyt-groups` | GET | 获取分组 |
| `/api/lyt-changes` | GET | 获取涨跌幅 |

---

## 八、前端页面

### 8.1 页面清单

| 路由 | 模板 | 功能 |
|------|------|------|
| `/` | `dashboard.html` | 仪表板（分页20条，含行情/搜索/热点） |
| `/board` | `board.html` | **新看板**（分页40条，含行情/搜索/分组/概念） |
| `/stocks` | `stocks.html` | 股票列表（含行情） |
| `/stock/{code}` | `stock_detail.html` | 个股详情（行情/公司画像/文章/关联） |
| `/groups` | `groups.html` | 分组列表 |
| `/group/{id}` | `group_detail.html` | 分组详情 |
| `/concepts` | `concepts.html` | 概念大全 |
| `/concept/{name}` | `concept_detail.html` | 概念详情 |
| `/search` | `search.html` | 搜索页面（名称/代码） |
| `/search-page` | `search_page.html` | **新搜索**（全文搜索） |
| `/social-security-new` | `social_security_new.html` | 社保基金新进 |
| `/market` | `market.html` | 简易行情页 |
| `/lyt` | `lyt.html` | 老鸭头突破信号 |
| `/import` | `import_data.html` | 数据导入页面 |
| `/update` | `update_stocks.html` | 更新股票页面 |
| `/chart` | `chart.html` | 图表页面 |
| `/demo` | `demo_cards.html` | 卡片组件演示 |

### 8.2 看板页面特性 (board.html)

| 特性 | 实现方式 |
|------|---------|
| 分页 | 服务端分页，每页40条，`?page=N` |
| 行情 | 前端异步加载，每批200只，显示进度 |
| 搜索 | 前端即时过滤（代码/名称/概念） |
| 分组标签 | 彩色标签，最多3个 |
| 概念标签 | 蓝色标签，最多6个，+N折叠 |
| 涨跌颜色 | 红色涨(#ff0077)，绿色跌(#00ff88) |

### 8.3 组件库

| 文件 | 组件 |
|------|------|
| `components/stock_card.html` | 个股卡片（base/detail/compact/timeline四种模式） |
| `static/css/cyber-theme.css` | 赛博朋克主题样式 |
| `static/css/stock-card.css` | 个股卡片样式 |

---

## 九、部署配置

### 9.1 本地开发

```bash
cd f:/app_stockapril
python main.py
# → http://localhost:7860
```

### 9.2 Vercel

```
文件: api/index.py
框架: Flask → Vercel Serverless
构建: pip install -r requirements.txt
数据: 从 GitHub Raw 加载 stocks_master.json.gz
```

### 9.3 ModelScope Studio

```
GitHub 同步 → ModelScope 自动构建
地址: https://treeie-aastock.ms.show
```

### 9.4 Docker

```dockerfile
FROM python:3.12-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python build_derivatives.py  # 构建衍生文件
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "main:app"]
```

### 9.5 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `PORT` | - | 服务端口（默认7860） |
| `VERCEL` | - | Vercel 环境标识 |
| `SUPABASE_URL` | - | Supabase 项目 URL |
| `SUPABASE_KEY` | - | Supabase 匿名密钥 |
| `GITHUB_TOKEN` | - | GitHub Personal Access Token |
| `FLASK_DEBUG` | - | 调试模式（开发时使用） |

---

## 十、部署检查清单

### 10.1 数据完整性

- [ ] `data/stocks/stocks_master.json` 存在且可解析
- [ ] `stocks_master.json` 中 `stocks` 字段为 dict（key=代码）
- [ ] 每只股票包含 `name`, `mention_count`, `articles` 字段
- [ ] `mention_count == len(articles)` 同步一致
- [ ] `last_updated` 格式为 `YYYY-MM-DD`
- [ ] `data/groups/groups.json` 存在
- [ ] `data/hot_topics/hot_topics.json` 存在
- [ ] 分组中 `stocks` 为 6位代码数组
- [ ] 热点中 `stocks` 为 `[{code, name}]` 对象数组

### 10.2 衍生文件

- [ ] `data/stocks/stocks_meta.json` 与 master 同步
- [ ] `data/stocks/stocks_master.json.gz` 与 master 同步
- [ ] `data/stocks/stocks_articles.json` 与 master 同步

### 10.3 服务启动

- [ ] `python main.py` 启动无报错
- [ ] 日志显示加载的股票数量正确
- [ ] `http://localhost:7860/` 可访问
- [ ] `http://localhost:7860/board` 可访问且分页正确
- [ ] 搜索建议 API 正常 (`/api/search/suggest?q=美的`)
- [ ] 全文搜索 API 正常 (`/api/search/fulltext?q=芯片`)
- [ ] 行情 API 正常 (`/api/market-data?codes=000333`)

### 10.4 行情验证

- [ ] `/board` 页面行情异步加载成功
- [ ] `/stock/{code}` 详情页行情显示正常
- [ ] 涨跌颜色正确（红涨绿跌）
- [ ] 总市值单位显示"亿"

### 10.5 搜索验证

- [ ] 搜索框输入中文能正常触发建议
- [ ] 全文搜索能返回文章匹配结果
- [ ] 关键词高亮正确

### 10.6 同步与部署

- [ ] `git status` 确认所有变更已提交
- [ ] `git push origin main` 成功
- [ ] Vercel 自动部署成功（如有配置）
- [ ] ModelScope 自动构建成功（如有配置）
- [ ] Supabase 数据同步成功（如有配置）

### 10.7 已知限制

1. **Flask debug=False 不自动重载模板** — 修改模板后需手动重启
2. **行情 API 限流** — 腾讯财经 API 无官方文档，依赖稳定性
3. **数据合并需手动执行** — 分片文件不会自动合并到 master
4. **Vercel 冷启动慢** — Serverless 函数首次加载需从 GitHub Raw 拉取数据
5. **JSON 文件膨胀** — stocks_master.json 已达 8.5MB，需考虑分片存储
6. **articles 按需加载** — 仪表板不加载全部文章，个股详情页按需读取

### 10.8 维护建议

1. **每日检查**: `git log` 确认最新数据推送
2. **每周检查**: 数据完整性（mention_count 与 articles 长度一致）
3. **每月检查**: stocks_master.json 文件大小，超过 15MB 需分片
4. **按需执行**: 分片数据合并 → build_derivatives → git push
5. **备份策略**: GitHub 为主要备份，Supabase 为辅助备份

---

## 附录 A: 文件目录结构

```
f:/app_stockapril/
├── main.py                    # Flask 主应用 (3700+行)
├── AGENTS.md                  # AI 执行规范
├── requirements.txt           # Python 依赖
├── api/index.py               # Vercel 入口
├── build_derivatives.py       # 衍生文件构建
├── process_article.py         # 文章处理
├── process_groups.py          # 分组处理
├── sync_to_supabase.py        # Supabase 同步
├── data/
│   ├── stocks/
│   │   ├── stocks_master.json      # 核心数据库
│   │   ├── stocks_master.json.gz   # 压缩版
│   │   ├── stocks_meta.json        # 简化版（Flask加载）
│   │   └── stocks_articles.json    # 文章拆分
│   ├── groups/
│   │   └── groups.json             # 分组数据
│   ├── hot_topics/
│   │   └── hot_topics.json         # 热点数据
│   ├── master/                     # 母版数据
│   ├── reports/                    # 研报
│   └── zixuangu/                   # 自选股导出
├── templates/
│   ├── dashboard.html              # 仪表板
│   ├── board.html                  # 看板 (新)
│   ├── stock_detail.html           # 个股详情
│   ├── search.html                 # 搜索页
│   ├── search_page.html            # 全文搜索 (新)
│   ├── market.html                 # 行情页 (新)
│   ├── components/
│   │   └── stock_card.html         # 卡片组件
│   └── ...
├── static/
│   └── css/
│       ├── cyber-theme.css
│       └── stock-card.css
├── breakt/                         # 老鸭头突破信号
├── sector_monitor/                 # 板块资金监控
├── archived/                       # 归档
│   ├── 全部个股.xls
│   └── scripts/
├── scripts/                        # 工具脚本
└── raw_material/                   # 原始材料
```

---

> **文档维护**: 随项目迭代持续更新。重要变更请同步修改本文档。
