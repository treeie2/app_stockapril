---
name: wechat-fetch-research-embedded
description: |
  微信文章 → 结构化投研数据 完整流水线（v3.2）。
  适用场景：从 mp.weixin.qq.com 文章链接提取个股信息并沉淀到 JSON 数据库。
  云端龙虾环境通过飞书接收文章链接，自动执行全流程。
  核心能力：（1）抓取文章正文；（2）LLM 提取个股结构化数据；
  （3）合并到 stocks_master.json；（4）构建衍生文件；
  （5）同步 GitHub + Supabase。
---

# wechat-fetch-research-embedded (v3.2)

> 云端龙虾环境专用。通过飞书接收微信文章链接，自动化投研数据流水线。
> v3.2 新增：`build_derivatives.py` 强制步骤 — 解决「前端看不到新数据」根本原因

## 目录约定

```
项目根目录 (f:/app_stockapril)/
├── data/stocks/
│   ├── stocks_master.json           # 主数据库（唯一写入源）
│   ├── stocks_meta.json             # 轻量版（Flask 启动，2.8MB）
│   ├── stocks_articles.json         # 文章分离（按需加载）
│   ├── stocks_master.json.gz        # 压缩版
│   ├── stocks_index.json            # 全局索引
│   └── YYYY-MM-DD.json              # 日期分片
├── data/groups/
│   └── groups.json                  # 分组数据
├── data/hot_topics/
│   └── hot_topics.json              # 热门题材
├── breakt/
│   ├── lyt_daily_signals.json       # lyt 5207 条信号（老鸭头）
│   └── lyt_changes.json             # lyt 变动记录
├── .trae/skills/wechat-fetch-research-embedded/
│   ├── SKILL.md                     # 本文件
│   ├── config.json                  # LLM 配置
│   ├── raw_material/                # 原始文章
│   └── scripts/
│       ├── pipeline.py              # [核心] 全流程编排
│       ├── fetch_wechat_to_raw_material.py   # 正文落盘
│       ├── extract_stocks_from_raw_material.py  # LLM 提取
│       ├── merge_new_stocks.py      # 合并到主数据
│       ├── sync_to_github.py        # GitHub 同步
│       └── sync_to_supabase.py      # Supabase 同步
└── main.py                          # Flask 应用
```

---

## 执行流程（三阶段）

### 阶段 0：接收输入

**触发方式**：飞书消息发送微信文章链接

**输入格式**：
```
新增个股：https://mp.weixin.qq.com/s/xxx
```

**AI 动作**：
1. 使用 `web_fetch` 工具抓取文章正文
2. 确认文章标题、日期、来源 URL
3. 识别文中所有个股名称和代码

---

### 阶段 1：正文落盘（raw_material）

**目标**：将文章原文保存为结构化 Markdown

**执行**：
```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/fetch_wechat_to_raw_material.py \
  --url "https://mp.weixin.qq.com/s/xxx" \
  --out "raw_material/raw_material_2026-06-25.md" \
  --manual_text_file "tmp_article.txt"
```

**raw_material 格式**：
```markdown
# 文章标题
**来源**: https://mp.weixin.qq.com/s/xxx
**抓取日期**: 2026-06-25
**作者**: xxx

---

文章正文内容...
```

---

### 阶段 2：LLM 提取个股数据

**目标**：用 LLM 从 raw_material 提取结构化个股数据

**执行**：
```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/extract_stocks_from_raw_material.py \
  --raw "raw_material/raw_material_2026-06-25.md" \
  --stock_xls ".trae/skills/wechat-fetch-research-embedded/assets/全部个股.xls" \
  --out_json "data/stocks_master_2026-06-25.json" \
  --mode merge
```

**输出 JSON 格式**（`data/stocks_master_YYYY-MM-DD.json`）：
```json
{
  "date": "2026-06-25",
  "source": "https://mp.weixin.qq.com/s/xxx",
  "stocks": {
    "000333": {
      "name": "美的集团",
      "articles": [{
        "title": "文章标题",
        "date": "2026-06-25",
        "source": "https://mp.weixin.qq.com/s/xxx",
        "accidents": ["事件1", "事件2"],
        "insights": ["观点1"],
        "key_metrics": ["数字指标1"],
        "target_valuation": ["估值目标1"],
        "products": ["产品A"],
        "core_business": ["核心业务A"],
        "industry_position": ["行业地位A"],
        "chain": ["产业链位置"],
        "partners": ["合作伙伴"]
      }]
    }
  }
}
```

### 5 维度抽取标准

| 维度 | 字段 | 红线约束 |
|------|------|---------|
| 1 | `accidents` | 事实性描述，单项 ≤60字 |
| 2 | `insights` | 必须指向具体个股 |
| 3 | `key_metrics` | 每条必须包含阿拉伯数字 |
| 4 | `target_valuation` | 必须包含市值/PE/PB/目标价+数字 |
| 5 | 个股基本信息 | products/core_business/industry_position/chain/partners |

### 三道防线

| 防线 | 位置 | 作用 |
|------|------|------|
| 第一道 | Python `is_valid_stock_context()` | 标题/长度/信号词过滤 |
| 第二道 | LLM Prompt 三步判断 | `__THIN__` 标记行业背景型 |
| 第三道 | `clean_extracted_data()` | 后置字段非空检查 |

---

### 阶段 3：合并 + 构建衍生 + 同步

**目标**：将当日提取结果合并到主数据文件，构建衍生文件（Flask 实际加载），推送上线

#### Step 3A：合并主数据（关键步骤）

```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/merge_new_stocks.py
```

**自动完成**：
- 读取 `data/stocks_master_YYYY-MM-DD.json`
- 按 `(source, title)` 去重合并到 `data/stocks/stocks_master.json`
- 同步更新 `data/stocks/YYYY-MM-DD.json` 分片
- 累加 `mention_count`
- 更新 `updated_at` 时间戳

#### Step 3A-2：构建衍生文件 ⚠️ 必须执行

> **这是最容易遗漏的步骤，遗漏会导致前端看不到任何新数据！**

```bash
cd f:/app_stockapril && python build_derivatives.py
```

**为什么必须执行？** Flask 启动时实际加载的文件是：
- `data/stocks/stocks_meta.json`（优先）
- `data/stocks/stocks_master.json.gz`（Docker/Vercel 回退）

**不执行此步骤** → 前端永远显示旧数据，无论 master 是否已更新。

`build_derivatives.py` 生成：
1. `stocks_meta.json` — Flask 优先加载的轻量版（2.8MB）
2. `stocks_articles.json` — 文章拆分（按需加载）
3. `stocks_master.json.gz` — 压缩版（1.1MB, Docker/Vercel）

#### Step 3B：同步 GitHub

```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/sync_to_github.py \
  --mode full \
  --base-dir "data/stocks" \
  --json "data/stocks/stocks_master.json" \
  --github-token "${GITHUB_TOKEN}"
```

#### Step 3C：同步 Supabase

```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/sync_to_supabase.py \
  --date 2026-06-25
```

#### Step 3D：重启服务 + 验证（本地开发）

```bash
# 1. 停旧服务
taskkill /f /im python.exe

# 2. 重新启动
cd f:/app_stockapril && python main.py

# 3. 验证新数据可见
# 访问 http://localhost:7860/board 确认新股票出现
```

#### Step 3E：同步 ModelScope（可选）

```bash
cd /path/to/aastock
cp /path/to/data/stocks/stocks_master.json data/stocks/
git add -A && git commit -m "sync: 2026-06-25" && git push origin master
```

---

## 简化流程（AI 手动处理）

当 LLM 提取脚本不可用时，AI 可直接处理：

1. **抓取**：`web_fetch` → 获取全文
2. **查码**：从 `assets/全部个股.xls` 或 `data/stocks/stocks_master.json` 查询代码
3. **写入**：直接 Python 脚本追加 articles
4. **合并**：更新 mention_count + last_updated
5. **推送**：git commit + push

---

## 输入输出规范

| 输入 | 格式 | 示例 |
|------|------|------|
| 文章 URL | `mp.weixin.qq.com/s/xxx` | `https://mp.weixin.qq.com/s/abc` |

| 输出 | 位置 | 说明 |
|------|------|------|
| 原始文章 | `raw_material/raw_material_YYYY-MM-DD.md` | 结构化 Markdown |
| 当日提取 | `data/stocks_master_YYYY-MM-DD.json` | 中间产物 |
| 主数据 | `data/stocks/stocks_master.json` | 前端读取 |
| 日期分片 | `data/stocks/YYYY-MM-DD.json` | 增量记录 |
| GitHub | `treeie2/app_stockapril` main 分支 | 自动部署 Vercel |
| ModelScope | `TREEIE/aastock` master 分支 | 国内访问 |

---

## 脚本清单（仅核心）

| 脚本 | 职能 | 必需 |
|------|------|:--:|
| `scripts/fetch_wechat_to_raw_material.py` | 正文落盘 raw_material | ✅ |
| `scripts/extract_stocks_from_raw_material.py` | LLM 提取个股 | ✅ |
| `scripts/merge_new_stocks.py` | 合并到主数据 | ✅ |
| `scripts/sync_to_github.py` | 推送 GitHub | ✅ |
| `scripts/sync_to_supabase.py` | 同步 Supabase | ✅ |
| `scripts/pipeline.py` | 一键全流程 | ⭐ |
| `scripts/config.py` | LLM 配置管理 | ✅ |
| `scripts/map_industry_concept.py` | 行业概念映射 | 🔧 |
| `scripts/normalize_dates.py` | 日期修复 | 🔧 |

---

## 常见问题

### Q: 更新了文章但前端看不到新数据？

**根因**：遗漏了 `build_derivatives.py` 步骤。

Flask 加载的是 `stocks_meta.json`（优先）或 `stocks_master.json.gz`，而非 `stocks_master.json`。

**修复**：
```bash
cd f:/app_stockapril
python build_derivatives.py    # 从 master 重新生成 meta + gz
taskkill /f /im python.exe     # 停服务
python main.py                  # 重启
```

### Q: 如何验证数据已正确加载？

检查 Flask 启动日志：
```
✅ 加载 3525 只股票    ← 应匹配 master 中的 stock_count
📊 数据加载完成：3525 只股票
```

如果日志显示的数量与 `stocks_master.json` 不一致，说明衍生文件未更新。

### Q: 完整检查清单

每次更新文章后：
- [ ] `merge_new_stocks.py` 执行成功
- [ ] `build_derivatives.py` 执行成功 ⚠️ 最容易遗漏
- [ ] `git push` 已推送
- [ ] Flask 已重启（本地）/ Vercel 已自动部署
- [ ] 访问 `/board` 确认新股票可见
