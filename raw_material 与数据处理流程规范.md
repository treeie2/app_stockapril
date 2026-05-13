# Raw Material 与数据处理流程规范

**版本**: v2.1  
**更新日期**: 2026-05-13  
**适用**: 微信文章→原始素材→结构化数据全流程

---

## 🆕 v2.1 变更说明

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
微信公众号文章
    ↓
[Step 1] 抓取/创建 raw_material
  - 方式A: fetch_wechat_to_raw_material.py（自动抓取）
  - 方式B: AI 手动整理文章内容
    ↓
raw_material/raw_material_YYYY-MM-DD_N.md
    ↓
[Step 2] 提取个股结构化数据
  - 方式A: extract_stocks_from_raw_material.py（LLM提取）
  - 方式B: AI 辅助提取（直接分析文章→构建JSON）
    ↓
data/stocks/YYYY-MM-DD.json（日期分片）
    ↓
[Step 3] 合并到主数据
  - 直接将日期分片合并到 data/stocks/stocks_master.json
  - 更新 mention_count、last_updated
    ↓
data/stocks/stocks_master.json（主数据）
    ↓
[Step 4] 同步到 Firebase
sync_stocks_to_firebase.py
    ↓
Firestore 数据库
    ↓
[Step 5] Web 界面展示（重启 Flask 生效）
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
  --out "data/stocks/2026-05-09.json"
```
*注意：该方式需要配置 LLM API Key，且可能因编码问题在 Windows 下运行失败*

**方式 B: AI 辅助提取（推荐）**

#### v2.1 优化流程：
1. AI 读取文章内容，识别提到的个股名称/代码
2. AI 提取每只股票的结构化数据（**仅需提取以下 4 个字段**）：
   - **accidents**（事件/催化剂）：事实性事件，单条≤60 字
   - **insights**（投研观点）：原文或忠实改写
   - **key_metrics**（关键指标）：数字、市占率等
   - **target_valuation**（目标估值）：估值、目标价
3. 调用 `process_article.py` 自动完成：
   - 从 `archived/同花顺行业.xls` 获取行业分类
   - 从 `archived/所属概念.xls` 获取概念标签
   - 从 `全部个股.xls` 获取股票名称
   - 构建完整的 JSON 格式
   - 合并到 `stocks_master.json`

**简化后的 AI 工作**：
- ❌ 不再需要：查找股票代码、行业、概念
- ✅ 只需：提取 4 个结构化字段（accidents/insights/key_metrics/target_valuation）

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

### Step 3: 合并到主数据

将日期分片的 stock 数据合并到 `stocks_master.json`：

```bash
# 方式A: 使用增量合并脚本（注意输出路径在 skill 目录下）
python .trae/skills/wechat-fetch-research-embedded/scripts/incremental_update.py \
  --json "data/stocks/2026-05-13.json" \
  --mode merge

# 方式B: 直接合并（推荐，避免路径问题）
cd project_root && python -c "
import json
with open('data/stocks/stocks_master.json') as f: master = json.load(f)
with open('data/stocks/2026-05-13.json') as f: daily = json.load(f)
for code, s in daily['stocks'].items():
    if code in master['stocks']:
        # 追加文章（去重）
        existing = master['stocks'][code]
        titles = [(a['title'], a['source']) for a in existing.get('articles',[])]
        for a in s.get('articles',[]):
            if (a['title'], a['source']) not in titles:
                existing.setdefault('articles',[]).append(a)
        existing['mention_count'] = len(existing['articles'])
        existing['last_updated'] = daily['date']
master['last_updated'] = daily['last_updated']
json.dump(master, open('data/stocks/stocks_master.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'OK: {len(daily[\"stocks\"])} stocks merged')
"
```

**验证（重要！）**：
```bash
# 检查 stocks_master.json 更新时间
ls -la data/stocks/stocks_master.json

# 验证某只股票的文章是否合并
python -c "import json; d=json.load(open('data/stocks/stocks_master.json','r',encoding='utf-8')); s=d['stocks']['688800']; print(s['name'], len(s['articles']), 'articles')"
```

### Step 4: 同步到 Firebase

```bash
python sync_stocks_to_firebase.py \
  --credentials ".trae/rules/firebase-credentials.json" \
  --json "data/stocks/stocks_master.json" \
  --on_exists merge
```

### Step 5: 刷新 Web 界面

合并后必须**重启 Flask 服务器**才能生效：

```bash
# 停止旧进程
Stop-Process -Name "python" -Force

# 重启
cd project_root
Start-Process -NoNewWindow python -ArgumentList "main.py"

# 打开浏览器验证
# http://127.0.0.1:7860/stock/688800
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

**输出路径**: `data/stocks/2026-05-09.json`

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
      "articles": [
        {
          "title": "今天的一些信息整理5.7",
          "date": "2026-05-09",
          "source": "https://mp.weixin.qq.com/s/jU3eFc1irDolyJyLd6egyg",
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
# 合并
python -c "
import json
m = json.load(open('data/stocks/stocks_master.json','r',encoding='utf-8'))
d = json.load(open('data/stocks/2026-05-09.json','r',encoding='utf-8'))
for c,s in d['stocks'].items():
    if c in m['stocks']:
        e = m['stocks'][c]
        known = [(a['title'],a['source']) for a in e.get('articles',[])]
        for a in s.get('articles',[]):
            if (a['title'],a['source']) not in known:
                e.setdefault('articles',[]).append(a)
        e['mention_count'] = len(e['articles'])
        e['last_updated'] = d['date']
m['last_updated'] = d['last_updated']
json.dump(m, open('data/stocks/stocks_master.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)
print('OK')
"

# 验证
python -c "import json; d=json.load(open('data/stocks/stocks_master.json','r',encoding='utf-8')); print('Total:', len(d['stocks']), 'stocks, last:', d.get('last_updated',''))"
```

#### 4. 同步到 Firebase

```bash
python sync_stocks_to_firebase.py \
  --credentials ".trae/rules/firebase-credentials.json" \
  --json "data/stocks/stocks_master.json" \
  --on_exists merge
```

#### 5. 重启服务器 + Git 提交

```bash
# 重启
Stop-Process -Name "python" -Force
Start-Process -NoNewWindow python -ArgumentList "main.py"

# 提交
git add raw_material/raw_material_2026-05-09.md
git add data/stocks/2026-05-09.json
git add data/stocks/stocks_master.json
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

### Q5: Firebase 同步失败怎么办？
**A**: 
1. 检查 Firebase 凭证文件是否正确
2. 检查网络连接
3. 查看错误日志
4. 可以跳过 Firebase 同步，先提交 Git

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
**最后更新**: 2026-05-13
