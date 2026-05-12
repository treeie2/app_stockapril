# Firebase 同步与前端应用流程说明

**版本**: v1.1  
**更新日期**: 2026-05-12  
**适用**: 数据同步到 Firebase 及前端应用使用

---

## 🆕 v1.1 变更说明

### 新增：last_updated 字段

- **JSON 文件层级**: 添加 `last_updated` 字段（ISO 8601 格式）
- **股票层级**: 每只股票添加 `last_updated` 字段（YYYY-MM-DD 格式）
- **Firestore 同步**: 自动同步 `last_updated` 字段
- **用途**: 
  - 数据排序（降序排列，最新的在前）
  - 增量更新判断
  - 追踪数据更新时间

### 示例

**本地 JSON**:
```json
{
  "last_updated": "2026-05-12T16:00:00+08:00",
  "stocks": {
    "600330": {
      "name": "天通股份",
      "code": "600330",
      "last_updated": "2026-05-12",
      ...
    }
  }
}
```

**Firestore 文档**:
```json
stocks/600330: {
  name: "天通股份",
  code: "600330",
  last_updated: "2026-05-12",
  ...
}
```

---

## 📋 目录

1. [整体架构](#整体架构)
2. [数据同步流程](#数据同步流程)
3. [前端读取流程](#前端读取流程)
4. [数据结构映射](#数据结构映射)
5. [API 接口](#api-接口)
6. [常见问题](#常见问题)

---

## 🏗️ 整体架构

### 数据流向

```
微信公众号文章
    ↓
raw_material (Markdown)
    ↓
extract_stocks_from_raw_material.py (LLM 抽取)
    ↓
stocks_master.json (本地 JSON)
    ↓
    ├──→ sync_to_firestore.py → Firebase Firestore
    │                              ↓
    └──→ main.py (Flask) ←─────── 读取
           ↓
      Web 界面 (HTML/JS)
```

### 三层数据架构

```
┌─────────────────────────────────────────┐
│  本地数据层 (data/stocks/)              │
│  - stocks_master.json (完整数据)        │
│  - stocks_index.json (索引)             │
│  - stocks/YYYY-MM-DD.json (分片)        │
└─────────────────────────────────────────┘
           ↓ 同步
┌─────────────────────────────────────────┐
│  云端数据层 (Firebase Firestore)        │
│  - stocks/{code} (股票文档)             │
│  - stocks/{code}/articles/{id} (文章)   │
│  - config/hot_topics (热点配置)         │
│  - config/groups (分组配置)             │
└─────────────────────────────────────────┘
           ↓ 读取
┌─────────────────────────────────────────┐
│  应用层 (Flask + 前端)                  │
│  - /api/stocks (股票列表 API)           │
│  - /api/stock/{code} (个股详情 API)     │
│  - /api/hot-topics (热点 API)           │
│  - Web 界面 (HTML 渲染)                 │
└─────────────────────────────────────────┘
```

---

## 🔄 数据同步流程

### Step 1: 从 raw_material 提取数据

**脚本**: `extract_stocks_from_raw_material.py`

**功能**:
- 读取 raw_material markdown 文件
- 使用 LLM 识别股票并抽取结构化数据
- 抽取字段包括：
  - **article 层级**: accidents, insights, key_metrics, target_valuation
  - **股票层级**: products, core_business, industry, partners, chain

**命令**:
```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/extract_stocks_from_raw_material.py \
  --raw "raw_material/raw_material_2026-05-09.md" \
  --xls ".trae/skills/wechat-fetch-research-embedded/assets/全部个股.xls" \
  --out "data/stocks/2026-05-09.json"
```

**输出**:
```json
{
  "date": "2026-05-09",
  "stocks": {
    "688250": {
      "name": "盛科通信",
      "code": "688250",
      "industry": "电子 - 半导体 - 集成电路",
      "products": ["交换芯片"],
      "core_business": ["交换芯片研发与销售"],
      "chain": ["中游 - 芯片设计"],
      "partners": ["阿里巴巴", "字节跳动"],
      "articles": [
        {
          "title": "今天的一些信息整理 5.7",
          "accidents": ["二季度订单加速放量"],
          "insights": ["MRC 协议影响有限"],
          "key_metrics": ["2026 年国产 GPU 出货量预计 400 万颗"],
          "target_valuation": ["约 2700 亿市值"]
        }
      ]
    }
  }
}
```

### Step 2: 增量合并到主数据

**脚本**: `incremental_update.py`

**功能**:
- 将每日数据合并到 stocks_master.json
- 更新 stocks_index.json 索引
- 去重文章（按 source 去重）
- 合并股票层级字段（products, core_business 等）

**命令**:
```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/incremental_update.py \
  --json "data/stocks/2026-05-09.json" \
  --mode merge
```

### Step 3: 同步到 Firebase Firestore

**脚本**: `sync_to_firestore.py`

**功能**:
- 将 stocks_master.json 同步到 Firebase
- 创建/更新股票文档：`stocks/{code}`
- 创建/更新文章子文档：`stocks/{code}/articles/{article_id}`
- 支持三种冲突处理策略：skip / update / merge

**命令**:
```bash
python .trae/skills/wechat-fetch-research-embedded/scripts/sync_to_firestore.py \
  --credentials ".trae/rules/firebase-credentials.json" \
  --json "data/stocks/2026-05-09.json" \
  --collection "stocks" \
  --article_subcollection "articles" \
  --on_exists merge
```

**Firebase 数据结构**:

```
Firestore
└── stocks (collection)
    ├── 688250 (document)
    │   ├── name: "盛科通信"
    │   ├── code: "688250"
    │   ├── board: "SH"
    │   ├── industry: "电子 - 半导体 - 集成电路"
    │   ├── products: ["交换芯片"]
    │   ├── core_business: ["交换芯片研发与销售"]
    │   ├── chain: ["中游 - 芯片设计"]
    │   ├── partners: ["阿里巴巴", "字节跳动"]
    │   ├── concepts: ["交换芯片", "Scale-out"]
    │   ├── mention_count: 2
    │   ├── articles: [           # 文章摘要数组（用于快速列表）
    │   │     {
    │   │       "title": "今天的一些信息整理 5.7",
    │   │       "date": "2026-05-09",
    │   │       "source": "https://...",
    │   │       "accidents": [...],
    │   │       "insights": [...],
    │   │       "key_metrics": [...]
    │   │     }
    │   │   ]
    │   └── articles (subcollection)
    │       ├── <sha1_hash_1> (document)  # 完整文章数据
    │       │   ├── title: "今天的一些信息整理 5.7"
    │       │   ├── date: "2026-05-09"
    │       │   ├── source: "https://..."
    │       │   ├── accidents: [...]
    │       │   ├── insights: [...]
    │       │   ├── key_metrics: [...]
    │       │   └── target_valuation: [...]
    │       └── <sha1_hash_2> (document)
    │
    └── 300991 (document)
        └── ...
```

**同步逻辑**:

1. **股票文档**: 使用 `set(..., merge=True)` 只更新提供的字段
2. **文章子文档**: 
   - 按 `source` 的 SHA1 哈希作为文档 ID
   - 根据 `--on_exists` 参数处理冲突：
     - `skip`: 跳过已存在的文章
     - `update`: 覆盖更新
     - `merge`: 智能合并（保留原有字段，补充新字段）
3. **文章摘要数组**: 在股票文档中维护一个 `articles` 数组，用于快速列表展示

### Step 4: 同步热点和分组数据

**脚本**: `firebase_hot_topics.py`

**功能**:
- 同步热点主题到 `config/hot_topics`
- 同步分组数据到 `config/groups`

**命令**:
```bash
python firebase_hot_topics.py
```

---

## 📖 前端读取流程

### Flask 应用加载数据

**文件**: `main.py`

**加载顺序**:

1. **优先从本地 JSON 加载**
   ```python
   # 加载 stocks_master.json
   with open(STOCKS_MASTER_FILE, 'r', encoding='utf-8') as f:
       data = json.load(f)
       stocks = {s['code']: s for s in data.get('stocks', [])}
   ```

2. **从 Firebase 增量加载**（可选）
   ```python
   firebase_stocks, firebase_concepts = load_data_from_firebase()
   if firebase_stocks:
       stocks.update(firebase_stocks)
       concepts.update(firebase_concepts)
   ```

3. **加载热点和分组**
   ```python
   # 从 Firebase 加载热点
   fb_topics = load_from_firebase(include_hidden=False)
   
   # 从本地加载分组
   with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
       groups = json.load(f)
   ```

### Firebase REST API 读取

**函数**: `load_data_from_firebase()`

**实现**:
```python
def load_data_from_firebase():
    """从 Firebase 加载股票数据（支持分页）"""
    all_stocks = {}
    all_concepts = {}
    page_token = None
    
    while True:
        # Firestore REST API
        url = f"{FIREBASE_BASE_URL}/stocks"
        if page_token:
            url += f"?pageToken={page_token}"
        
        response = requests.get(url, timeout=30)
        data = response.json()
        documents = data.get('documents', [])
        
        for doc in documents:
            fields = doc.get('fields', {})
            code = fields.get('code', {}).get('stringValue', '')
            
            # 构建股票对象
            stock = {
                'name': fields.get('name', {}).get('stringValue', ''),
                'code': code,
                'industry': fields.get('industry', {}).get('stringValue', ''),
                'products': [...],  # 从 arrayValue 解析
                'articles': [...]   # 从 arrayValue 解析
            }
            
            all_stocks[code] = stock
        
        # 分页处理
        page_token = data.get('nextPageToken')
        if not page_token:
            break
    
    return all_stocks, all_concepts
```

### Web 界面渲染

**模板文件**:
- `templates/stocks.html` - 股票列表页
- `templates/stock_detail.html` - 个股详情页
- `templates/group_detail.html` - 分组详情页
- `templates/hot_topic_detail.html` - 热点详情页

**前端 JavaScript**:
```javascript
// 从 API 加载股票数据
fetch('/api/stocks')
  .then(res => res.json())
  .then(data => {
      // 渲染股票列表
      renderStockList(data.stocks);
  });

// 加载个股详情
fetch(`/api/stock/${code}`)
  .then(res => res.json())
  .then(stock => {
      // 显示股票信息
      displayStockInfo(stock);
      // 显示文章列表
      renderArticles(stock.articles);
  });
```

---

## 🔌 API 接口

### 股票相关 API

#### GET /api/stocks
获取所有股票列表

**响应**:
```json
{
  "stocks": [
    {
      "code": "688250",
      "name": "盛科通信",
      "industry": "电子 - 半导体 - 集成电路",
      "concepts": ["交换芯片"],
      "mention_count": 2
    }
  ],
  "total": 3157
}
```

#### GET /api/stock/<code>
获取个股详情

**响应**:
```json
{
  "code": "688250",
  "name": "盛科通信",
  "industry": "电子 - 半导体 - 集成电路",
  "products": ["交换芯片"],
  "core_business": ["交换芯片研发与销售"],
  "chain": ["中游 - 芯片设计"],
  "partners": ["阿里巴巴", "字节跳动"],
  "concepts": ["交换芯片", "Scale-out"],
  "valuation": {
    "target_market_cap": "2700 亿",
    "target_market_cap_billion": 2700.0
  },
  "articles": [
    {
      "title": "今天的一些信息整理 5.7",
      "date": "2026-05-09",
      "source": "https://...",
      "accidents": ["二季度订单加速放量"],
      "insights": ["MRC 协议影响有限"],
      "key_metrics": ["2026 年国产 GPU 出货量预计 400 万颗"],
      "target_valuation": ["约 2700 亿市值"]
    }
  ]
}
```

### 热点相关 API

#### GET /api/hot-topics
获取所有热点主题

**响应**:
```json
{
  "hot_topics": [
    {
      "id": "1",
      "name": "算电协同",
      "description": "算力与电力协同发展",
      "stocks": ["688250", "300991"],
      "created_at": "2026-05-01"
    }
  ]
}
```

#### GET /api/hot-topic/<id>
获取热点详情

### 分组相关 API

#### GET /api/groups
获取所有分组

#### GET /api/group/<id>
获取分组详情

---

## 📊 数据结构映射

### 本地 JSON → Firebase Firestore

| 本地 JSON 字段 | Firestore 字段 | 类型 | 说明 |
|---------------|---------------|------|------|
| `name` | `name` | string | 股票名称 |
| `code` | `code` | string | 股票代码 |
| `board` | `board` | string | 交易所（SH/SZ） |
| `industry` | `industry` | string | 所属行业 |
| `concepts` | `concepts` | array | 概念列表 |
| `products` | `products` | array | 产品服务 |
| `core_business` | `core_business` | array | 核心业务 |
| `chain` | `chain` | array | 产业链位置 |
| `partners` | `partners` | array | 合作伙伴 |
| `mention_count` | `mention_count` | integer | 文章数量 |
| `articles[]` | `articles[]` | array | 文章摘要（父文档） |
| `articles[]` | `articles/{id}` | subcollection | 文章详情（子文档） |

### 文章字段映射

| 字段 | 父文档 articles 数组 | 子文档 articles/{id} |
|------|---------------------|---------------------|
| `title` | ✅ | ✅ |
| `date` | ✅ | ✅ |
| `source` | ✅ | ✅ |
| `accidents` | ✅ | ✅ |
| `insights` | ✅ | ✅ |
| `key_metrics` | ✅ | ✅ |
| `target_valuation` | ❌ | ✅ |

**说明**:
- 父文档的 `articles` 数组用于快速列表展示（不包含 target_valuation）
- 子文档包含完整文章数据（包含 target_valuation）

---

## ❓ 常见问题

### Q1: Firebase 同步失败怎么办？

**A**: 
1. 检查凭证文件路径是否正确
2. 检查网络连接
3. 查看错误日志
4. 重试同步命令

### Q2: 前端如何知道数据已更新？

**A**: 
- 每次页面加载时，Flask 会重新从 Firebase 读取数据
- 可以通过浏览器开发者工具查看 Network 请求
- 检查 `/api/stocks` 返回的数据和时间戳

### Q3: 如何验证 Firebase 数据是否正确？

**A**: 
1. 访问 Firebase 控制台：https://console.firebase.google.com/
2. 进入 Firestore Database
3. 查看 `stocks` collection 中的文档
4. 对比本地 JSON 和 Firebase 数据

### Q4: 文章子文档的 ID 如何生成？

**A**: 
- 使用 `source` URL 的 SHA1 哈希值
- 确保同一篇文章只有一个文档
- 代码：`article_id = hashlib.sha1(source.encode()).hexdigest()`

### Q5: 如何回滚错误的同步？

**A**: 
1. 从 Git 恢复旧的 JSON 文件
2. 手动删除 Firebase 中的错误文档
3. 重新运行同步脚本

### Q6: 前端加载慢怎么办？

**A**: 
- Firebase 支持分页加载（每页 100 条）
- 使用 `pageToken` 参数分批加载
- 前端实现虚拟滚动，只渲染可见区域

---

## 🔧 调试技巧

### 检查 Firebase 数据

```bash
# 使用 Firebase CLI
firebase firestore:get /stocks/688250

# 或使用 REST API
curl "https://firestore.googleapis.com/v1/projects/webstock-724/databases/(default)/documents/stocks/688250"
```

### 查看同步日志

```bash
python sync_to_firestore.py \
  --credentials ".trae/rules/firebase-credentials.json" \
  --json "data/stocks/2026-05-09.json" \
  --on_exists merge \
  --dry_run  # 预览不实际写入
```

### 前端调试

```javascript
// 浏览器控制台
fetch('/api/stocks')
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 📝 完整示例

### 一键同步脚本

```bash
#!/bin/bash
# sync_all.sh - 一键同步所有数据到 Firebase

DATE=$(date +%Y-%m-%d)

echo "1. 提取个股数据..."
python .trae/skills/wechat-fetch-research-embedded/scripts/extract_stocks_from_raw_material.py \
  --raw "raw_material/raw_material_${DATE}.md" \
  --xls ".trae/skills/wechat-fetch-research-embedded/assets/全部个股.xls" \
  --out "data/stocks/${DATE}.json"

echo "2. 增量合并..."
python .trae/skills/wechat-fetch-research-embedded/scripts/incremental_update.py \
  --json "data/stocks/${DATE}.json" \
  --mode merge

echo "3. 同步到 Firebase..."
python .trae/skills/wechat-fetch-research-embedded/scripts/sync_to_firestore.py \
  --credentials ".trae/rules/firebase-credentials.json" \
  --json "data/stocks/${DATE}.json" \
  --on_exists merge

echo "4. 同步热点..."
python firebase_hot_topics.py

echo "✅ 完成！"
```

---

**文档维护**: 系统自动更新  
**最后更新**: 2026-05-12
